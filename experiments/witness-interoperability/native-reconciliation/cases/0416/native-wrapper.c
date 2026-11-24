#define main __repairseal_main
#include "program.c"
#undef main
_Static_assert(sizeof(unsigned) == 4, "32-bit unsigned required");
static unsigned __repairseal_values[8];
static unsigned __repairseal_position;
static int __repairseal_failed;
unsigned __VERIFIER_nondet_uint(void) {
  return __repairseal_values[__repairseal_position++];
}
void __VERIFIER_error(void) { __repairseal_failed = 1; }
int repairseal_point(const unsigned *values, unsigned count) {
  for(unsigned i=0; i<count; ++i) __repairseal_values[i] = values[i];
  __repairseal_position = 0u;
  __repairseal_failed = 0;
  __repairseal_main();
  return __repairseal_failed;
}
