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
  unsigned n = __VERIFIER_nondet_uint();
  __CPROVER_assume(n == 2u || n == 4u);
  unsigned __repairseal_q = __repairseal_candidate(n);
  if (
n == n
  ) {
    unsigned __repairseal_t = __repairseal_reference(n);
    __CPROVER_assert(__repairseal_q == __repairseal_t, "repairseal.repair");
  } else {
    unsigned __repairseal_p = __repairseal_original(n);
    __CPROVER_assert(__repairseal_q == __repairseal_p, "repairseal.preserve");
  }
  return 0;
}
