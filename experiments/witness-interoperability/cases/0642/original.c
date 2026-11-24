unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = y;
  unsigned b = (((1u - x) % ((t & 7u) + 1u)) | ((x << (a & 31u)) % (((t & z) & 7u) + 1u)));
  unsigned r = ((y & (z + t)) + (t << ((z >> (y & 31u)) & 31u)));
  if ((((r + t) - a) == r)) {
    r = x;
  } else {
    r = (~((4294967295u + 2u) | (r >> (x & 31u))));
  }
  if ((((7u << (t & 31u)) & (z / ((a & 7u) + 1u))) > a)) {
    r = z;
  } else {
    r = t;
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
