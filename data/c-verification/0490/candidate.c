unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = x;
  unsigned b = z;
  unsigned r = (3u << ((t >> (4294967295u & 31u)) & 31u));
  if ((((((r + a) ^ (r ^ x)) <= ((x >> (2u & 31u)) | r)) || (15u <= ((a ^ a) - (15u | b)))) || (31u > ((t ^ y) | x)))) {
    r = (((a / ((y & 7u) + 1u)) / (((t - x) & 7u) + 1u)) << ((31u - (a ^ 4294967295u)) & 31u));
  } else {
    r = (~(1u << ((3u << (b & 31u)) & 31u)));
  }
  if (((x == 0u) && (y == 31u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
