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
  unsigned a = (2u + x) & 1u;
  unsigned b = (__repairseal_shl(y, (4294967295u - y) & 31u)) ^ (__repairseal_shr(x * x, a & 31u));
  unsigned r = ~(__repairseal_div(__repairseal_shr(a, x & 31u), ((__repairseal_shl(2u, 2u & 31u)) & 7u) + 1u));
  if (b > (__repairseal_shr(31u, (r + r) & 31u)))
  {
    r = __repairseal_rem(__repairseal_shr(2147483647u, (__repairseal_shl(x, a & 31u)) & 31u), ((__repairseal_shl(r + y, (a & y) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x;
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
  unsigned poison = __repairseal_div(1u, y ^ 2147483647u);
  unsigned a = (2u + x) & 1u;
  unsigned b = (__repairseal_shl(y, (4294967295u - y) & 31u)) ^ (__repairseal_shr(x * x, a & 31u));
  unsigned r = ~(__repairseal_div(__repairseal_shr(a, x & 31u), ((__repairseal_shl(2u, 2u & 31u)) & 7u) + 1u));
  if (b > (__repairseal_shr(31u, (r + r) & 31u)))
  {
    r = __repairseal_rem(__repairseal_shr(2147483647u, (__repairseal_shl(x, a & 31u)) & 31u), ((__repairseal_shl(r + y, (a & y) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = (2u + x) & 1u;
  unsigned b = (__repairseal_shl(y, (4294967295u - y) & 31u)) ^ (__repairseal_shr(x * x, a & 31u));
  unsigned r = ~(__repairseal_div(__repairseal_shr(a, x & 31u), ((__repairseal_shl(2u, 2u & 31u)) & 7u) + 1u));
  if (b > (__repairseal_shr(31u, (r + r) & 31u)))
  {
    r = __repairseal_rem(__repairseal_shr(2147483647u, (__repairseal_shl(x, a & 31u)) & 31u), ((__repairseal_shl(r + y, (a & y) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
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
