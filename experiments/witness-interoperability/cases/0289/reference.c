unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 1u) * (y + 4u)) ^ (z + 15u);
return r;
}
