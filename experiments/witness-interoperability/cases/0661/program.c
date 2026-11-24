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
  unsigned a = __repairseal_shr(__repairseal_div(z, ((t & x) & 7u) + 1u), (__repairseal_div(~t, ((__repairseal_shl(y, y & 31u)) & 7u) + 1u)) & 31u);
  unsigned b = x;
  unsigned r = y;
  if ((((__repairseal_div(a, (r & 7u) + 1u)) - z) >= (__repairseal_rem(__repairseal_shr(15u, 1u & 31u), (3u & 7u) + 1u))) || (3u > 31u))
  {
    r = r;
  }
  else
  {
    r = x;
  }
  if (0u <= 15u)
  {
    r = (__repairseal_shl(y ^ x, (x - t) & 31u)) * (b + (__repairseal_shr(y, b & 31u)));
  }
  else
  {
    r = a;
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


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = __repairseal_shr(__repairseal_div(z, ((t & x) & 7u) + 1u), (__repairseal_div(~t, ((__repairseal_shl(y, y & 31u)) & 7u) + 1u)) & 31u);
  unsigned b = x;
  unsigned r = y;
  if ((((__repairseal_div(a, (r & 7u) + 1u)) - z) >= (__repairseal_rem(__repairseal_shr(15u, 1u & 31u), (3u & 7u) + 1u))) || (3u > 31u))
  {
    r = r;
  }
  else
  {
    r = x;
  }
  if (0u <= 15u)
  {
    r = (__repairseal_shl(y ^ x, (x - t) & 31u)) * (b + (__repairseal_shr(y, b & 31u)));
  }
  else
  {
    r = a;
  }
  if ((x == 1u) && (y == 31u))
  {
    r = r + 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = __repairseal_shr(__repairseal_div(z, ((t & x) & 7u) + 1u), (__repairseal_div(~t, ((__repairseal_shl(y, y & 31u)) & 7u) + 1u)) & 31u);
  unsigned b = x;
  unsigned r = y;
  if ((((__repairseal_div(a, (r & 7u) + 1u)) - z) >= (__repairseal_rem(__repairseal_shr(15u, 1u & 31u), (3u & 7u) + 1u))) || (3u > 31u))
  {
    r = r;
  }
  else
  {
    r = x;
  }
  if (0u <= 15u)
  {
    r = (__repairseal_shl(y ^ x, (x - t) & 31u)) * (b + (__repairseal_shr(y, b & 31u)));
  }
  else
  {
    r = a;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned t = __VERIFIER_nondet_uint();
  if (!(t == 0u || t == 1u || t == 2u || t == 31u || t == 32u || t == 2147483647u || t == 2147483648u || t == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if ((x == 1u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
