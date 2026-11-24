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
unsigned __repairseal_original(unsigned main)
{
  return main;
}


unsigned __repairseal_candidate(unsigned main)
{
  return main;
}


unsigned __repairseal_reference(unsigned main)
{
  return main;
}


int main(void) { 
  unsigned main = __VERIFIER_nondet_uint();
  if (!(main == 0u || main == 1u || main == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(main);
  if (main == main) {
    unsigned __repairseal_t = __repairseal_reference(main);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(main);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
