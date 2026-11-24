unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 11u) * (y + 11u)) ^ (z + 9u);
return r;
}
