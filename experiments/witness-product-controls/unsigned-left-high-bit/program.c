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
  return x;
}


unsigned __repairseal_candidate(unsigned x)
{
  return __repairseal_shl(x, 31u);
}


unsigned __repairseal_reference(unsigned x)
{
  return (x & 1u) * 2147483648u;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x);
  if (x == x) {
    unsigned __repairseal_t = __repairseal_reference(x);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
