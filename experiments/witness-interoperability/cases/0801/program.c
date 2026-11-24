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
unsigned __repairseal_original(unsigned m, unsigned n)
{
  return __repairseal_div((m + n) - 1u, n);
}


unsigned __repairseal_candidate(unsigned m, unsigned n)
{
  unsigned rs_generated0 = 0u;
  if ((__repairseal_rem(m, n)) != 0u)
  {
    rs_generated0 = 1u;
  }
  else
  {
    rs_generated0 = 0u;
  }
  return (__repairseal_div(m, n)) + rs_generated0;
}


unsigned __repairseal_reference(unsigned m, unsigned n)
{
  unsigned r = 0u;
  if (m == 0u)
  {
    r = 0u;
  }
  else
  {
    r = 1u + (__repairseal_div(m - 1u, n));
  }
  return r;
}


int main(void) { 
  unsigned m = __VERIFIER_nondet_uint();
  if (!(m == 0u || m == 1u || m == 2u || m == 3u || m == 4u || m == 5u || m == 6u || m == 7u || m == 8u || m == 9u || m == 10u || m == 11u || m == 12u || m == 13u || m == 14u || m == 15u || m == 16u || m == 17u || m == 18u || m == 19u || m == 20u || m == 21u || m == 22u || m == 23u || m == 24u || m == 25u || m == 26u || m == 27u || m == 28u || m == 29u || m == 30u || m == 31u || m == 4294967264u || m == 4294967265u || m == 4294967266u || m == 4294967267u || m == 4294967268u || m == 4294967269u || m == 4294967270u || m == 4294967271u || m == 4294967272u || m == 4294967273u || m == 4294967274u || m == 4294967275u || m == 4294967276u || m == 4294967277u || m == 4294967278u || m == 4294967279u || m == 4294967280u || m == 4294967281u || m == 4294967282u || m == 4294967283u || m == 4294967284u || m == 4294967285u || m == 4294967286u || m == 4294967287u || m == 4294967288u || m == 4294967289u || m == 4294967290u || m == 4294967291u || m == 4294967292u || m == 4294967293u || m == 4294967294u || m == 4294967295u)) return 0;
  unsigned n = __VERIFIER_nondet_uint();
  if (!(n == 1u || n == 2u || n == 3u || n == 4u || n == 5u || n == 6u || n == 7u || n == 8u || n == 9u || n == 10u || n == 11u || n == 12u || n == 13u || n == 14u || n == 15u || n == 16u || n == 17u || n == 18u || n == 19u || n == 20u || n == 21u || n == 22u || n == 23u || n == 24u || n == 25u || n == 26u || n == 27u || n == 28u || n == 29u || n == 30u || n == 31u || n == 32u || n == 4294967264u || n == 4294967265u || n == 4294967266u || n == 4294967267u || n == 4294967268u || n == 4294967269u || n == 4294967270u || n == 4294967271u || n == 4294967272u || n == 4294967273u || n == 4294967274u || n == 4294967275u || n == 4294967276u || n == 4294967277u || n == 4294967278u || n == 4294967279u || n == 4294967280u || n == 4294967281u || n == 4294967282u || n == 4294967283u || n == 4294967284u || n == 4294967285u || n == 4294967286u || n == 4294967287u || n == 4294967288u || n == 4294967289u || n == 4294967290u || n == 4294967291u || n == 4294967292u || n == 4294967293u || n == 4294967294u || n == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(m, n);
  if (m > (4294967295u - (n - 1u))) {
    unsigned __repairseal_t = __repairseal_reference(m, n);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(m, n);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
