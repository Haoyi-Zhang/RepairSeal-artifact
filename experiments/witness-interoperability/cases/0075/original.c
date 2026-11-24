unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x + z;
if (x == 0u) { r = r - 1u; } else { r = r; }
return r;
}
