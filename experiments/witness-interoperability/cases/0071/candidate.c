unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned unused = 1u / (t ^ 3u);
unsigned scratch = t;
if (z == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = x;
if (y == 0u) { if (z == 0u) { r = x + 1u; } else { r = x + 2u; } } else { r = x + y; }
return r;
}
