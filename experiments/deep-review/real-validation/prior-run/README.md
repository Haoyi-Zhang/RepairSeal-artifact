# Superseded initial native run

This directory preserves the first complete execution and the exact
`run.py`/`order_types.py` source bytes bound in its protocol. It is historical
evidence and is **not** added to the final campaign's 10,602 execution count.

Independent code review found two overbroad admission boundaries in the generic
new quotient profile: names that a real `<stdio.h>` could expand as macros,
and I/O strings whose Python-decoded meaning differs from C hex-escape rules.
None of the thirteen retained source identities uses those constructs, but
the admission gate was narrowed, adversarial regression cases were added, and
the entire native campaign was executed again with fresh code/domain/compiler
bindings. The authoritative final records are `../records/`.

The initial run finished at 2026-11-26T19:45:15.486693+00:00. Its exact original
protocol, sources, native receipts, summary, verification output and logs remain
here. The source snapshot's relative directory assumptions refer to the
original study location; it is a byte preimage for audit, not a relocated
standalone reproduction entry point. No historical dependency hash was edited
to disguise the subsequent gate changes.
