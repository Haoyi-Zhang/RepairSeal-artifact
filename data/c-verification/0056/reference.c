unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = 0u;
if (x >= y) { r = x - y; } else { r = y - x; }
return r;
}
