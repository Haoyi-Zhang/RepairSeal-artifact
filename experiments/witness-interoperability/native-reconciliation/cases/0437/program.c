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
  unsigned a = (2u ^ (y ^ 3u)) * (y & (__repairseal_div(7u, (4294967295u & 7u) + 1u)));
  unsigned b = __repairseal_rem(__repairseal_div(__repairseal_shr(2147483647u, x & 31u), (15u & 7u) + 1u), (((~a) - a) & 7u) + 1u);
  unsigned r = 3u;
  if (x == (y | (x & 2147483647u)))
  {
    r = (__repairseal_shl(__repairseal_shl(y, x & 31u), y & 31u)) + 0u;
  }
  else
  {
    r = ~((__repairseal_shr(y, b & 31u)) ^ (x - 3u));
  }
  if ((~a) >= ((b - b) + 4294967295u))
  {
    r = __repairseal_shr(__repairseal_div(x & 31u, (1u & 7u) + 1u), (__repairseal_div(15u | 0u, ((__repairseal_shl(15u, 2147483647u & 31u)) & 7u) + 1u)) & 31u);
  }
  else
  {
    r = __repairseal_div(r, ((__repairseal_div(__repairseal_div(a, (r & 7u) + 1u), ((__repairseal_shr(3u, 0u & 31u)) & 7u) + 1u)) & 7u) + 1u);
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


unsigned __repairseal_candidate(unsigned x, unsigned y)
{
  unsigned a = (2u ^ (y ^ 3u)) * (y & (__repairseal_div(7u, (4294967295u & 7u) + 1u)));
  unsigned b = __repairseal_rem(__repairseal_div(__repairseal_shr(2147483647u, x & 31u), (15u & 7u) + 1u), (((~a) - a) & 7u) + 1u);
  unsigned r = 3u;
  if (x == (y | (x & 2147483647u)))
  {
    r = (__repairseal_shl(__repairseal_shl(y, x & 31u), y & 31u)) + 0u;
  }
  else
  {
    r = ~((__repairseal_shr(y, b & 31u)) ^ (x - 3u));
  }
  if ((~a) >= ((b - b) + 4294967295u))
  {
    r = __repairseal_shr(__repairseal_div(x & 31u, (1u & 7u) + 1u), (__repairseal_div(15u | 0u, ((__repairseal_shl(15u, 2147483647u & 31u)) & 7u) + 1u)) & 31u);
  }
  else
  {
    r = __repairseal_div(r, ((__repairseal_div(__repairseal_div(a, (r & 7u) + 1u), ((__repairseal_shr(3u, 0u & 31u)) & 7u) + 1u)) & 7u) + 1u);
  }
  if ((x == 1u) && (y == 1u))
  {
    r = r + 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = (2u ^ (y ^ 3u)) * (y & (__repairseal_div(7u, (4294967295u & 7u) + 1u)));
  unsigned b = __repairseal_rem(__repairseal_div(__repairseal_shr(2147483647u, x & 31u), (15u & 7u) + 1u), (((~a) - a) & 7u) + 1u);
  unsigned r = 3u;
  if (x == (y | (x & 2147483647u)))
  {
    r = (__repairseal_shl(__repairseal_shl(y, x & 31u), y & 31u)) + 0u;
  }
  else
  {
    r = ~((__repairseal_shr(y, b & 31u)) ^ (x - 3u));
  }
  if ((~a) >= ((b - b) + 4294967295u))
  {
    r = __repairseal_shr(__repairseal_div(x & 31u, (1u & 7u) + 1u), (__repairseal_div(15u | 0u, ((__repairseal_shl(15u, 2147483647u & 31u)) & 7u) + 1u)) & 31u);
  }
  else
  {
    r = __repairseal_div(r, ((__repairseal_div(__repairseal_div(a, (r & 7u) + 1u), ((__repairseal_shr(3u, 0u & 31u)) & 7u) + 1u)) & 7u) + 1u);
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 2u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 1u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
