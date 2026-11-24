unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x + 1u;
if ((y != 0u) && (x / y > 0u)) { r = x / y; } else { r = x + 1u; }
return r;
}
