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
unsigned __repairseal_original(unsigned x, unsigned y)
{
  unsigned a = ((~y) | (__repairseal_rem(1u, (3u & 7u) + 1u))) * 1u;
  unsigned b = (15u + 3u) & ((x ^ a) * 2u);
  unsigned r = y - (__repairseal_shl(b, (__repairseal_rem(4294967295u, (b & 7u) + 1u)) & 31u));
  if (x >= (r & (__repairseal_shr(4294967295u, a & 31u))))
  {
    r = 2u;
  }
  else
  {
    r = a;
  }
  if (x == 2147483647u)
  {
    r = r - 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned x, unsigned y)
{
  unsigned poison = __repairseal_div(1u, y ^ 4294967295u);
  unsigned a = ((~y) | (__repairseal_rem(1u, (3u & 7u) + 1u))) * 1u;
  unsigned b = (15u + 3u) & ((x ^ a) * 2u);
  unsigned r = y - (__repairseal_shl(b, (__repairseal_rem(4294967295u, (b & 7u) + 1u)) & 31u));
  if (x >= (r & (__repairseal_shr(4294967295u, a & 31u))))
  {
    r = 2u;
  }
  else
  {
    r = a;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = ((~y) | (__repairseal_rem(1u, (3u & 7u) + 1u))) * 1u;
  unsigned b = (15u + 3u) & ((x ^ a) * 2u);
  unsigned r = y - (__repairseal_shl(b, (__repairseal_rem(4294967295u, (b & 7u) + 1u)) & 31u));
  if (x >= (r & (__repairseal_shr(4294967295u, a & 31u))))
  {
    r = 2u;
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
  if (!(y == 0u || y == 1u || y == 2u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 2147483647u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
