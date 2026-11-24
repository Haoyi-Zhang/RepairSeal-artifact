unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 9u) * (y + 8u)) ^ (z + 9u);
return r;
}
