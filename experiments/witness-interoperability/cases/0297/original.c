unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 5u) * (y + 2u)) ^ (z + 5u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
