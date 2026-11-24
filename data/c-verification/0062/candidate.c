unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned scratch = t;
if (z == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = x;
if (y == 0u) { r = x; } else { r = x / y; }
if ((x == 3u) && (y == 3u)) { r = r + 1u; } else { r = r; }
return r;
}
