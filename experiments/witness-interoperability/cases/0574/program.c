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
unsigned __repairseal_original(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(~(__repairseal_div(x, (z & 7u) + 1u)), (z & 7u) + 1u);
  unsigned b = 1u;
  unsigned r = z;
  if ((((~y) + y) >= ((r - r) * y)) || (((__repairseal_shl(__repairseal_shl(b, 31u & 31u), (y & b) & 31u)) == ((1u ^ z) - (x + 0u))) || ((__repairseal_shr(__repairseal_shl(r, b & 31u), (z * x) & 31u)) > (x * x))))
  {
    r = 31u;
  }
  else
  {
    r = (3u & 3u) * y;
  }
  if (x == 2147483648u)
  {
    r = r - 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_candidate(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(~(__repairseal_div(x, (z & 7u) + 1u)), (z & 7u) + 1u);
  unsigned b = 1u;
  unsigned r = z;
  if ((((~y) + y) >= ((r - r) * y)) || (((__repairseal_shl(__repairseal_shl(b, 31u & 31u), (y & b) & 31u)) == ((1u ^ z) - (x + 0u))) || ((__repairseal_shr(__repairseal_shl(r, b & 31u), (z * x) & 31u)) > (x * x))))
  {
    r = 31u;
  }
  else
  {
    r = (3u & 3u) * y;
  }
  if ((x == 3u) && (y == 3u))
  {
    r = r + 1u;
  }
  else
  {
    r = r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z)
{
  unsigned a = __repairseal_div(~(__repairseal_div(x, (z & 7u) + 1u)), (z & 7u) + 1u);
  unsigned b = 1u;
  unsigned r = z;
  if ((((~y) + y) >= ((r - r) * y)) || (((__repairseal_shl(__repairseal_shl(b, 31u & 31u), (y & b) & 31u)) == ((1u ^ z) - (x + 0u))) || ((__repairseal_shr(__repairseal_shl(r, b & 31u), (z * x) & 31u)) > (x * x))))
  {
    r = 31u;
  }
  else
  {
    r = (3u & 3u) * y;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z);
  if ((x == 2147483648u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
