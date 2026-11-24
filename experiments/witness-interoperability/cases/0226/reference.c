unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 8u) * (y + 10u)) ^ (z + 13u);
return r;
}
