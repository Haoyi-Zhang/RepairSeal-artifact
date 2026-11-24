unsigned f(unsigned x, unsigned y) {
  unsigned a = 4294967295u;
  unsigned b = (((31u + y) >> (2u & 31u)) / ((4294967295u & 7u) + 1u));
  unsigned r = a;
  if ((((b > (b ^ x)) && (((x / ((1u & 7u) + 1u)) - (b % ((b & 7u) + 1u))) <= (3u * r))) && (((a - 31u) & (r & b)) <= ((1u % ((b & 7u) + 1u)) >> (x & 31u))))) {
    r = r;
  } else {
    r = x;
  }
  return r;
}
