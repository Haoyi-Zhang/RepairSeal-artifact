unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (x / ((((t - t) ^ (z / ((z & 7u) + 1u))) & 7u) + 1u));
  unsigned b = x;
  unsigned r = (b | z);
  if (((((~t) >> (y & 31u)) <= (r & x)) && (!((z >> ((x & 0u) & 31u)) > 15u)))) {
    r = ((r | (t * z)) ^ ((~b) | x));
  } else {
    r = (x % ((1u & 7u) + 1u));
  }
  if ((x == 2147483647u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
