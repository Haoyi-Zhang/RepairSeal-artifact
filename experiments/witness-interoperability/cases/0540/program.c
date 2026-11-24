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
  unsigned a = ((2147483647u | x) + (~x)) ^ ((z + x) | (__repairseal_shl(z, 0u & 31u)));
  unsigned b = (a & a) & y;
  unsigned r = z;
  if ((__repairseal_shr(__repairseal_shr(z, r & 31u), (31u ^ z) & 31u)) != ((b | x) + (__repairseal_shl(b, z & 31u))))
  {
    r = (b + (1u ^ z)) - (__repairseal_div(y * 2147483647u, (1u & 7u) + 1u));
  }
  else
  {
    r = b;
  }
  if ((((a | y) | (z & r)) >= (__repairseal_rem(x - z, (x & 7u) + 1u))) || ((15u <= (b + (3u & x))) && (a > 1u)))
  {
    r = ((z & b) - y) + (__repairseal_div(__repairseal_div(r, (y & 7u) + 1u), (b & 7u) + 1u));
  }
  else
  {
    r = 2147483647u | a;
  }
  if (x == 0u)
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
  unsigned a = ((2147483647u | x) + (~x)) ^ ((z + x) | (__repairseal_shl(z, 0u & 31u)));
  unsigned b = (a & a) & y;
  unsigned r = z;
  if ((__repairseal_shr(__repairseal_shr(z, r & 31u), (31u ^ z) & 31u)) != ((b | x) + (__repairseal_shl(b, z & 31u))))
  {
    r = (b + (1u ^ z)) - (__repairseal_div(y * 2147483647u, (1u & 7u) + 1u));
  }
  else
  {
    r = b;
  }
  if ((((a | y) | (z & r)) >= (__repairseal_rem(x - z, (x & 7u) + 1u))) || ((15u <= (b + (3u & x))) && (a > 1u)))
  {
    r = ((z & b) - y) + (__repairseal_div(__repairseal_div(r, (y & 7u) + 1u), (b & 7u) + 1u));
  }
  else
  {
    r = 2147483647u | a;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z)
{
  unsigned a = ((2147483647u | x) + (~x)) ^ ((z + x) | (__repairseal_shl(z, 0u & 31u)));
  unsigned b = (a & a) & y;
  unsigned r = z;
  if ((__repairseal_shr(__repairseal_shr(z, r & 31u), (31u ^ z) & 31u)) != ((b | x) + (__repairseal_shl(b, z & 31u))))
  {
    r = (b + (1u ^ z)) - (__repairseal_div(y * 2147483647u, (1u & 7u) + 1u));
  }
  else
  {
    r = b;
  }
  if ((((a | y) | (z & r)) >= (__repairseal_rem(x - z, (x & 7u) + 1u))) || ((15u <= (b + (3u & x))) && (a > 1u)))
  {
    r = ((z & b) - y) + (__repairseal_div(__repairseal_div(r, (y & 7u) + 1u), (b & 7u) + 1u));
  }
  else
  {
    r = 2147483647u | a;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 2u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z);
  if ((x == 0u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
