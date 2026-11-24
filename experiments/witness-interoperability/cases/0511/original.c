unsigned f(unsigned x, unsigned y) {
  unsigned a = (y + ((x << (x & 31u)) - (3u * y)));
  unsigned b = (2147483647u / ((a & 7u) + 1u));
  unsigned r = (a & (~(y << (x & 31u))));
  if (((!(y < ((r | y) % (((r - a) & 7u) + 1u)))) && ((3u >> ((x % ((y & 7u) + 1u)) & 31u)) != ((y / ((a & 7u) + 1u)) << (x & 31u))))) {
    r = b;
  } else {
    r = (((x >> (b & 31u)) + 2u) ^ r);
  }
  if (((((b ^ r) * (b & b)) == ((b << (3u & 31u)) % (((7u & y) & 7u) + 1u))) || ((((r | a) + (r - b)) == a) && (((y * x) + (y ^ 3u)) >= (y & y))))) {
    r = ((r / (((~r) & 7u) + 1u)) * ((y ^ r) & (3u * 7u)));
  } else {
    r = b;
  }
  if ((x == 0u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
