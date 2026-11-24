unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 2u) * (y + 5u)) ^ (z + 1u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
