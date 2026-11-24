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
  unsigned a = __repairseal_shl((~y) & y, (__repairseal_shl(y - x, (x - y) & 31u)) & 31u);
  unsigned b = ((__repairseal_div(x, (x & 7u) + 1u)) & y) + ((__repairseal_div(2u, (a & 7u) + 1u)) + (y * x));
  unsigned r = (2u + (x & a)) & ((__repairseal_rem(a, (b & 7u) + 1u)) | (x * x));
  if ((__repairseal_shr(__repairseal_rem(x, (r & 7u) + 1u), (__repairseal_div(2u, (b & 7u) + 1u)) & 31u)) > ((__repairseal_rem(y, (y & 7u) + 1u)) + 3u))
  {
    r = r & (__repairseal_shr(r + a, (b * b) & 31u));
  }
  else
  {
    r = 3u;
  }
  if (((((__repairseal_div(b, (x & 7u) + 1u)) | (__repairseal_shr(1u, 7u & 31u))) == b) || ((r + x) >= (~(y | 2147483647u)))) || (((b * 7u) * (__repairseal_shl(x, r & 31u))) != (__repairseal_rem(0u, (r & 7u) + 1u))))
  {
    r = ((b & 7u) & (r - r)) + 2147483647u;
  }
  else
  {
    r = x - (__repairseal_rem(a - x, ((b ^ x) & 7u) + 1u));
  }
  if (x == 3u)
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
  unsigned a = __repairseal_shl((~y) & y, (__repairseal_shl(y - x, (x - y) & 31u)) & 31u);
  unsigned b = ((__repairseal_div(x, (x & 7u) + 1u)) & y) + ((__repairseal_div(2u, (a & 7u) + 1u)) + (y * x));
  unsigned r = (2u + (x & a)) & ((__repairseal_rem(a, (b & 7u) + 1u)) | (x * x));
  if ((__repairseal_shr(__repairseal_rem(x, (r & 7u) + 1u), (__repairseal_div(2u, (b & 7u) + 1u)) & 31u)) > ((__repairseal_rem(y, (y & 7u) + 1u)) + 3u))
  {
    r = r & (__repairseal_shr(r + a, (b * b) & 31u));
  }
  else
  {
    r = 3u;
  }
  if (((((__repairseal_div(b, (x & 7u) + 1u)) | (__repairseal_shr(1u, 7u & 31u))) == b) || ((r + x) >= (~(y | 2147483647u)))) || (((b * 7u) * (__repairseal_shl(x, r & 31u))) != (__repairseal_rem(0u, (r & 7u) + 1u))))
  {
    r = ((b & 7u) & (r - r)) + 2147483647u;
  }
  else
  {
    r = x - (__repairseal_rem(a - x, ((b ^ x) & 7u) + 1u));
  }
  if ((x == 2147483647u) && (y == 0u))
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
  unsigned a = __repairseal_shl((~y) & y, (__repairseal_shl(y - x, (x - y) & 31u)) & 31u);
  unsigned b = ((__repairseal_div(x, (x & 7u) + 1u)) & y) + ((__repairseal_div(2u, (a & 7u) + 1u)) + (y * x));
  unsigned r = (2u + (x & a)) & ((__repairseal_rem(a, (b & 7u) + 1u)) | (x * x));
  if ((__repairseal_shr(__repairseal_rem(x, (r & 7u) + 1u), (__repairseal_div(2u, (b & 7u) + 1u)) & 31u)) > ((__repairseal_rem(y, (y & 7u) + 1u)) + 3u))
  {
    r = r & (__repairseal_shr(r + a, (b * b) & 31u));
  }
  else
  {
    r = 3u;
  }
  if (((((__repairseal_div(b, (x & 7u) + 1u)) | (__repairseal_shr(1u, 7u & 31u))) == b) || ((r + x) >= (~(y | 2147483647u)))) || (((b * 7u) * (__repairseal_shl(x, r & 31u))) != (__repairseal_rem(0u, (r & 7u) + 1u))))
  {
    r = ((b & 7u) & (r - r)) + 2147483647u;
  }
  else
  {
    r = x - (__repairseal_rem(a - x, ((b ^ x) & 7u) + 1u));
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 3u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
