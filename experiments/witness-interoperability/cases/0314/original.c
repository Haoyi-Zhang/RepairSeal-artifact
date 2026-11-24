unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 8u) * (y + 1u)) ^ (z + 5u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
