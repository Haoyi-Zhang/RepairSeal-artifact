unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 2u) * (y + 2u)) ^ (z + 3u);
return r;
}
