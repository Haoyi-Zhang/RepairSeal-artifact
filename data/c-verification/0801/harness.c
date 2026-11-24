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
  unsigned m = __VERIFIER_nondet_uint();
  __CPROVER_assume(m == 0u || m == 1u || m == 2u || m == 3u || m == 4u || m == 5u || m == 6u || m == 7u || m == 8u || m == 9u || m == 10u || m == 11u || m == 12u || m == 13u || m == 14u || m == 15u || m == 16u || m == 17u || m == 18u || m == 19u || m == 20u || m == 21u || m == 22u || m == 23u || m == 24u || m == 25u || m == 26u || m == 27u || m == 28u || m == 29u || m == 30u || m == 31u || m == 4294967264u || m == 4294967265u || m == 4294967266u || m == 4294967267u || m == 4294967268u || m == 4294967269u || m == 4294967270u || m == 4294967271u || m == 4294967272u || m == 4294967273u || m == 4294967274u || m == 4294967275u || m == 4294967276u || m == 4294967277u || m == 4294967278u || m == 4294967279u || m == 4294967280u || m == 4294967281u || m == 4294967282u || m == 4294967283u || m == 4294967284u || m == 4294967285u || m == 4294967286u || m == 4294967287u || m == 4294967288u || m == 4294967289u || m == 4294967290u || m == 4294967291u || m == 4294967292u || m == 4294967293u || m == 4294967294u || m == 4294967295u);
  unsigned n = __VERIFIER_nondet_uint();
  __CPROVER_assume(n == 1u || n == 2u || n == 3u || n == 4u || n == 5u || n == 6u || n == 7u || n == 8u || n == 9u || n == 10u || n == 11u || n == 12u || n == 13u || n == 14u || n == 15u || n == 16u || n == 17u || n == 18u || n == 19u || n == 20u || n == 21u || n == 22u || n == 23u || n == 24u || n == 25u || n == 26u || n == 27u || n == 28u || n == 29u || n == 30u || n == 31u || n == 32u || n == 4294967264u || n == 4294967265u || n == 4294967266u || n == 4294967267u || n == 4294967268u || n == 4294967269u || n == 4294967270u || n == 4294967271u || n == 4294967272u || n == 4294967273u || n == 4294967274u || n == 4294967275u || n == 4294967276u || n == 4294967277u || n == 4294967278u || n == 4294967279u || n == 4294967280u || n == 4294967281u || n == 4294967282u || n == 4294967283u || n == 4294967284u || n == 4294967285u || n == 4294967286u || n == 4294967287u || n == 4294967288u || n == 4294967289u || n == 4294967290u || n == 4294967291u || n == 4294967292u || n == 4294967293u || n == 4294967294u || n == 4294967295u);
  unsigned __repairseal_q = __repairseal_candidate(m, n);
  if (
m > (4294967295u - (n - 1u))
  ) {
    unsigned __repairseal_t = __repairseal_reference(m, n);
    __CPROVER_assert(__repairseal_q == __repairseal_t, "repairseal.repair");
  } else {
    unsigned __repairseal_p = __repairseal_original(m, n);
    __CPROVER_assert(__repairseal_q == __repairseal_p, "repairseal.preserve");
  }
  return 0;
}
