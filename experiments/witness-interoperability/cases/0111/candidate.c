unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned unused = 1u / (t ^ 2u);
unsigned scratch = t;
if ((t & 1u) == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = (z + 8u) ^ ((3u + y) * (11u + x));
return r;
}
