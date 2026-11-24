/* Generated wrapper. Included receiver-owned functions are unchanged. */
_Static_assert(sizeof(unsigned) == 4, "unsigned must occupy four bytes");
_Static_assert(~0u == 4294967295u, "unsigned must have 32 value bits");
extern unsigned __VERIFIER_nondet_uint(void);
extern void __CPROVER_assume(_Bool);
extern void __CPROVER_assert(_Bool, const char *);
#define f __repairseal_original
#include "original.c"
#undef f
#define f __repairseal_candidate
#include "candidate.c"
#undef f
#define f __repairseal_reference
#include "reference.c"
#undef f
int main(void)
{
  unsigned x = __VERIFIER_nondet_uint();
  __CPROVER_assume(x == 0u || x == 1u || x == 2u);
  unsigned y = __VERIFIER_nondet_uint();
  __CPROVER_assume(y == 0u || y == 1u || y == 2u);
  unsigned z = __VERIFIER_nondet_uint();
  __CPROVER_assume(z == 0u || z == 1u || z == 2u);
  unsigned t = __VERIFIER_nondet_uint();
  __CPROVER_assume(t == 0u || t == 1u || t == 2u);
  unsigned __repairseal_q = __repairseal_candidate(x, y, z, t);
  if (
x == 0u
  ) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z, t);
    __CPROVER_assert(__repairseal_q == __repairseal_t, "repairseal.repair");
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z, t);
    __CPROVER_assert(__repairseal_q == __repairseal_p, "repairseal.preserve");
  }
  return 0;
}
