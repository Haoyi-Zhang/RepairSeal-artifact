unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 4u) * (y + 4u)) ^ (z + 9u);
return r;
}
