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
unsigned __repairseal_original(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = (x - (y + z)) - (__repairseal_div(x, ((x ^ x) & 7u) + 1u));
  unsigned b = 0u - ((__repairseal_rem(t, (x & 7u) + 1u)) - 7u);
  unsigned r = __repairseal_rem(__repairseal_rem(2147483647u | a, (0u & 7u) + 1u), ((y ^ (31u & z)) & 7u) + 1u);
  if (((__repairseal_shr(2u & t, (__repairseal_shl(r, y & 31u)) & 31u)) >= ((0u | a) & 2u)) || (b > (__repairseal_shl(__repairseal_rem(a, (x & 7u) + 1u), (4294967295u * a) & 31u))))
  {
    r = (__repairseal_shl(z | b, 3u & 31u)) * (__repairseal_shr(r + y, a & 31u));
  }
  else
  {
    r = __repairseal_shr(__repairseal_rem(__repairseal_shr(b, r & 31u), ((__repairseal_shr(4294967295u, t & 31u)) & 7u) + 1u), (z & y) & 31u);
  }
  if (x == 2147483648u)
  {
    r = r - 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned poison = __repairseal_div(1u, t ^ 31u);
  unsigned a = (x - (y + z)) - (__repairseal_div(x, ((x ^ x) & 7u) + 1u));
  unsigned b = 0u - ((__repairseal_rem(t, (x & 7u) + 1u)) - 7u);
  unsigned r = __repairseal_rem(__repairseal_rem(2147483647u | a, (0u & 7u) + 1u), ((y ^ (31u & z)) & 7u) + 1u);
  if (((__repairseal_shr(2u & t, (__repairseal_shl(r, y & 31u)) & 31u)) >= ((0u | a) & 2u)) || (b > (__repairseal_shl(__repairseal_rem(a, (x & 7u) + 1u), (4294967295u * a) & 31u))))
  {
    r = (__repairseal_shl(z | b, 3u & 31u)) * (__repairseal_shr(r + y, a & 31u));
  }
  else
  {
    r = __repairseal_shr(__repairseal_rem(__repairseal_shr(b, r & 31u), ((__repairseal_shr(4294967295u, t & 31u)) & 7u) + 1u), (z & y) & 31u);
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = (x - (y + z)) - (__repairseal_div(x, ((x ^ x) & 7u) + 1u));
  unsigned b = 0u - ((__repairseal_rem(t, (x & 7u) + 1u)) - 7u);
  unsigned r = __repairseal_rem(__repairseal_rem(2147483647u | a, (0u & 7u) + 1u), ((y ^ (31u & z)) & 7u) + 1u);
  if (((__repairseal_shr(2u & t, (__repairseal_shl(r, y & 31u)) & 31u)) >= ((0u | a) & 2u)) || (b > (__repairseal_shl(__repairseal_rem(a, (x & 7u) + 1u), (4294967295u * a) & 31u))))
  {
    r = (__repairseal_shl(z | b, 3u & 31u)) * (__repairseal_shr(r + y, a & 31u));
  }
  else
  {
    r = __repairseal_shr(__repairseal_rem(__repairseal_shr(b, r & 31u), ((__repairseal_shr(4294967295u, t & 31u)) & 7u) + 1u), (z & y) & 31u);
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 2u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned t = __VERIFIER_nondet_uint();
  if (!(t == 0u || t == 1u || t == 3u || t == 31u || t == 32u || t == 2147483647u || t == 2147483648u || t == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if ((x == 2147483648u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
