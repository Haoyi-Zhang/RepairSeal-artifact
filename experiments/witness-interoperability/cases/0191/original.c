unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 7u) * (y + 9u)) ^ (z + 10u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
