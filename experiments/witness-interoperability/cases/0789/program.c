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
unsigned __repairseal_original(unsigned w)
{
  unsigned r = 0u;
  if ((w >= w) && ((__repairseal_rem(w, 2u)) == 0u))
  {
    r = 1u;
  }
  else
  {
    r = 0u;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned w)
{
  unsigned r = 0u;
  if ((w >= 4u) && ((__repairseal_rem(w, 2u)) == 0u))
  {
    r = 1u;
  }
  else
  {
    r = 0u;
  }
  return r;
}


unsigned __repairseal_reference(unsigned w)
{
  unsigned r = 0u;
  if ((w > 2u) && ((__repairseal_rem(w, 2u)) == 0u))
  {
    r = 1u;
  }
  else
  {
    r = 0u;
  }
  return r;
}


int main(void) { 
  unsigned w = __VERIFIER_nondet_uint();
  if (!(w == 2u || w == 3u || w == 4u || w == 5u || w == 8u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(w);
  if (w == 2u) {
    unsigned __repairseal_t = __repairseal_reference(w);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(w);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
