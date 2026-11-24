unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 8u) * (y + 2u)) ^ (z + 3u);
return r;
}
