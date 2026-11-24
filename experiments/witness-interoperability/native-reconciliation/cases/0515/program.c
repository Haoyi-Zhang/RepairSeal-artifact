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
  unsigned b = x & 3u;
  unsigned r = y;
  if ((((__repairseal_shl(b, (0u | a) & 31u)) != (__repairseal_shr(y - r, r & 31u))) || ((__repairseal_div(y + 15u, ((__repairseal_rem(b, (r & 7u) + 1u)) & 7u) + 1u)) > ((r - b) * (y & b)))) && (3u < 0u))
  {
    r = __repairseal_div((__repairseal_shl(r, a & 31u)) | (r ^ b), ((x ^ b) & 7u) + 1u);
  }
  else
  {
    r = (~(x * 15u)) | ((__repairseal_shr(4294967295u, y & 31u)) * a);
  }
  if (!(x == r))
  {
    r = r;
  }
  else
  {
    r = y;
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
  unsigned poison = __repairseal_div(1u, y ^ 1u);
  unsigned a = x;
  unsigned b = x & 3u;
  unsigned r = y;
  if ((((__repairseal_shl(b, (0u | a) & 31u)) != (__repairseal_shr(y - r, r & 31u))) || ((__repairseal_div(y + 15u, ((__repairseal_rem(b, (r & 7u) + 1u)) & 7u) + 1u)) > ((r - b) * (y & b)))) && (3u < 0u))
  {
    r = __repairseal_div((__repairseal_shl(r, a & 31u)) | (r ^ b), ((x ^ b) & 7u) + 1u);
  }
  else
  {
    r = (~(x * 15u)) | ((__repairseal_shr(4294967295u, y & 31u)) * a);
  }
  if (!(x == r))
  {
    r = r;
  }
  else
  {
    r = y;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = x;
  unsigned b = x & 3u;
  unsigned r = y;
  if ((((__repairseal_shl(b, (0u | a) & 31u)) != (__repairseal_shr(y - r, r & 31u))) || ((__repairseal_div(y + 15u, ((__repairseal_rem(b, (r & 7u) + 1u)) & 7u) + 1u)) > ((r - b) * (y & b)))) && (3u < 0u))
  {
    r = __repairseal_div((__repairseal_shl(r, a & 31u)) | (r ^ b), ((x ^ b) & 7u) + 1u);
  }
  else
  {
    r = (~(x * 15u)) | ((__repairseal_shr(4294967295u, y & 31u)) * a);
  }
  if (!(x == r))
  {
    r = r;
  }
  else
  {
    r = y;
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
