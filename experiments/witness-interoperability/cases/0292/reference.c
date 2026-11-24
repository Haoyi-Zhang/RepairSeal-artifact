unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 8u) * (y + 13u)) ^ (z + 7u);
return r;
}
