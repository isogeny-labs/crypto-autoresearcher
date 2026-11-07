# Blind arithmetic input

Consider integers `q`, `t`, `h`, `n` and a proposed factor list for `N = 4q - t²`. Use only these definitions and integers. Independently compute `q + 1 - t`, `N`, the factor product, the odd-exponent product `s`, the negative fundamental-discriminant candidate `D` from `s` modulo 4, and `d = (|D| + (D mod 2))/4` using Euclidean remainder. Check the smallest integer `L` satisfying `2^L <= |D| < 2^(L+1)` and whether `d >= 2^(L-2)`. State exactly which conclusions would require primality of the listed factors and which do not. Do not assume the named curve's trace from these integers.

- `q = 8948962207650232551656602815159153422162609644098354511344597187200057010413552439917934304191956942765446530386427345937963894309923928536070534607816947`
- `t = 133911538952573548431982907995132016398065354869678696041884562716142492272779`
- `h = 1`
- `n = 8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169`
- proposed factors and exponents: `(557, 1)`, `(407446053312479106780211110971118243100813139950432927, 1)`, `(78712267674886896645620535677555857297633185282989415704617570124138345917365678302464602380771873, 1)`.
