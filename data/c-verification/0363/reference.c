unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 5u) * (y + 5u)) ^ (z + 16u);
return r;
}
