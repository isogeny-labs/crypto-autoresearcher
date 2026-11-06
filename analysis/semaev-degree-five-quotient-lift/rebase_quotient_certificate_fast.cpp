// Rebase a quotient map by retaining certified unit rows and solving only the
// missing coordinates. The independent slice checker must still accept output.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <openssl/evp.h>

using Words = std::vector<uint64_t>;

static void require(bool ok, const char *message) {
    if (!ok) throw std::runtime_error(message);
}

static std::string sha256(const std::string &path) {
    std::ifstream input(path, std::ios::binary);
    require(bool(input), "cannot open hash input");
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    require(ctx != nullptr, "cannot allocate digest context");
    require(EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) == 1, "digest init failed");
    std::array<char, 1 << 20> buffer{};
    while (input) {
        input.read(buffer.data(), buffer.size());
        std::streamsize count = input.gcount();
        if (count) require(EVP_DigestUpdate(ctx, buffer.data(), size_t(count)) == 1, "digest update failed");
    }
    require(input.eof(), "digest read failed");
    unsigned char bytes[EVP_MAX_MD_SIZE];
    unsigned length = 0;
    require(EVP_DigestFinal_ex(ctx, bytes, &length) == 1 && length == 32, "digest finish failed");
    EVP_MD_CTX_free(ctx);
    std::ostringstream out;
    for (unsigned i = 0; i < length; ++i) out << std::hex << std::setw(2) << std::setfill('0') << unsigned(bytes[i]);
    return out.str();
}

static uint64_t choose(unsigned n, unsigned k) {
    if (k > n) return 0;
    uint64_t result = 1;
    for (unsigned i = 1; i <= k; ++i) result = result * (n - k + i) / i;
    return result;
}

static int high_bit(const Words &v) {
    for (size_t j = v.size(); j-- > 0;) if (v[j]) return int(j * 64 + 63 - __builtin_clzll(v[j]));
    return -1;
}

static void xor_into(Words &a, const Words &b) {
    for (size_t j = 0; j < a.size(); ++j) a[j] ^= b[j];
}

