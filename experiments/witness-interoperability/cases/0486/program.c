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
  unsigned a = ((0u & y) - 4294967295u) & (~(x + 4294967295u));
  unsigned b = ((__repairseal_shl(y, x & 31u)) * (__repairseal_shr(2147483647u, x & 31u))) * y;
  unsigned r = ~y;
  if ((7u <= r) && (x == ((b ^ b) & (x * r))))
  {
    r = __repairseal_shr(1u - (__repairseal_rem(r, (x & 7u) + 1u)), b & 31u);
  }
  else
  {
    r = a & (r - (__repairseal_div(2147483647u, (a & 7u) + 1u)));
  }
  if (x == 31u)
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
  unsigned a = ((0u & y) - 4294967295u) & (~(x + 4294967295u));
  unsigned b = ((__repairseal_shl(y, x & 31u)) * (__repairseal_shr(2147483647u, x & 31u))) * y;
  unsigned r = ~y;
  if ((7u <= r) && (x == ((b ^ b) & (x * r))))
  {
    r = __repairseal_shr(1u - (__repairseal_rem(r, (x & 7u) + 1u)), b & 31u);
  }
  else
  {
    r = a & (r - (__repairseal_div(2147483647u, (a & 7u) + 1u)));
  }
  if ((x == 2147483648u) && (y == 2147483648u))
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
  unsigned a = ((0u & y) - 4294967295u) & (~(x + 4294967295u));
  unsigned b = ((__repairseal_shl(y, x & 31u)) * (__repairseal_shr(2147483647u, x & 31u))) * y;
  unsigned r = ~y;
  if ((7u <= r) && (x == ((b ^ b) & (x * r))))
  {
    r = __repairseal_shr(1u - (__repairseal_rem(r, (x & 7u) + 1u)), b & 31u);
  }
  else
  {
    r = a & (r - (__repairseal_div(2147483647u, (a & 7u) + 1u)));
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 31u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
