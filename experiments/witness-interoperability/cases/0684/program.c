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
unsigned __repairseal_original(unsigned x, unsigned y)
{
  unsigned a = (__repairseal_rem(x - y, (x & 7u) + 1u)) * (x - (2147483647u ^ x));
  unsigned b = ~(__repairseal_div(y, ((~x) & 7u) + 1u));
  unsigned r = (__repairseal_rem(__repairseal_div(a, (a & 7u) + 1u), ((15u ^ 15u) & 7u) + 1u)) | y;
  if (((__repairseal_rem(b ^ x, ((__repairseal_rem(2u, (7u & 7u) + 1u)) & 7u) + 1u)) == (__repairseal_div(y + 4294967295u, ((__repairseal_shr(2147483647u, x & 31u)) & 7u) + 1u))) && (2147483647u < ((2u * a) ^ (~y))))
  {
    r = ((2u + y) - (__repairseal_rem(b, (r & 7u) + 1u))) + ((__repairseal_rem(0u, (b & 7u) + 1u)) - r);
  }
  else
  {
    r = __repairseal_shl(r * 4294967295u, r & 31u);
  }
  if (((y | b) * (__repairseal_rem(2u, (2u & 7u) + 1u))) != b)
  {
    r = y;
  }
  else
  {
    r = ((__repairseal_rem(b, (15u & 7u) + 1u)) ^ (__repairseal_div(x, (31u & 7u) + 1u))) + b;
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


unsigned __repairseal_candidate(unsigned x, unsigned y)
{
  unsigned a = (__repairseal_rem(x - y, (x & 7u) + 1u)) * (x - (2147483647u ^ x));
  unsigned b = ~(__repairseal_div(y, ((~x) & 7u) + 1u));
  unsigned r = (__repairseal_rem(__repairseal_div(a, (a & 7u) + 1u), ((15u ^ 15u) & 7u) + 1u)) | y;
  if (((__repairseal_rem(b ^ x, ((__repairseal_rem(2u, (7u & 7u) + 1u)) & 7u) + 1u)) == (__repairseal_div(y + 4294967295u, ((__repairseal_shr(2147483647u, x & 31u)) & 7u) + 1u))) && (2147483647u < ((2u * a) ^ (~y))))
  {
    r = ((2u + y) - (__repairseal_rem(b, (r & 7u) + 1u))) + ((__repairseal_rem(0u, (b & 7u) + 1u)) - r);
  }
  else
  {
    r = __repairseal_shl(r * 4294967295u, r & 31u);
  }
  if (((y | b) * (__repairseal_rem(2u, (2u & 7u) + 1u))) != b)
  {
    r = y;
  }
  else
  {
    r = ((__repairseal_rem(b, (15u & 7u) + 1u)) ^ (__repairseal_div(x, (31u & 7u) + 1u))) + b;
  }
  return r;
}


unsigned __repairseal_reference(unsigned x, unsigned y)
{
  unsigned a = (__repairseal_rem(x - y, (x & 7u) + 1u)) * (x - (2147483647u ^ x));
  unsigned b = ~(__repairseal_div(y, ((~x) & 7u) + 1u));
  unsigned r = (__repairseal_rem(__repairseal_div(a, (a & 7u) + 1u), ((15u ^ 15u) & 7u) + 1u)) | y;
  if (((__repairseal_rem(b ^ x, ((__repairseal_rem(2u, (7u & 7u) + 1u)) & 7u) + 1u)) == (__repairseal_div(y + 4294967295u, ((__repairseal_shr(2147483647u, x & 31u)) & 7u) + 1u))) && (2147483647u < ((2u * a) ^ (~y))))
  {
    r = ((2u + y) - (__repairseal_rem(b, (r & 7u) + 1u))) + ((__repairseal_rem(0u, (b & 7u) + 1u)) - r);
  }
  else
  {
    r = __repairseal_shl(r * 4294967295u, r & 31u);
  }
  if (((y | b) * (__repairseal_rem(2u, (2u & 7u) + 1u))) != b)
  {
    r = y;
  }
  else
  {
    r = ((__repairseal_rem(b, (15u & 7u) + 1u)) ^ (__repairseal_div(x, (31u & 7u) + 1u))) + b;
  }
  return r;
}


int main(void) { 
  unsigned x = __VERIFIER_nondet_uint();
  if (!(x == 0u || x == 1u || x == 3u || x == 31u || x == 32u || x == 2147483647u || x == 2147483648u || x == 4294967295u)) return 0;
  unsigned y = __VERIFIER_nondet_uint();
  if (!(y == 0u || y == 1u || y == 2u || y == 31u || y == 32u || y == 2147483647u || y == 2147483648u || y == 4294967295u)) return 0;
  unsigned __repairseal_q = __repairseal_candidate(x, y);
  if ((x == 0u)) {
    unsigned __repairseal_t = __repairseal_reference(x, y);
    if (__repairseal_q != __repairseal_t) __VERIFIER_error();
  } else {
    unsigned __repairseal_p = __repairseal_original(x, y);
    if (__repairseal_q != __repairseal_p) __VERIFIER_error();
  }
  return 0;
}
