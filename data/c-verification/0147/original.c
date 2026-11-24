unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 7u) * (y + 7u)) ^ (z + 14u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
