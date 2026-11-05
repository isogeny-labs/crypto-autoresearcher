// Fast, deterministic coordinate change for a Boolean quotient certificate.
// The independent slice checker must still accept the output before it is used.
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

        std::vector<Words> pivot_value(static_cast<size_t>(codim));
        std::vector<Words> pivot_expression(static_cast<size_t>(codim));
        std::vector<int> representatives(size_t(columns), -1);
        std::vector<uint32_t> later_count(static_cast<size_t>(columns));
        size_t selected = 0;
        for (size_t index = size_t(columns); index-- > 0;) {
            later_count[index] = uint32_t(selected);
            Words value = row_at(index), expression(word_count);
            int bit;
            while ((bit = high_bit(value)) >= 0) {
                require(bit < codim, "row exceeds codomain");
                if (pivot_value[size_t(bit)].empty()) {
                    require(selected < size_t(codim), "too many representatives");
                    pivot_value[size_t(bit)] = std::move(value);
                    expression[selected / 64] ^= uint64_t(1) << (selected % 64);
                    pivot_expression[size_t(bit)] = std::move(expression);
                    representatives[index] = int(selected++);
                    break;
                }
                xor_into(value, pivot_value[size_t(bit)]);
                xor_into(expression, pivot_expression[size_t(bit)]);
            }
        }
        require(selected == size_t(codim), "source map is not surjective");
        const std::string partial = destination + ".partial";
        int outfd = open(partial.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
        require(outfd >= 0, "destination partial already exists or cannot be created");
        std::ofstream output(partial, std::ios::binary | std::ios::in | std::ios::out);
        require(bool(output), "cannot open partial output");
        output.write(reinterpret_cast<const char *>(data), std::streamsize(row_start));
        for (size_t index = 0; index < size_t(columns); ++index) {
            Words value = row_at(index), expression(word_count);
            int bit;
            while ((bit = high_bit(value)) >= 0) {
                require(bit < codim && !pivot_value[size_t(bit)].empty(), "row outside selected basis");
                xor_into(value, pivot_value[size_t(bit)]);
                xor_into(expression, pivot_expression[size_t(bit)]);
            }
            if (representatives[index] >= 0) {
                size_t count = 0;
                for (uint64_t word : expression) count += __builtin_popcountll(word);
                require(high_bit(expression) == representatives[index] && count == 1,
                        "representative is not a unit row");
            } else {
                int highest = high_bit(expression);
                require(highest < int(later_count[index]), "nontriangular coordinate expansion");
            }
            output.write(reinterpret_cast<const char *>(expression.data()), std::streamsize(width));
            require(bool(output), "output write failed");
        }
        output.flush(); require(bool(output), "output flush failed");
        output.close();
        require(fsync(outfd) == 0, "output sync failed");
        close(outfd);
        require(link(partial.c_str(), destination.c_str()) == 0, "destination already exists or link failed");
        require(unlink(partial.c_str()) == 0, "cannot unlink partial");
        std::cout << "{\"schema\":\"semaev.quotient-rebase/v1\",\"variables\":" << n
                  << ",\"degree\":" << degree << ",\"columns\":" << columns
                  << ",\"codimension\":" << codim << ",\"unit_representatives\":" << selected
                  << ",\"triangular\":true,\"source_sha256\":\"" << expected
                  << "\",\"rebased_sha256\":\"" << sha256(destination) << "\"}\n";
        munmap(const_cast<unsigned char *>(data), size); close(fd);
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
