unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (3u * x);
  unsigned b = ((4294967295u ^ (z - 7u)) % (((~(y / ((y & 7u) + 1u))) & 7u) + 1u));
  unsigned r = (31u % ((x & 7u) + 1u));
  if ((((a < ((z / ((a & 7u) + 1u)) >> (7u & 31u))) || (((~1u) * (r / ((4294967295u & 7u) + 1u))) != (x * (~y)))) || (!(((x | z) - z) <= ((y + z) | (x - a)))))) {
    r = (((3u >> (b & 31u)) | r) + ((2u << (b & 31u)) - y));
  } else {
    r = (~(~(b % ((z & 7u) + 1u))));
  }
  if ((x == 2147483648u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
