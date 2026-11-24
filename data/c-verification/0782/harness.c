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
  unsigned w = __VERIFIER_nondet_uint();
  __CPROVER_assume(w == 1u || w == 2u || w == 3u || w == 4u || w == 5u || w == 6u || w == 7u || w == 8u || w == 9u || w == 10u || w == 11u || w == 12u || w == 13u || w == 14u || w == 15u || w == 16u || w == 17u || w == 18u || w == 19u || w == 20u || w == 21u || w == 22u || w == 23u || w == 24u || w == 25u || w == 26u || w == 27u || w == 28u || w == 29u || w == 30u || w == 31u || w == 32u || w == 33u || w == 34u || w == 35u || w == 36u || w == 37u || w == 38u || w == 39u || w == 40u || w == 41u || w == 42u || w == 43u || w == 44u || w == 45u || w == 46u || w == 47u || w == 48u || w == 49u || w == 50u || w == 51u || w == 52u || w == 53u || w == 54u || w == 55u || w == 56u || w == 57u || w == 58u || w == 59u || w == 60u || w == 61u || w == 62u || w == 63u || w == 64u);
  unsigned __repairseal_q = __repairseal_candidate(w);
  if (
w == 2u
  ) {
    unsigned __repairseal_t = __repairseal_reference(w);
    __CPROVER_assert(__repairseal_q == __repairseal_t, "repairseal.repair");
  } else {
    unsigned __repairseal_p = __repairseal_original(w);
    __CPROVER_assert(__repairseal_q == __repairseal_p, "repairseal.preserve");
  }
  return 0;
}
