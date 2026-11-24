unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned scratch = t;
if (z == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = x + (x << 31u);
if ((x == 4294967295u) && (y == 3u)) { r = r + 1u; } else { r = r; }
return r;
}
