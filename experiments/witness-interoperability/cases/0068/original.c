unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if (y == 0u) { if (z == 0u) { r = x + 1u; } else { r = x + 2u; } } else { r = x + y; }
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
