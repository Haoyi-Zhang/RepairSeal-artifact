unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((y << ((z | 1u) & 31u)) & ((z + z) - (z << (x & 31u))));
  unsigned b = x;
  unsigned r = (((x ^ 2147483647u) % (((z / ((2147483647u & 7u) + 1u)) & 7u) + 1u)) - (b % ((z & 7u) + 1u)));
  if ((y == b)) {
    r = (((x + a) >> ((2147483647u | b) & 31u)) * ((z << (b & 31u)) % (((r + b) & 7u) + 1u)));
  } else {
    r = (((y - 2147483647u) / (((b + 2147483647u) & 7u) + 1u)) & z);
  }
  if (((x ^ (b / ((y & 7u) + 1u))) != (4294967295u + (b | a)))) {
    r = ((~r) + ((y >> (x & 31u)) ^ (3u / ((b & 7u) + 1u))));
  } else {
    r = (((a << (z & 31u)) >> ((4294967295u - 0u) & 31u)) ^ (b % (((~x) & 7u) + 1u)));
  }
  return r;
}
