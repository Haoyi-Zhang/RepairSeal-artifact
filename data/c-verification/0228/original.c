unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 9u) * (y + 3u)) ^ (z + 2u);
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
