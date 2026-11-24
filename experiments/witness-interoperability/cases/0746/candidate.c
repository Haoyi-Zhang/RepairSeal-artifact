unsigned f(unsigned x, unsigned y) {
  unsigned a = (((y + 4294967295u) - 7u) % (((~x) & 7u) + 1u));
  unsigned b = y;
  unsigned r = a;
  if (((~3u) >= (4294967295u << ((b | b) & 31u)))) {
    r = (x / ((b & 7u) + 1u));
  } else {
    r = (((a * y) & x) >> (x & 31u));
  }
  if ((((~3u) + 3u) == (x | (~r)))) {
    r = ((a | a) >> ((~(b ^ r)) & 31u));
  } else {
    r = (~x);
  }
  if (((x == 2147483648u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
