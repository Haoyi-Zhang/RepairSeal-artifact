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
  unsigned a = __repairseal_shr(~(__repairseal_shl(y, y & 31u)), x & 31u);
  unsigned b = a * a;
  unsigned r = __repairseal_rem(b, ((__repairseal_shr(__repairseal_shr(y, 15u & 31u), b & 31u)) & 7u) + 1u);
  if ((__repairseal_rem(__repairseal_shr(x, 2u & 31u), ((b + x) & 7u) + 1u)) == 2147483647u)
  {
    r = 4294967295u;
  }
  else
  {
    r = __repairseal_div(__repairseal_shl(0u - r, (__repairseal_div(y, (4294967295u & 7u) + 1u)) & 31u), (r & 7u) + 1u);
  }
  if (x <= ((__repairseal_shl(y, b & 31u)) - b))
  {
    r = (__repairseal_shl(a, (3u | r) & 31u)) + (__repairseal_rem(0u, (b & 7u) + 1u));
  }
  else
  {
    r = y;
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


unsigned __repairseal_candidate(unsigned x, unsigned y)
{
  unsigned poison = __repairseal_div(1u, y ^ 1u);
  unsigned a = __repairseal_shr(~(__repairseal_shl(y, y & 31u)), x & 31u);
  unsigned b = a * a;
  unsigned r = __repairseal_rem(b, ((__repairseal_shr(__repairseal_shr(y, 15u & 31u), b & 31u)) & 7u) + 1u);
  if ((__repairseal_rem(__repairseal_shr(x, 2u & 31u), ((b + x) & 7u) + 1u)) == 2147483647u)
  {
    r = 4294967295u;
  }
  else
  {
    r = __repairseal_div(__repairseal_shl(0u - r, (__repairseal_div(y, (4294967295u & 7u) + 1u)) & 31u), (r & 7u) + 1u);
  }
  if (x <= ((__repairseal_shl(y, b & 31u)) - b))
  {
    r = (__repairseal_shl(a, (3u | r) & 31u)) + (__repairseal_rem(0u, (b & 7u) + 1u));
  }
  else
  {
    r = y;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = __repairseal_shr(~(__repairseal_shl(y, y & 31u)), x & 31u);
  unsigned b = a * a;
  unsigned r = __repairseal_rem(b, ((__repairseal_shr(__repairseal_shr(y, 15u & 31u), b & 31u)) & 7u) + 1u);
  if ((__repairseal_rem(__repairseal_shr(x, 2u & 31u), ((b + x) & 7u) + 1u)) == 2147483647u)
  {
    r = 4294967295u;
  }
  else
  {
    r = __repairseal_div(__repairseal_shl(0u - r, (__repairseal_div(y, (4294967295u & 7u) + 1u)) & 31u), (r & 7u) + 1u);
  }
  if (x <= ((__repairseal_shl(y, b & 31u)) - b))
  {
    r = (__repairseal_shl(a, (3u | r) & 31u)) + (__repairseal_rem(0u, (b & 7u) + 1u));
  }
  else
  {
    r = y;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 2147483648u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
