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
unsigned __repairseal_original(unsigned n)
{
  return (__repairseal_div(3u, 2u)) * n;
}


unsigned __repairseal_candidate(unsigned n)
{
  return (__repairseal_div(3u, 2u)) * n;
}


unsigned __repairseal_reference(unsigned n)
{
  return __repairseal_div(3u * n, 2u);
}


int main(void) { 
  unsigned n = __VERIFIER_nondet_uint();
  if (!(n == 2u || n == 4u || n == 10000u || n == 25460u || n == 50000u || n == 54646u || n == 59790u || n == 578456u || n == 8457980u || n == 56798056u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(n);
  if (n == n) {
    unsigned __repairseal_t = __repairseal_reference(n);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(n);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
