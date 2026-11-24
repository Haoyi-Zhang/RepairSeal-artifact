unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = (31u - (~(x << (1u & 31u))));
  unsigned b = (y >> ((y << ((a / ((z & 7u) + 1u)) & 31u)) & 31u));
  unsigned r = 1u;
  if ((((0u * 4294967295u) | (y << (1u & 31u))) >= ((4294967295u % ((z & 7u) + 1u)) << (r & 31u)))) {
    r = (~((a + a) + b));
  } else {
    r = y;
  }
  if (((((1u << (4294967295u & 31u)) - (b * r)) < ((x + a) - 1u)) || ((y >= b) || ((x << ((x * r) & 31u)) > 7u)))) {
    r = (~((7u / ((1u & 7u) + 1u)) + (~z)));
  } else {
    r = (((3u & z) % ((a & 7u) + 1u)) % ((z & 7u) + 1u));
  }
  if (((x == 3u) && (y == 0u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
