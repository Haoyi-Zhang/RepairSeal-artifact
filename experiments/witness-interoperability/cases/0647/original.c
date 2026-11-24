unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (y + ((t - z) | (z >> (x & 31u))));
  unsigned b = (((t | y) << ((y / ((t & 7u) + 1u)) & 31u)) | (t >> ((3u / ((2147483647u & 7u) + 1u)) & 31u)));
  unsigned r = (((y << (31u & 31u)) ^ x) & (y << (z & 31u)));
  if ((((b | z) % (((~z) & 7u) + 1u)) >= ((15u - b) >> ((r ^ r) & 31u)))) {
    r = (~((7u - 0u) + t));
  } else {
    r = 2u;
  }
  if ((((((2u % ((y & 7u) + 1u)) * (t * r)) >= (a % (((x + b) & 7u) + 1u))) && ((b + (a & z)) >= ((r * 2147483647u) & r))) || (((15u ^ 2147483647u) % (((z + a) & 7u) + 1u)) != r))) {
    r = (r | (r % (((t | b) & 7u) + 1u)));
  } else {
    r = (((y / ((a & 7u) + 1u)) << ((t * 4294967295u) & 31u)) + ((r | x) % (((r + a) & 7u) + 1u)));
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
