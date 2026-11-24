unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x * 2147483649u;
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
