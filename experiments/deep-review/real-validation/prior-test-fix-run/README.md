# Superseded run before a test-only spelling correction

The computational gate, quotient proof, and native runner were already correct in this complete run. Offline verification passed. A positive unittest accessed the misspelled field `native_process_execututions`; the actual result field is `native_process_executions`. The typo made one of 17 tests error, while all four receipt-tampering controls and all 12 gate tests passed.

Because the test file is explicitly hash-bound in the frozen protocol, its one-token correction was followed by a complete new native run. This run and exact code/test preimages are preserved rather than editing its original protocol hashes. Its native executions are not added to the final reported campaign. Authoritative data are in `../records/`.
