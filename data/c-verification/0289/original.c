unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 1u) * (y + 4u)) ^ (z + 15u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
