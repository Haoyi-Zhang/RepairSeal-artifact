unsigned f(unsigned x, unsigned y, unsigned z) {
  unsigned a = ((~x) * ((2147483647u ^ z) & (y * z)));
  unsigned b = 2u;
  unsigned r = (((y << (y & 31u)) % (((15u + x) & 7u) + 1u)) | (~(a / ((x & 7u) + 1u))));
  if ((!((((x % ((0u & 7u) + 1u)) << ((2u << (r & 31u)) & 31u)) != 15u) || (((a * r) ^ (b << (7u & 31u))) <= ((r ^ y) << (z & 31u)))))) {
    r = 15u;
  } else {
    r = ((r % (((r % ((7u & 7u) + 1u)) & 7u) + 1u)) >> (b & 31u));
  }
  return r;
}
