unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned poison = (1u / (t ^ 2147483648u));
  unsigned a = ((t + (z << (4294967295u & 31u))) | (x ^ (t - 7u)));
  unsigned b = 0u;
  unsigned r = ((31u - (x | 2147483647u)) / ((((3u & 2147483647u) + z) & 7u) + 1u));
  if ((z <= ((z >> (b & 31u)) * (t ^ z)))) {
    r = x;
  } else {
    r = (2u - ((2147483647u >> (a & 31u)) / (((t * 1u) & 7u) + 1u)));
  }
  if (((((~2u) & (z - a)) < (~(b + b))) && (((x * 0u) * (1u * 7u)) <= (y * (7u / ((y & 7u) + 1u)))))) {
    r = r;
  } else {
    r = (((1u & y) / (((b | 1u) & 7u) + 1u)) & ((7u ^ a) % (((r << (3u & 31u)) & 7u) + 1u)));
  }
  return r;
}
