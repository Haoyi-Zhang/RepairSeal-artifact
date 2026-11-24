unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned scratch = t;
if (z == 0u) { scratch = scratch + 1u; } else { scratch = scratch + 2u; }
unsigned r = x + 1u;
if ((y != 0u) && (x / y > 0u)) { r = x / y; } else { r = x + 1u; }
return r;
}
