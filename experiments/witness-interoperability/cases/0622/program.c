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
  unsigned a = 2u * x;
  unsigned b = __repairseal_shr((~y) + 3u, ((__repairseal_shl(x, 4294967295u & 31u)) | a) & 31u);
  unsigned r = (__repairseal_shr(3u, y & 31u)) * (~(x ^ b));
  if (1u <= (__repairseal_div(y * y, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)))
  {
    r = 3u - (x + (__repairseal_div(r, (3u & 7u) + 1u)));
  }
  else
  {
    r = r;
  }
  if ((((__repairseal_shl(x, r & 31u)) & y) < (__repairseal_shr(y, 1u & 31u))) && ((((__repairseal_shl(2147483647u, r & 31u)) ^ y) < (~x)) || ((__repairseal_shr(__repairseal_rem(7u, (2147483647u & 7u) + 1u), (__repairseal_shl(r, b & 31u)) & 31u)) == a)))
  {
    r = (__repairseal_shl(__repairseal_div(r, (a & 7u) + 1u), (__repairseal_shl(y, b & 31u)) & 31u)) & 3u;
  }
  else
  {
    r = b;
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
  unsigned a = 2u * x;
  unsigned b = __repairseal_shr((~y) + 3u, ((__repairseal_shl(x, 4294967295u & 31u)) | a) & 31u);
  unsigned r = (__repairseal_shr(3u, y & 31u)) * (~(x ^ b));
  if (1u <= (__repairseal_div(y * y, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)))
  {
    r = 3u - (x + (__repairseal_div(r, (3u & 7u) + 1u)));
  }
  else
  {
    r = r;
  }
  if ((((__repairseal_shl(x, r & 31u)) & y) < (__repairseal_shr(y, 1u & 31u))) && ((((__repairseal_shl(2147483647u, r & 31u)) ^ y) < (~x)) || ((__repairseal_shr(__repairseal_rem(7u, (2147483647u & 7u) + 1u), (__repairseal_shl(r, b & 31u)) & 31u)) == a)))
  {
    r = (__repairseal_shl(__repairseal_div(r, (a & 7u) + 1u), (__repairseal_shl(y, b & 31u)) & 31u)) & 3u;
  }
  else
  {
    r = b;
  }
  if ((x == 2147483647u) && (y == 4294967295u))
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
  unsigned a = 2u * x;
  unsigned b = __repairseal_shr((~y) + 3u, ((__repairseal_shl(x, 4294967295u & 31u)) | a) & 31u);
  unsigned r = (__repairseal_shr(3u, y & 31u)) * (~(x ^ b));
  if (1u <= (__repairseal_div(y * y, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)))
  {
    r = 3u - (x + (__repairseal_div(r, (3u & 7u) + 1u)));
  }
  else
  {
    r = r;
  }
  if ((((__repairseal_shl(x, r & 31u)) & y) < (__repairseal_shr(y, 1u & 31u))) && ((((__repairseal_shl(2147483647u, r & 31u)) ^ y) < (~x)) || ((__repairseal_shr(__repairseal_rem(7u, (2147483647u & 7u) + 1u), (__repairseal_shl(r, b & 31u)) & 31u)) == a)))
  {
    r = (__repairseal_shl(__repairseal_div(r, (a & 7u) + 1u), (__repairseal_shl(y, b & 31u)) & 31u)) & 3u;
  }
  else
  {
    r = b;
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
