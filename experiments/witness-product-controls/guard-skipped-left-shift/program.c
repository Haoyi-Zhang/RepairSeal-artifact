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
unsigned __repairseal_original(unsigned x)
{
  return x + 1u;
}


unsigned __repairseal_candidate(unsigned x)
{
  return x;
}


unsigned __repairseal_reference(unsigned x)
{
  return x;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x);
  if ((x == x) || ((__repairseal_shl(1u, 32u)) > 0u)) {
    unsigned __repairseal_t = __repairseal_reference(x);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
