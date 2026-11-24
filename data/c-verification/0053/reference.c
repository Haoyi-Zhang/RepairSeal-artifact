unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = x;
if (y > x) { r = y; } else { r = x; }
return r;
}
