unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 11u) * (y + 13u)) ^ (z + 1u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
