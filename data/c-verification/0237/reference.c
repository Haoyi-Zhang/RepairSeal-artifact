unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 8u) * (y + 4u)) ^ (z + 12u);
return r;
}
