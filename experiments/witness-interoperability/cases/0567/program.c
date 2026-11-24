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
  unsigned a = ((__repairseal_shr(x, y & 31u)) ^ (y + x)) * y;
  unsigned b = y | (__repairseal_shl(__repairseal_rem(0u, (a & 7u) + 1u), (__repairseal_div(15u, (x & 7u) + 1u)) & 31u));
  unsigned r = __repairseal_div(__repairseal_shl(__repairseal_shl(1u, 15u & 31u), a & 31u), (y & 7u) + 1u);
  if (31u != (__repairseal_shl(__repairseal_div(x, (y & 7u) + 1u), x & 31u)))
  {
    r = __repairseal_rem(b, ((__repairseal_shr(x, (a ^ r) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = 3u;
  }
  if (((__repairseal_div(y, (2147483647u & 7u) + 1u)) + (b - r)) != (r + (a | b)))
  {
    r = __repairseal_shl(__repairseal_shl(b, (__repairseal_shr(r, b & 31u)) & 31u), ((y ^ 2147483647u) & (__repairseal_shl(1u, b & 31u))) & 31u);
  }
  else
  {
    r = __repairseal_shl(y + 4294967295u, ((__repairseal_shr(b, a & 31u)) * x) & 31u);
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
  unsigned poison = __repairseal_div(1u, y ^ 32u);
  unsigned a = ((__repairseal_shr(x, y & 31u)) ^ (y + x)) * y;
  unsigned b = y | (__repairseal_shl(__repairseal_rem(0u, (a & 7u) + 1u), (__repairseal_div(15u, (x & 7u) + 1u)) & 31u));
  unsigned r = __repairseal_div(__repairseal_shl(__repairseal_shl(1u, 15u & 31u), a & 31u), (y & 7u) + 1u);
  if (31u != (__repairseal_shl(__repairseal_div(x, (y & 7u) + 1u), x & 31u)))
  {
    r = __repairseal_rem(b, ((__repairseal_shr(x, (a ^ r) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = 3u;
  }
  if (((__repairseal_div(y, (2147483647u & 7u) + 1u)) + (b - r)) != (r + (a | b)))
  {
    r = __repairseal_shl(__repairseal_shl(b, (__repairseal_shr(r, b & 31u)) & 31u), ((y ^ 2147483647u) & (__repairseal_shl(1u, b & 31u))) & 31u);
  }
  else
  {
    r = __repairseal_shl(y + 4294967295u, ((__repairseal_shr(b, a & 31u)) * x) & 31u);
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = ((__repairseal_shr(x, y & 31u)) ^ (y + x)) * y;
  unsigned b = y | (__repairseal_shl(__repairseal_rem(0u, (a & 7u) + 1u), (__repairseal_div(15u, (x & 7u) + 1u)) & 31u));
  unsigned r = __repairseal_div(__repairseal_shl(__repairseal_shl(1u, 15u & 31u), a & 31u), (y & 7u) + 1u);
  if (31u != (__repairseal_shl(__repairseal_div(x, (y & 7u) + 1u), x & 31u)))
  {
    r = __repairseal_rem(b, ((__repairseal_shr(x, (a ^ r) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = 3u;
  }
  if (((__repairseal_div(y, (2147483647u & 7u) + 1u)) + (b - r)) != (r + (a | b)))
  {
    r = __repairseal_shl(__repairseal_shl(b, (__repairseal_shr(r, b & 31u)) & 31u), ((y ^ 2147483647u) & (__repairseal_shl(1u, b & 31u))) & 31u);
  }
  else
  {
    r = __repairseal_shl(y + 4294967295u, ((__repairseal_shr(b, a & 31u)) * x) & 31u);
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
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
