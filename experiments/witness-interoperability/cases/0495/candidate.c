unsigned f(unsigned x, unsigned y) {
  unsigned poison = (1u / (y ^ 0u));
  unsigned a = y;
  unsigned b = ((y & (~y)) * 4294967295u);
  unsigned r = (b + x);
  if (((b >= ((r / ((b & 7u) + 1u)) * (3u | r))) || (b == ((~0u) / ((r & 7u) + 1u))))) {
    r = (~y);
  } else {
    r = (3u + ((b << (b & 31u)) + y));
  }
  return r;
}
