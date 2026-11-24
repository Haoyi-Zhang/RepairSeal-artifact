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
  unsigned a = ~(__repairseal_div(y, ((y + 2u) & 7u) + 1u));
  unsigned b = ((y + z) & (t ^ x)) ^ ((15u - 1u) & t);
  unsigned r = x;
  if ((__repairseal_shl(y, r & 31u)) == (__repairseal_shl(z - 7u, (x & b) & 31u)))
  {
    r = t | ((t + 2u) ^ (__repairseal_rem(r, (2u & 7u) + 1u)));
  }
  else
  {
    r = ((r - r) | y) * (__repairseal_rem(15u, ((__repairseal_div(a, (2147483647u & 7u) + 1u)) & 7u) + 1u));
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


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = ~(__repairseal_div(y, ((y + 2u) & 7u) + 1u));
  unsigned b = ((y + z) & (t ^ x)) ^ ((15u - 1u) & t);
  unsigned r = x;
  if ((__repairseal_shl(y, r & 31u)) == (__repairseal_shl(z - 7u, (x & b) & 31u)))
  {
    r = t | ((t + 2u) ^ (__repairseal_rem(r, (2u & 7u) + 1u)));
  }
  else
  {
    r = ((r - r) | y) * (__repairseal_rem(15u, ((__repairseal_div(a, (2147483647u & 7u) + 1u)) & 7u) + 1u));
  }
  if ((x == 31u) && (y == 32u))
  {
    r = r + 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z, unsigned t)
{
  unsigned a = ~(__repairseal_div(y, ((y + 2u) & 7u) + 1u));
  unsigned b = ((y + z) & (t ^ x)) ^ ((15u - 1u) & t);
  unsigned r = x;
  if ((__repairseal_shl(y, r & 31u)) == (__repairseal_shl(z - 7u, (x & b) & 31u)))
  {
    r = t | ((t + 2u) ^ (__repairseal_rem(r, (2u & 7u) + 1u)));
  }
  else
  {
    r = ((r - r) | y) * (__repairseal_rem(15u, ((__repairseal_div(a, (2147483647u & 7u) + 1u)) & 7u) + 1u));
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 2u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned t = __VERIFIER_nondet_uint();
  if (!(t == 0u || t == 1u || t == 3u || t == 31u || t == 32u || t == 2147483647u || t == 2147483648u || t == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if ((x == 4294967295u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
