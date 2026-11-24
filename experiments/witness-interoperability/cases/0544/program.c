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
  unsigned a = y;
  unsigned b = ((y + 15u) * 15u) - (y + (a * y));
  unsigned r = (b ^ (__repairseal_shl(a, 15u & 31u))) + b;
  if (!(((__repairseal_rem(2147483647u, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)) > (0u & a)) && ((r & (x | a)) >= (__repairseal_div(r | r, (b & 7u) + 1u)))))
  {
    r = (__repairseal_shl(__repairseal_div(y, (r & 7u) + 1u), a & 31u)) | ((r * b) - (15u * 31u));
  }
  else
  {
    r = ~b;
  }
  if ((__repairseal_shl(b, a & 31u)) <= x)
  {
    r = (__repairseal_shr(~r, (__repairseal_shl(x, y & 31u)) & 31u)) - (__repairseal_shr(r ^ a, b & 31u));
  }
  else
  {
    r = (__repairseal_shr(~3u, (1u * b) & 31u)) | (__repairseal_shl(a * 1u, a & 31u));
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
  unsigned a = y;
  unsigned b = ((y + 15u) * 15u) - (y + (a * y));
  unsigned r = (b ^ (__repairseal_shl(a, 15u & 31u))) + b;
  if (!(((__repairseal_rem(2147483647u, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)) > (0u & a)) && ((r & (x | a)) >= (__repairseal_div(r | r, (b & 7u) + 1u)))))
  {
    r = (__repairseal_shl(__repairseal_div(y, (r & 7u) + 1u), a & 31u)) | ((r * b) - (15u * 31u));
  }
  else
  {
    r = ~b;
  }
  if ((__repairseal_shl(b, a & 31u)) <= x)
  {
    r = (__repairseal_shr(~r, (__repairseal_shl(x, y & 31u)) & 31u)) - (__repairseal_shr(r ^ a, b & 31u));
  }
  else
  {
    r = (__repairseal_shr(~3u, (1u * b) & 31u)) | (__repairseal_shl(a * 1u, a & 31u));
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = y;
  unsigned b = ((y + 15u) * 15u) - (y + (a * y));
  unsigned r = (b ^ (__repairseal_shl(a, 15u & 31u))) + b;
  if (!(((__repairseal_rem(2147483647u, ((__repairseal_rem(y, (y & 7u) + 1u)) & 7u) + 1u)) > (0u & a)) && ((r & (x | a)) >= (__repairseal_div(r | r, (b & 7u) + 1u)))))
  {
    r = (__repairseal_shl(__repairseal_div(y, (r & 7u) + 1u), a & 31u)) | ((r * b) - (15u * 31u));
  }
  else
  {
    r = ~b;
  }
  if ((__repairseal_shl(b, a & 31u)) <= x)
  {
    r = (__repairseal_shr(~r, (__repairseal_shl(x, y & 31u)) & 31u)) - (__repairseal_shr(r ^ a, b & 31u));
  }
  else
  {
    r = (__repairseal_shr(~3u, (1u * b) & 31u)) | (__repairseal_shl(a * 1u, a & 31u));
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
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
