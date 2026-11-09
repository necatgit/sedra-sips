# 0002: How ZKas merged mining (AuxPoW) works

| | |
|---|---|
| Date | 2026-11-05 |
| Reviewed | zkas-rusty `97fafeca`, rusty-kaspa `4edcbbcc` (v2.1.0), sedrad `4a1153d` (v2.0.0), PuddlePool's Miningcore `38054dec` |
| Full report | Raw report with all file:line references and evidence; published later with the project repository |
| Review | The central claims were re-checked directly in the source; see "Review notes" |

Labels: **Verified** = checked in code or data, with a reference. **Inferred** = reasoned from evidence, could be wrong.
**Unknown** = not determinable from the sources.

## Summary

- **How it works (Verified).** A pool puts a 68-byte commitment to the ZKas block (`ZKM1` + 64 hex characters) into the
  coinbase of the Kaspa block it is mining. If the work on that Kaspa block also meets ZKas's (lower) difficulty, the
  pool sends ZKas a proof: the Kaspa header, its coinbase transaction and a Merkle path linking the two. Kaspa nodes need
  no change.
- **Dual acceptance (Verified).** A ZKas block is valid if its own proof of work meets the target, or if it carries a
  valid proof of this kind. Native mining keeps working.
- **"Secured by Kaspa" would be an overstatement (Verified).** ZKas checks only that enough kHeavyHash work was done and
  bound to the ZKas block. It does not check that the "parent" is a real or accepted Kaspa block; the code says so
  explicitly. PuddlePool already uses Sedra blocks as ZKas parents. **A merged-mined chain is only as secure as the
  hashrate that chooses to mine it.**
- **Free hashrate cuts both ways (Inferred).** Merged mining costs Kaspa miners nothing extra. That is what attracts
  hashrate, but it also means a large Kaspa pool could dominate the aux chain at no cost. ZKas has no mitigation for this.
- **Difficulty (Verified).** ZKas's difficulty adjustment has no merged-mining logic: aux-mined blocks count like any
  other. How it behaves when a large pool joins or leaves suddenly was not measured.
- **Hardening (Verified).** After launch ZKas needed several security fixes, including one where a single solution
  could be credited to two ZKas blocks. Merged mining is not a small or low-risk change.
- **SDR and ZKAS in the same Kaspa block: possible, but only just (Inferred, arithmetic from verified constants).**
  Kaspa limits the coinbase payload to 204 bytes. With a standard payout address and the node's version prefix, about
  145 bytes remain for the pool. Two 68-byte commitments use 136, leaving about 9 bytes for the pool's own tag.
  A third coin cannot fit. PuddlePool's current tag (~22 bytes) would have to shrink.
- **Pools (Verified).** Each pool needs code per aux coin. PuddlePool's Miningcore supports one aux coin per pool today,
  so it needs multi-aux support. Whether other Kaspa pools would add a Sedra commitment is **Unknown**.
- **Size of the port (Inferred).** ZKas's core merged-mining logic is about 1,150 lines of Rust including tests. Adding it
  to Sedra touches the block header and its P2P, RPC and database encodings, PoW validation, the pruning proof, fork
  activation and tests.

## What Sedra would need (Inferred, design input for SIP-0001)

1. Its own commitment tag (not `ZKMM`/`ZKM1`, and containing a character outside `0-9a-f` so it can never appear inside
   another chain's hex), with a commitment bound to Sedra's genesis block.
2. The same "exactly once" rule for the tag, nonce binding, and a ban on Sedra's own tag inside Sedra's coinbase.
3. Size limits on the proof, a fork activation by DAA score, and tests for valid, invalid and boundary cases.
4. Test vectors proving that Sedra's hashing gives byte-identical results to Kaspa's on real Kaspa blocks
   (not yet tested).

## Open questions

Tracked in the project's question list:

- Byte budget for pools, shorter or shared commitment with ZKas: Q18 (decided: own commitment); raw-bytes commitment: Q25 (decided: base64url, see SIP-0001 §4.2)
- Whether Sedra's hashing of Kaspa parent headers matches Kaspa's exactly: Q19
- Keeping up with Kaspa header format changes: Q20
- Which other Kaspa pools would add Sedra: Q21
- Whether the merged-mining security model is acceptable: Q22
- How Sedra's difficulty reacts to large merged hashrate joining or leaving: Q23
- Scope of Sedra's self-parent ban: Q24

## What this does NOT mean

- It does **not** mean Sedra can be merged-mined today, or that any Kaspa pool has agreed to do it.
- It does **not** mean Sedra would inherit Kaspa's security.
- It does **not** mean the port is small or low-risk.
- Byte-level compatibility between Sedra's hashing and Kaspa's is **not** established; it is inferred from matching code.
- It says nothing about prices, rewards, adoption or timelines.

## Review notes

- Re-checked in zkas-rusty `97fafeca` on 2026-11-05: the "parent need not be a valid Kaspa block" statement
  (`consensus/core/src/auxpow.rs:25-26`), the `ZKMM`/`ZKM1` tags (`:47`, `:51`) and the exactly-once rule. Re-checked in
  rusty-kaspa `4edcbbcc`: `max_coinbase_payload_len: 204` (`consensus/core/src/config/params.rs:614`).
- References to PuddlePool's Miningcore code (`@mc` in the full report) cannot be checked from outside, because that
  repository is not public.
- Correction of an earlier statement by the project: in early planning, merged mining was described as Sedra being
  "secured by Kaspa". That was an overstatement; see the summary.
