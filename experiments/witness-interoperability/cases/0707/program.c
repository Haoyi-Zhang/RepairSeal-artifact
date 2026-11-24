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
  unsigned a = (y | y) + (__repairseal_shl(3u, (__repairseal_shl(2u, y & 31u)) & 31u));
  unsigned b = __repairseal_rem(~(15u * y), ((y + 4294967295u) & 7u) + 1u);
  unsigned r = __repairseal_shr(y, ((__repairseal_shr(b, x & 31u)) - (7u + y)) & 31u);
  if ((15u != (__repairseal_rem(31u & 15u, ((b & x) & 7u) + 1u))) && ((__repairseal_div(__repairseal_div(1u, (a & 7u) + 1u), ((__repairseal_rem(r, (2u & 7u) + 1u)) & 7u) + 1u)) >= y))
  {
    r = (a * (a & y)) + r;
  }
  else
  {
    r = ((__repairseal_div(a, (2147483647u & 7u) + 1u)) + (__repairseal_shr(x, 31u & 31u))) * ((1u ^ 31u) * a);
  }
  if ((((__repairseal_div(a, (y & 7u) + 1u)) + 1u) >= b) && ((__repairseal_rem(y + y, ((b * 2147483647u) & 7u) + 1u)) < x))
  {
    r = __repairseal_div(b, ((__repairseal_shl(15u, (__repairseal_div(a, (r & 7u) + 1u)) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x + x;
  }
  if (x == 32u)
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
  unsigned a = (y | y) + (__repairseal_shl(3u, (__repairseal_shl(2u, y & 31u)) & 31u));
  unsigned b = __repairseal_rem(~(15u * y), ((y + 4294967295u) & 7u) + 1u);
  unsigned r = __repairseal_shr(y, ((__repairseal_shr(b, x & 31u)) - (7u + y)) & 31u);
  if ((15u != (__repairseal_rem(31u & 15u, ((b & x) & 7u) + 1u))) && ((__repairseal_div(__repairseal_div(1u, (a & 7u) + 1u), ((__repairseal_rem(r, (2u & 7u) + 1u)) & 7u) + 1u)) >= y))
  {
    r = (a * (a & y)) + r;
  }
  else
  {
    r = ((__repairseal_div(a, (2147483647u & 7u) + 1u)) + (__repairseal_shr(x, 31u & 31u))) * ((1u ^ 31u) * a);
  }
  if ((((__repairseal_div(a, (y & 7u) + 1u)) + 1u) >= b) && ((__repairseal_rem(y + y, ((b * 2147483647u) & 7u) + 1u)) < x))
  {
    r = __repairseal_div(b, ((__repairseal_shl(15u, (__repairseal_div(a, (r & 7u) + 1u)) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x + x;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = (y | y) + (__repairseal_shl(3u, (__repairseal_shl(2u, y & 31u)) & 31u));
  unsigned b = __repairseal_rem(~(15u * y), ((y + 4294967295u) & 7u) + 1u);
  unsigned r = __repairseal_shr(y, ((__repairseal_shr(b, x & 31u)) - (7u + y)) & 31u);
  if ((15u != (__repairseal_rem(31u & 15u, ((b & x) & 7u) + 1u))) && ((__repairseal_div(__repairseal_div(1u, (a & 7u) + 1u), ((__repairseal_rem(r, (2u & 7u) + 1u)) & 7u) + 1u)) >= y))
  {
    r = (a * (a & y)) + r;
  }
  else
  {
    r = ((__repairseal_div(a, (2147483647u & 7u) + 1u)) + (__repairseal_shr(x, 31u & 31u))) * ((1u ^ 31u) * a);
  }
  if ((((__repairseal_div(a, (y & 7u) + 1u)) + 1u) >= b) && ((__repairseal_rem(y + y, ((b * 2147483647u) & 7u) + 1u)) < x))
  {
    r = __repairseal_div(b, ((__repairseal_shl(15u, (__repairseal_div(a, (r & 7u) + 1u)) & 31u)) & 7u) + 1u);
  }
  else
  {
    r = x + x;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 32u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
