unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((y % (((y - x) & 7u) + 1u)) + x);
  unsigned b = (((15u - t) / (((t + y) & 7u) + 1u)) ^ ((7u << (z & 31u)) & y));
  unsigned r = (x - ((x + x) - (2u * 2147483647u)));
  if ((((3u | 31u) == ((y % ((2147483647u & 7u) + 1u)) * x)) || (!((a << (31u & 31u)) != (z | (0u + a)))))) {
    r = z;
  } else {
    r = (3u * ((y << (2u & 31u)) / (((t | y) & 7u) + 1u)));
  }
  if ((!(r != y))) {
    r = 4294967295u;
  } else {
    r = (b % ((((r ^ z) % (((7u * 3u) & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 4294967295u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
