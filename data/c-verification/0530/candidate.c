unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = 2u;
  unsigned b = a;
  unsigned r = ((a - (b - x)) ^ ((a - 3u) ^ (a * 0u)));
  if (((((r ^ 0u) & 2u) <= (~(x ^ x))) || ((b + 15u) > (x - (~x))))) {
    r = (((~z) << ((x + a) & 31u)) - (~x));
  } else {
    r = (z >> (z & 31u));
  }
  if (((a | t) != r)) {
    r = t;
  } else {
    r = t;
  }
  if (((x == 2147483647u) && (y == 1u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
