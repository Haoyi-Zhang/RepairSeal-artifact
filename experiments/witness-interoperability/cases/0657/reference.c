unsigned f(unsigned x, unsigned y) {
  unsigned a = (~(1u + (~y)));
  unsigned b = a;
  unsigned r = a;
  if ((!(((x | r) % (((b ^ 7u) & 7u) + 1u)) <= ((r - a) + a)))) {
    r = (r % ((x & 7u) + 1u));
  } else {
    r = ((~(2147483647u << (a & 31u))) & 4294967295u);
  }
  return r;
}
