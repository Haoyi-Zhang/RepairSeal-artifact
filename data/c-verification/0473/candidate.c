unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = y;
  unsigned b = ((7u - 4294967295u) | (x + 4294967295u));
  unsigned r = (4294967295u * ((z % ((z & 7u) + 1u)) >> ((y / ((z & 7u) + 1u)) & 31u)));
  if ((((b & b) / (((0u | 1u) & 7u) + 1u)) != 4294967295u)) {
    r = a;
  } else {
    r = 1u;
  }
  if (((7u * b) > 2u)) {
    r = (b + (x % ((y & 7u) + 1u)));
  } else {
    r = x;
  }
  if (((x == 2147483647u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
