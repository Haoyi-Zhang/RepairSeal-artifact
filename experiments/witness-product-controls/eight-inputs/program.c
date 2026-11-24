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
unsigned __repairseal_original(unsigned x0, unsigned x1, unsigned x2, unsigned x3, unsigned x4, unsigned x5, unsigned x6, unsigned x7)
{
  return ((((((x0 + x1) + x2) + x3) + x4) + x5) + x6) + x7;
}


unsigned __repairseal_candidate(unsigned x0, unsigned x1, unsigned x2, unsigned x3, unsigned x4, unsigned x5, unsigned x6, unsigned x7)
{
  return (((((((x0 + x1) + x2) + x3) + x4) + x5) + x6) + x7) + 1u;
}


unsigned __repairseal_reference(unsigned x0, unsigned x1, unsigned x2, unsigned x3, unsigned x4, unsigned x5, unsigned x6, unsigned x7)
{
  return ((((((x0 + x1) + x2) + x3) + x4) + x5) + x6) + x7;
}


int main(void) { 
  unsigned x0 = __VERIFIER_nondet_uint();
  if (!(x0 == 0u)) return 0;
  unsigned x1 = __VERIFIER_nondet_uint();
  if (!(x1 == 0u)) return 0;
  unsigned x2 = __VERIFIER_nondet_uint();
  if (!(x2 == 0u)) return 0;
  unsigned x3 = __VERIFIER_nondet_uint();
  if (!(x3 == 0u)) return 0;
  unsigned x4 = __VERIFIER_nondet_uint();
  if (!(x4 == 0u)) return 0;
  unsigned x5 = __VERIFIER_nondet_uint();
  if (!(x5 == 0u)) return 0;
  unsigned x6 = __VERIFIER_nondet_uint();
  if (!(x6 == 0u)) return 0;
  unsigned x7 = __VERIFIER_nondet_uint();
  if (!(x7 == 0u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x0, x1, x2, x3, x4, x5, x6, x7);
  if (x0 == x0) {
    unsigned __repairseal_t = __repairseal_reference(x0, x1, x2, x3, x4, x5, x6, x7);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x0, x1, x2, x3, x4, x5, x6, x7);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
