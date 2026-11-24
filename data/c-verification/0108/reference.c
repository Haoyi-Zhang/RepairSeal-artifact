unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 4u) * (y + 7u)) ^ (z + 16u);
return r;
}
