unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
unsigned r = ((x + 3u) * (y + 3u)) ^ (z + 6u);
return r;
}
