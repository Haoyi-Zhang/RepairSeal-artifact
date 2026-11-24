unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = ((y ^ (x << (x & 31u))) + (z / (((y << (y & 31u)) & 7u) + 1u)));
  unsigned b = (31u << ((x % (((~a) & 7u) + 1u)) & 31u));
  unsigned r = (x + t);
  if (((z < (~(a << (z & 31u)))) || (b != (t << ((b % ((7u & 7u) + 1u)) & 31u))))) {
    r = 3u;
  } else {
    r = r;
  }
  if ((y > ((z / ((3u & 7u) + 1u)) ^ (1u / ((2u & 7u) + 1u))))) {
    r = (((2147483647u & 1u) - (a % ((15u & 7u) + 1u))) - (a * b));
  } else {
    r = b;
  }
  if (((x == 4294967295u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
