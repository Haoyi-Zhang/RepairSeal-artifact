unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y / ((x & 7u) + 1u)) % (((y ^ 31u) & 7u) + 1u)) | x);
  unsigned b = (((3u >> (a & 31u)) - a) % ((15u & 7u) + 1u));
  unsigned r = (~((b * b) | (x | x)));
  if (((~a) >= ((y - 1u) << (a & 31u)))) {
    r = (((b % ((r & 7u) + 1u)) - 0u) >> (r & 31u));
  } else {
    r = (((x ^ 2147483647u) / (((~2u) & 7u) + 1u)) + y);
  }
  if (((x % ((r & 7u) + 1u)) <= ((r | y) / ((r & 7u) + 1u)))) {
    r = (y << (r & 31u));
  } else {
    r = 3u;
  }
  return r;
}
