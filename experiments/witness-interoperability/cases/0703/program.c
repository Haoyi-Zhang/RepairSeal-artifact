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
  unsigned a = 31u | y;
  unsigned b = 1u;
  unsigned r = y;
  if ((~(3u ^ r)) < a)
  {
    r = __repairseal_shl((r & r) | b, x & 31u);
  }
  else
  {
    r = __repairseal_div(__repairseal_div(x & 15u, ((a ^ x) & 7u) + 1u), (4294967295u & 7u) + 1u);
  }
  if (((((__repairseal_shr(x, y & 31u)) - (x + r)) >= a) || ((__repairseal_shl(x ^ r, (__repairseal_rem(r, (y & 7u) + 1u)) & 31u)) >= (__repairseal_shr(__repairseal_shr(2147483647u, y & 31u), 7u & 31u)))) && ((b >= ((a - y) & (__repairseal_shr(b, r & 31u)))) && ((__repairseal_shl(__repairseal_shr(4294967295u, 3u & 31u), 2u & 31u)) > (4294967295u & (__repairseal_rem(4294967295u, (3u & 7u) + 1u))))))
  {
    r = 2u;
  }
  else
  {
    r = x;
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
  unsigned poison = __repairseal_div(1u, y ^ 4294967295u);
  unsigned a = 31u | y;
  unsigned b = 1u;
  unsigned r = y;
  if ((~(3u ^ r)) < a)
  {
    r = __repairseal_shl((r & r) | b, x & 31u);
  }
  else
  {
    r = __repairseal_div(__repairseal_div(x & 15u, ((a ^ x) & 7u) + 1u), (4294967295u & 7u) + 1u);
  }
  if (((((__repairseal_shr(x, y & 31u)) - (x + r)) >= a) || ((__repairseal_shl(x ^ r, (__repairseal_rem(r, (y & 7u) + 1u)) & 31u)) >= (__repairseal_shr(__repairseal_shr(2147483647u, y & 31u), 7u & 31u)))) && ((b >= ((a - y) & (__repairseal_shr(b, r & 31u)))) && ((__repairseal_shl(__repairseal_shr(4294967295u, 3u & 31u), 2u & 31u)) > (4294967295u & (__repairseal_rem(4294967295u, (3u & 7u) + 1u))))))
  {
    r = 2u;
  }
  else
  {
    r = x;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = 31u | y;
  unsigned b = 1u;
  unsigned r = y;
  if ((~(3u ^ r)) < a)
  {
    r = __repairseal_shl((r & r) | b, x & 31u);
  }
  else
  {
    r = __repairseal_div(__repairseal_div(x & 15u, ((a ^ x) & 7u) + 1u), (4294967295u & 7u) + 1u);
  }
  if (((((__repairseal_shr(x, y & 31u)) - (x + r)) >= a) || ((__repairseal_shl(x ^ r, (__repairseal_rem(r, (y & 7u) + 1u)) & 31u)) >= (__repairseal_shr(__repairseal_shr(2147483647u, y & 31u), 7u & 31u)))) && ((b >= ((a - y) & (__repairseal_shr(b, r & 31u)))) && ((__repairseal_shl(__repairseal_shr(4294967295u, 3u & 31u), 2u & 31u)) > (4294967295u & (__repairseal_rem(4294967295u, (3u & 7u) + 1u))))))
  {
    r = 2u;
  }
  else
  {
    r = x;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
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
