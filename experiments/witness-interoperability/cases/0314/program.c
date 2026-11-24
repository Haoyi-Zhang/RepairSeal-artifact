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
  unsigned r = ((x + 8u) * (y + 1u)) ^ (z + 5u);
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
  unsigned scratch = t;
  if ((t & 1u) == 0u)
  {
    scratch = scratch + 1u;
  }
  else
  {
    scratch = scratch + 2u;
  }
  unsigned r = (z + 5u) ^ ((1u + y) * (8u + x));
  if ((x == 2u) && (z == 2u))
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
  unsigned r = ((x + 8u) * (y + 1u)) ^ (z + 5u);
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 2u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 2u)) return 0;
  unsigned t = __VERIFIER_nondet_uint();
  if (!(t == 0u || t == 1u || t == 2u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if (x == 0u) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
