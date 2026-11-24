unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if ((z & 1u) == 0u) { r = x ^ y; } else { r = x + y; }
return r;
}
