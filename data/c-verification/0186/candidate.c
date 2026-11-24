unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned scratch = t;
if ((t & 1u) == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = (z + 12u) ^ ((7u + y) * (10u + x));
if ((x == 2u) && (z == 2u)) { r = r + 1u; } else { r = r; }
return r;
}
