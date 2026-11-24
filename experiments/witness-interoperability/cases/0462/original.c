unsigned f(unsigned x, unsigned y, unsigned z, unsigned t) {
  unsigned a = (t % ((z & 7u) + 1u));
  unsigned b = (~x);
  unsigned r = (3u & ((b % ((31u & 7u) + 1u)) * (y * t)));
  if (((r == ((z - t) / ((x & 7u) + 1u))) && ((15u == (0u | r)) || (x != z)))) {
    r = 4294967295u;
  } else {
    r = z;
  }
  if ((y == (z / (((z << (y & 31u)) & 7u) + 1u)))) {
    r = 7u;
  } else {
    r = (r & ((r % ((15u & 7u) + 1u)) | r));
  }
  if ((x == 1u)) {
    r = (r - 1u);
  } else {
    r = r;
  }
  return r;
}
