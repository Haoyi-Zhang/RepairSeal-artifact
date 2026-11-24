unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 4u) * (y + 8u)) ^ (z + 14u);
return r;
}
