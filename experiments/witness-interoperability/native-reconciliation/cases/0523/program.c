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
  unsigned a = 15u;
  unsigned b = ((__repairseal_shr(a, 0u & 31u)) ^ (__repairseal_rem(x, (x & 7u) + 1u))) | ((z * 0u) * (__repairseal_rem(y, (x & 7u) + 1u)));
  unsigned r = (1u ^ 15u) & ((__repairseal_div(b, (0u & 7u) + 1u)) + x);
  if (((((__repairseal_shl(7u, y & 31u)) | 2147483647u) != ((1u ^ 7u) & (3u ^ 1u))) && ((__repairseal_div(z + 3u, ((__repairseal_shr(r, a & 31u)) & 7u) + 1u)) <= x)) && ((__repairseal_shl(__repairseal_div(31u, (b & 7u) + 1u), 4294967295u & 31u)) != ((__repairseal_shr(1u, 0u & 31u)) * (__repairseal_rem(3u, (r & 7u) + 1u)))))
  {
    r = b & ((__repairseal_shr(y, z & 31u)) + (4294967295u | r));
  }
  else
  {
    r = z & (y | (x | a));
  }
  if (((y <= y) || (31u < a)) && (((b | a) != (__repairseal_shl(7u ^ 2u, (__repairseal_div(3u, (b & 7u) + 1u)) & 31u))) && ((__repairseal_rem(z & r, ((y ^ 4294967295u) & 7u) + 1u)) <= ((a & r) - (__repairseal_rem(x, (r & 7u) + 1u))))))
  {
    r = 3u;
  }
  else
  {
    r = y | r;
  }
  if (x == 2u)
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
  unsigned poison = __repairseal_div(1u, z ^ 31u);
  unsigned a = 15u;
  unsigned b = ((__repairseal_shr(a, 0u & 31u)) ^ (__repairseal_rem(x, (x & 7u) + 1u))) | ((z * 0u) * (__repairseal_rem(y, (x & 7u) + 1u)));
  unsigned r = (1u ^ 15u) & ((__repairseal_div(b, (0u & 7u) + 1u)) + x);
  if (((((__repairseal_shl(7u, y & 31u)) | 2147483647u) != ((1u ^ 7u) & (3u ^ 1u))) && ((__repairseal_div(z + 3u, ((__repairseal_shr(r, a & 31u)) & 7u) + 1u)) <= x)) && ((__repairseal_shl(__repairseal_div(31u, (b & 7u) + 1u), 4294967295u & 31u)) != ((__repairseal_shr(1u, 0u & 31u)) * (__repairseal_rem(3u, (r & 7u) + 1u)))))
  {
    r = b & ((__repairseal_shr(y, z & 31u)) + (4294967295u | r));
  }
  else
  {
    r = z & (y | (x | a));
  }
  if (((y <= y) || (31u < a)) && (((b | a) != (__repairseal_shl(7u ^ 2u, (__repairseal_div(3u, (b & 7u) + 1u)) & 31u))) && ((__repairseal_rem(z & r, ((y ^ 4294967295u) & 7u) + 1u)) <= ((a & r) - (__repairseal_rem(x, (r & 7u) + 1u))))))
  {
    r = 3u;
  }
  else
  {
    r = y | r;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y, unsigned z)
{
  unsigned a = 15u;
  unsigned b = ((__repairseal_shr(a, 0u & 31u)) ^ (__repairseal_rem(x, (x & 7u) + 1u))) | ((z * 0u) * (__repairseal_rem(y, (x & 7u) + 1u)));
  unsigned r = (1u ^ 15u) & ((__repairseal_div(b, (0u & 7u) + 1u)) + x);
  if (((((__repairseal_shl(7u, y & 31u)) | 2147483647u) != ((1u ^ 7u) & (3u ^ 1u))) && ((__repairseal_div(z + 3u, ((__repairseal_shr(r, a & 31u)) & 7u) + 1u)) <= x)) && ((__repairseal_shl(__repairseal_div(31u, (b & 7u) + 1u), 4294967295u & 31u)) != ((__repairseal_shr(1u, 0u & 31u)) * (__repairseal_rem(3u, (r & 7u) + 1u)))))
  {
    r = b & ((__repairseal_shr(y, z & 31u)) + (4294967295u | r));
  }
  else
  {
    r = z & (y | (x | a));
  }
  if (((y <= y) || (31u < a)) && (((b | a) != (__repairseal_shl(7u ^ 2u, (__repairseal_div(3u, (b & 7u) + 1u)) & 31u))) && ((__repairseal_rem(z & r, ((y ^ 4294967295u) & 7u) + 1u)) <= ((a & r) - (__repairseal_rem(x, (r & 7u) + 1u))))))
  {
    r = 3u;
  }
  else
  {
    r = y | r;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 2u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 3u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned z = __VERIFIER_nondet_uint();
  if (!(z == 0u || z == 1u || z == 3u || z == 31u || z == 32u || z == 2147483647u || z == 2147483648u || z == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y, z);
  if ((x == 2u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y, z);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y, z);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
