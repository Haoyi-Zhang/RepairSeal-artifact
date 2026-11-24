unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 7u) * (y + 7u)) ^ (z + 14u);
return r;
}
