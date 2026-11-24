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
unsigned __repairseal_original(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = y + ((t - z) | (__repairseal_shr(z, x & 31u)));
  unsigned b = (__repairseal_shl(t | y, (__repairseal_div(y, (t & 7u) + 1u)) & 31u)) | (__repairseal_shr(t, (__repairseal_div(3u, (2147483647u & 7u) + 1u)) & 31u));
  unsigned r = ((__repairseal_shl(y, 31u & 31u)) ^ x) & (__repairseal_shl(y, z & 31u));
  if ((__repairseal_rem(b | z, ((~z) & 7u) + 1u)) >= (__repairseal_shr(15u - b, (r ^ r) & 31u)))
  {
    r = ~((7u - 0u) + t);
  }
  else
  {
    r = 2u;
  }
  if (((((__repairseal_rem(2u, (y & 7u) + 1u)) * (t * r)) >= (__repairseal_rem(a, ((x + b) & 7u) + 1u))) && ((b + (a & z)) >= ((r * 2147483647u) & r))) || ((__repairseal_rem(15u ^ 2147483647u, ((z + a) & 7u) + 1u)) != r))
  {
    r = r | (__repairseal_rem(r, ((t | b) & 7u) + 1u));
  }
  else
  {
    r = (__repairseal_shl(__repairseal_div(y, (a & 7u) + 1u), (t * 4294967295u) & 31u)) + (__repairseal_rem(r | x, ((r + a) & 7u) + 1u));
  }
  if (x == 0u)
  {
    r = r - 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned poison = __repairseal_div(1u, t ^ 1u);
  unsigned a = y + ((t - z) | (__repairseal_shr(z, x & 31u)));
  unsigned b = (__repairseal_shl(t | y, (__repairseal_div(y, (t & 7u) + 1u)) & 31u)) | (__repairseal_shr(t, (__repairseal_div(3u, (2147483647u & 7u) + 1u)) & 31u));
  unsigned r = ((__repairseal_shl(y, 31u & 31u)) ^ x) & (__repairseal_shl(y, z & 31u));
  if ((__repairseal_rem(b | z, ((~z) & 7u) + 1u)) >= (__repairseal_shr(15u - b, (r ^ r) & 31u)))
  {
    r = ~((7u - 0u) + t);
  }
  else
  {
    r = 2u;
  }
  if (((((__repairseal_rem(2u, (y & 7u) + 1u)) * (t * r)) >= (__repairseal_rem(a, ((x + b) & 7u) + 1u))) && ((b + (a & z)) >= ((r * 2147483647u) & r))) || ((__repairseal_rem(15u ^ 2147483647u, ((z + a) & 7u) + 1u)) != r))
  {
    r = r | (__repairseal_rem(r, ((t | b) & 7u) + 1u));
  }
  else
  {
    r = (__repairseal_shl(__repairseal_div(y, (a & 7u) + 1u), (t * 4294967295u) & 31u)) + (__repairseal_rem(r | x, ((r + a) & 7u) + 1u));
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = y + ((t - z) | (__repairseal_shr(z, x & 31u)));
  unsigned b = (__repairseal_shl(t | y, (__repairseal_div(y, (t & 7u) + 1u)) & 31u)) | (__repairseal_shr(t, (__repairseal_div(3u, (2147483647u & 7u) + 1u)) & 31u));
  unsigned r = ((__repairseal_shl(y, 31u & 31u)) ^ x) & (__repairseal_shl(y, z & 31u));
  if ((__repairseal_rem(b | z, ((~z) & 7u) + 1u)) >= (__repairseal_shr(15u - b, (r ^ r) & 31u)))
  {
    r = ~((7u - 0u) + t);
  }
  else
  {
    r = 2u;
  }
  if (((((__repairseal_rem(2u, (y & 7u) + 1u)) * (t * r)) >= (__repairseal_rem(a, ((x + b) & 7u) + 1u))) && ((b + (a & z)) >= ((r * 2147483647u) & r))) || ((__repairseal_rem(15u ^ 2147483647u, ((z + a) & 7u) + 1u)) != r))
  {
    r = r | (__repairseal_rem(r, ((t | b) & 7u) + 1u));
  }
  else
  {
    r = (__repairseal_shl(__repairseal_div(y, (a & 7u) + 1u), (t * 4294967295u) & 31u)) + (__repairseal_rem(r | x, ((r + a) & 7u) + 1u));
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned t = __VERIFIER_nondet_uint();
  if (!(t == 0u || t == 1u || t == 3u || t == 31u || t == 32u || t == 2147483647u || t == 2147483648u || t == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if ((x == 0u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
