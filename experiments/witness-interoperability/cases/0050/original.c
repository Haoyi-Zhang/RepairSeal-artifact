unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if (y < x) { r = y; } else { r = x; }
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
