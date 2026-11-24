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
  unsigned a = x;
  unsigned b = (__repairseal_div(2u, ((a - y) & 7u) + 1u)) & (a & (__repairseal_shl(a, x & 31u)));
  unsigned r = __repairseal_div(__repairseal_shl(y & a, b & 31u), ((__repairseal_rem(__repairseal_div(x, (a & 7u) + 1u), ((a + b) & 7u) + 1u)) & 7u) + 1u);
  if ((__repairseal_shr(~r, r & 31u)) >= r)
  {
    r = __repairseal_rem(1u, ((__repairseal_div(b | x, (x & 7u) + 1u)) & 7u) + 1u);
  }
  else
  {
    r = x | x;
  }
  if ((!((31u ^ (a * 31u)) == (__repairseal_div(y | y, (3u & 7u) + 1u)))) && (4294967295u <= a))
  {
    r = b;
  }
  else
  {
    r = a;
  }
  if (x == 4294967295u)
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
  unsigned a = x;
  unsigned b = (__repairseal_div(2u, ((a - y) & 7u) + 1u)) & (a & (__repairseal_shl(a, x & 31u)));
  unsigned r = __repairseal_div(__repairseal_shl(y & a, b & 31u), ((__repairseal_rem(__repairseal_div(x, (a & 7u) + 1u), ((a + b) & 7u) + 1u)) & 7u) + 1u);
  if ((__repairseal_shr(~r, r & 31u)) >= r)
  {
    r = __repairseal_rem(1u, ((__repairseal_div(b | x, (x & 7u) + 1u)) & 7u) + 1u);
  }
  else
  {
    r = x | x;
  }
  if ((!((31u ^ (a * 31u)) == (__repairseal_div(y | y, (3u & 7u) + 1u)))) && (4294967295u <= a))
  {
    r = b;
  }
  else
  {
    r = a;
  }
  if ((x == 4294967295u) && (y == 0u))
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
  unsigned a = x;
  unsigned b = (__repairseal_div(2u, ((a - y) & 7u) + 1u)) & (a & (__repairseal_shl(a, x & 31u)));
  unsigned r = __repairseal_div(__repairseal_shl(y & a, b & 31u), ((__repairseal_rem(__repairseal_div(x, (a & 7u) + 1u), ((a + b) & 7u) + 1u)) & 7u) + 1u);
  if ((__repairseal_shr(~r, r & 31u)) >= r)
  {
    r = __repairseal_rem(1u, ((__repairseal_div(b | x, (x & 7u) + 1u)) & 7u) + 1u);
  }
  else
  {
    r = x | x;
  }
  if ((!((31u ^ (a * 31u)) == (__repairseal_div(y | y, (3u & 7u) + 1u)))) && (4294967295u <= a))
  {
    r = b;
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
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 4294967295u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