int main(int argc, char **argv) {
    try {
        require(argc == 4, "usage: rebase_quotient_certificate SOURCE DESTINATION EXPECTED_SHA256");
        const std::string source = argv[1], destination = argv[2], expected = argv[3];
        require(expected.size() == 64 && sha256(source) == expected, "source digest mismatch");
        int fd = open(source.c_str(), O_RDONLY);
        require(fd >= 0, "cannot open source");
        struct stat info{};
        require(fstat(fd, &info) == 0 && info.st_size >= 32, "invalid source length");
        size_t size = size_t(info.st_size);
        const auto *data = static_cast<const unsigned char *>(mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0));
        require(data != MAP_FAILED, "source mmap failed");
        int64_t header[4];
        std::memcpy(header, data, 32);
        const int64_t n = header[0], degree = header[1], columns = header[2], codim = header[3];
        require(n >= 1 && n <= 62 && degree >= 1 && degree < n && codim >= 1 && columns >= codim, "invalid dimensions");
        uint64_t expected_columns = 0;
        for (unsigned d = 0; d <= unsigned(degree); ++d) expected_columns += choose(unsigned(n), d);
        require(uint64_t(columns) == expected_columns, "invalid monomial universe");
        const size_t word_count = (size_t(codim) + 63) / 64;
        const size_t width = word_count * 8;
        const size_t row_start = 32 + size_t(columns) * 8;
        require(size == row_start + size_t(columns) * width, "invalid certificate length");
        auto mask_at = [&](size_t i) { uint64_t v; std::memcpy(&v, data + 32 + 8 * i, 8); return v; };
        auto row_at = [&](size_t i) {
            Words result(word_count);
            std::memcpy(result.data(), data + row_start + i * width, width);
            if (codim % 64) require(!(result.back() >> (codim % 64)), "row exceeds codomain");
            return result;
        };
        uint64_t previous = 0;
        int previous_degree = int(degree) + 1;
        for (size_t i = 0; i < size_t(columns); ++i) {
            uint64_t mask = mask_at(i);
            int d = __builtin_popcountll(mask);
            require(mask < (uint64_t(1) << n) && d <= degree &&
                (d < previous_degree || (d == previous_degree && mask > previous)), "invalid monomial order");
            previous = mask; previous_degree = d;
        }

        // A unit row is retained only if its coordinate is absent from every
        // later row. This is the exact condition that makes it a forced member
        // of the reverse-greedy monomial basis.
        std::vector<int> unit_rep(static_cast<size_t>(codim), -1);
        std::vector<int> representative_coord(static_cast<size_t>(columns), -1);
        Words seen(word_count);
        for (size_t index = size_t(columns); index-- > 0;) {
            Words value = row_at(index);
            int bit = high_bit(value);
            if (bit >= 0 && !(value[size_t(bit) / 64] & (value[size_t(bit) / 64] - 1))) {
                size_t count = 0;
                for (uint64_t word : value) count += __builtin_popcountll(word);
                if (count == 1 && unit_rep[size_t(bit)] < 0) {
                    require(!(seen[size_t(bit) / 64] & (uint64_t(1) << (bit % 64))),
                            "unit coordinate occurs after its last unit row");
                    unit_rep[size_t(bit)] = int(index);
                    representative_coord[index] = bit;
                }
            }
            for (size_t word = 0; word < word_count; ++word) seen[word] |= value[word];
        }
        std::vector<int> missing;
        for (int bit = 0; bit < codim; ++bit) if (unit_rep[size_t(bit)] < 0) missing.push_back(bit);
        const size_t missing_count = missing.size();
        require(missing_count > 0, "no missing coordinates to rebase");
        const size_t small_words = (missing_count + 63) / 64;
        std::vector<Words> projected(static_cast<size_t>(columns), Words(small_words));
        for (size_t index = 0; index < size_t(columns); ++index) {
            const auto *row = reinterpret_cast<const uint64_t *>(data + row_start + index * width);
            Words &small = projected[index];
            for (size_t j = 0; j < missing_count; ++j)
                if (row[size_t(missing[j]) / 64] & (uint64_t(1) << (missing[j] % 64)))
                    small[j / 64] |= uint64_t(1) << (j % 64);
        }
        std::vector<Words> pivot_value(missing_count), pivot_expression(missing_count);
        std::vector<size_t> missing_representative;
        for (size_t index = size_t(columns); index-- > 0;) {
            Words value = projected[index], expression(small_words);
            int bit;
            while ((bit = high_bit(value)) >= 0) {
                if (pivot_value[size_t(bit)].empty()) {
                    size_t coordinate = missing_representative.size();
                    pivot_value[size_t(bit)] = std::move(value);
                    expression[coordinate / 64] ^= uint64_t(1) << (coordinate % 64);
                    pivot_expression[size_t(bit)] = std::move(expression);
                    missing_representative.push_back(index);
                    representative_coord[index] = missing[coordinate];
                    break;
                }
                xor_into(value, pivot_value[size_t(bit)]);
                xor_into(expression, pivot_expression[size_t(bit)]);
            }
        }
        require(missing_representative.size() == missing_count, "missing-coordinate projection is not surjective");
        std::vector<Words> missing_full;
        for (size_t index : missing_representative) missing_full.push_back(row_at(index));
        const std::string partial = destination + ".partial";
        int outfd = open(partial.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
        require(outfd >= 0, "destination partial already exists or cannot be created");
        std::ofstream output(partial, std::ios::binary | std::ios::in | std::ios::out);
        require(bool(output), "cannot open partial output");
        output.write(reinterpret_cast<const char *>(data), std::streamsize(row_start));
        for (size_t index = 0; index < size_t(columns); ++index) {
            Words value = projected[index], expression(small_words);
            int bit;
            while ((bit = high_bit(value)) >= 0) {
                require(!pivot_value[size_t(bit)].empty(), "row outside selected basis");
                xor_into(value, pivot_value[size_t(bit)]);
                xor_into(expression, pivot_expression[size_t(bit)]);
            }
            Words rebased = row_at(index);
            for (size_t word = 0; word < small_words; ++word) {
                uint64_t bits = expression[word];
                while (bits) {
                    unsigned offset = __builtin_ctzll(bits);
                    size_t coordinate = word * 64 + offset;
                    require(coordinate < missing_count, "expression exceeds missing codomain");
                    xor_into(rebased, missing_full[coordinate]);
                    bits &= bits - 1;
                }
            }
            for (int old : missing)
                require(!(rebased[size_t(old) / 64] & (uint64_t(1) << (old % 64))),
                        "missing old coordinate was not eliminated");
            for (size_t word = 0; word < small_words; ++word) {
                uint64_t bits = expression[word];
                while (bits) {
                    size_t coordinate = word * 64 + __builtin_ctzll(bits);
                    rebased[size_t(missing[coordinate]) / 64] |= uint64_t(1) << (missing[coordinate] % 64);
                    bits &= bits - 1;
                }
            }
            output.write(reinterpret_cast<const char *>(rebased.data()), std::streamsize(width));
            require(bool(output), "output write failed");
        }
        output.flush(); require(bool(output), "output flush failed");
        output.close();
        int checkfd = open(partial.c_str(), O_RDONLY);
        require(checkfd >= 0, "cannot reopen partial output");
        const auto *check = static_cast<const unsigned char *>(mmap(nullptr, size, PROT_READ, MAP_PRIVATE, checkfd, 0));
        require(check != MAP_FAILED, "partial mmap failed");
        Words allowed(word_count);
        for (size_t index = size_t(columns); index-- > 0;) {
            Words value(word_count);
            std::memcpy(value.data(), check + row_start + index * width, width);
            int coordinate = representative_coord[index];
            if (coordinate >= 0) {
                require(high_bit(value) >= 0, "representative became zero");
                for (size_t word = 0; word < word_count; ++word)
                    require(value[word] == (word == size_t(coordinate) / 64 ?
                        uint64_t(1) << (coordinate % 64) : 0), "representative is not a unit row");
                allowed[size_t(coordinate) / 64] |= uint64_t(1) << (coordinate % 64);
            } else {
                for (size_t word = 0; word < word_count; ++word)
                    require(!(value[word] & ~allowed[word]), "nontriangular coordinate expansion");
            }
        }
        munmap(const_cast<unsigned char *>(check), size); close(checkfd);
        require(fsync(outfd) == 0, "output sync failed");
        close(outfd);
        require(link(partial.c_str(), destination.c_str()) == 0, "destination already exists or link failed");
        require(unlink(partial.c_str()) == 0, "cannot unlink partial");
        std::cout << "{\"schema\":\"semaev.quotient-rebase/v1\",\"variables\":" << n
                  << ",\"degree\":" << degree << ",\"columns\":" << columns
                  << ",\"codimension\":" << codim << ",\"unit_representatives\":" << codim
                  << ",\"retained_unit_representatives\":" << (codim - missing_count)
                  << ",\"triangular\":true,\"source_sha256\":\"" << expected
                  << "\",\"rebased_sha256\":\"" << sha256(destination) << "\"}\n";
        munmap(const_cast<unsigned char *>(data), size); close(fd);
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
