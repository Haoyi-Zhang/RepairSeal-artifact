#include <limits.h>
#include <stdlib.h>
#define main repairseal_subject_main
#include "program.c"
#undef main
_Static_assert(sizeof(unsigned) * CHAR_BIT == 32, "32-bit unsigned required");
static unsigned supplied[8];
static unsigned position;
unsigned __VERIFIER_nondet_uint(void) { return supplied[position++]; }
void __VERIFIER_error(void) { _Exit(17); }
int main(int argc, char **argv) {
  if (argc < 2 || argc > 9) return 31;
  for (int i = 1; i < argc; ++i) supplied[i-1] = (unsigned)strtoul(argv[i], 0, 10);
  position = 0u;
  repairseal_subject_main();
  return 0;
}
