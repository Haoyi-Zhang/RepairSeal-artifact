unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 6u) * (y + 6u)) ^ (z + 11u);
return r;
}
