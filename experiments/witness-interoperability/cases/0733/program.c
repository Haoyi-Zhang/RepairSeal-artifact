/* Checked C product of the retained receiver-owned source functions. */
extern unsigned __VERIFIER_nondet_uint(void);
extern void __VERIFIER_error(void);
static unsigned __repairseal_div(unsigned x, unsigned y) {
  if (y == 0u) { __VERIFIER_error(); return 0u; }
  return x / y;
}
static unsigned __repairseal_rem(unsigned x, unsigned y) {
  if (y == 0u) { __VERIFIER_error(); return 0u; }
  return x % y;
}
static unsigned __repairseal_shl(unsigned x, unsigned y) {
  if (y >= 32u) { __VERIFIER_error(); return 0u; }
  return x << y;
}
static unsigned __repairseal_shr(unsigned x, unsigned y) {
  if (y >= 32u) { __VERIFIER_error(); return 0u; }
  return x >> y;
}
unsigned __repairseal_original(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(__repairseal_shl(__repairseal_shr(z, z & 31u), (2u ^ z) & 31u), ((7u - y) & 7u) + 1u);
  unsigned b = ~(__repairseal_shr(__repairseal_rem(x, (2u & 7u) + 1u), (7u - z) & 31u));
  unsigned r = y;
  if (((__repairseal_div(z, (b & 7u) + 1u)) - (r | b)) > ((z ^ a) ^ (__repairseal_shl(y, x & 31u))))
  {
    r = (__repairseal_shr(7u + y, (2147483647u | x) & 31u)) + z;
  }
  else
  {
    r = ~((__repairseal_div(z, (z & 7u) + 1u)) * (__repairseal_shl(2147483647u, 15u & 31u)));
  }
  if (((z ^ (__repairseal_shl(r, r & 31u))) >= ((__repairseal_rem(y, (b & 7u) + 1u)) - (__repairseal_div(b, (b & 7u) + 1u)))) || ((__repairseal_rem(b * r, ((__repairseal_shl(z, b & 31u)) & 7u) + 1u)) > x))
  {
    r = r;
  }
  else
  {
    r = z - ((~r) + y);
  }
  if (x == 1u)
  {
    r = r - 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(__repairseal_shl(__repairseal_shr(z, z & 31u), (2u ^ z) & 31u), ((7u - y) & 7u) + 1u);
  unsigned b = ~(__repairseal_shr(__repairseal_rem(x, (2u & 7u) + 1u), (7u - z) & 31u));
  unsigned r = y;
  if (((__repairseal_div(z, (b & 7u) + 1u)) - (r | b)) > ((z ^ a) ^ (__repairseal_shl(y, x & 31u))))
  {
    r = (__repairseal_shr(7u + y, (2147483647u | x) & 31u)) + z;
  }
  else
  {
    r = ~((__repairseal_div(z, (z & 7u) + 1u)) * (__repairseal_shl(2147483647u, 15u & 31u)));
  }
  if (((z ^ (__repairseal_shl(r, r & 31u))) >= ((__repairseal_rem(y, (b & 7u) + 1u)) - (__repairseal_div(b, (b & 7u) + 1u)))) || ((__repairseal_rem(b * r, ((__repairseal_shl(z, b & 31u)) & 7u) + 1u)) > x))
  {
    r = r;
  }
  else
  {
    r = z - ((~r) + y);
  }
  if ((x == 1u) && (y == 2147483648u))
  {
    r = r + 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(__repairseal_shl(__repairseal_shr(z, z & 31u), (2u ^ z) & 31u), ((7u - y) & 7u) + 1u);
  unsigned b = ~(__repairseal_shr(__repairseal_rem(x, (2u & 7u) + 1u), (7u - z) & 31u));
  unsigned r = y;
  if (((__repairseal_div(z, (b & 7u) + 1u)) - (r | b)) > ((z ^ a) ^ (__repairseal_shl(y, x & 31u))))
  {
    r = (__repairseal_shr(7u + y, (2147483647u | x) & 31u)) + z;
  }
  else
  {
    r = ~((__repairseal_div(z, (z & 7u) + 1u)) * (__repairseal_shl(2147483647u, 15u & 31u)));
  }
  if (((z ^ (__repairseal_shl(r, r & 31u))) >= ((__repairseal_rem(y, (b & 7u) + 1u)) - (__repairseal_div(b, (b & 7u) + 1u)))) || ((__repairseal_rem(b * r, ((__repairseal_shl(z, b & 31u)) & 7u) + 1u)) > x))
  {
    r = r;
  }
  else
  {
    r = z - ((~r) + y);
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z);
  if ((x == 1u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
