unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if ((z & 1u) == 0u) { r = x ^ y; } else { r = x + y; }
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
