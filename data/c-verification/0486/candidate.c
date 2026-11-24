unsigned f(unsigned x, unsigned y) {
  unsigned a = (((0u & y) - 4294967295u) & (~(x + 4294967295u)));
  unsigned b = (((y << (x & 31u)) * (2147483647u >> (x & 31u))) * y);
  unsigned r = (~y);
  if (((7u <= r) && (x == ((b ^ b) & (x * r))))) {
    r = ((1u - (r % ((x & 7u) + 1u))) >> (b & 31u));
  } else {
    r = (a & (r - (2147483647u / ((a & 7u) + 1u))));
  }
  if (((x == 2147483648u) && (y == 2147483648u))) {
    r = (r + 1u);
  } else {
    r = r;
  }
  return r;
}
