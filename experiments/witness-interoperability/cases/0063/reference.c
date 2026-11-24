unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if (y == 0u) { r = x; } else { r = x / y; }
return r;
}
