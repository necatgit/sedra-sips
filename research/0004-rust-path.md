# 0004: Go node or Rust codebase

| | |
|---|---|
| Date | 2026-11-05 |
| Reviewed | sedrad `v2.0.0` = `4a1153d`; kaspad (Go) `v0.12.15` = `5a3b8a00`; rusty-kaspa `v1.0.1` = `fcd9c28f`, `v1.1.0`, `4edcbbcc` (v2.1.0+); zkas-rusty `f5f3c050` |
| Full report | Raw report published later with the project repository; helper scripts in [archive/2026-11-05-0004-scripts/](archive/2026-11-05-0004-scripts/) |
| Decision | **Rust, based on rusty-kaspa v1.0.1**, in two steps (see "Decision"). Decided 2026-11-05 by Nec |

Labels: **Verified** = checked in code, with a command or data, with a reference. **Inferred** = reasoned from evidence,
could be wrong. **Unknown** = not determinable from the sources.

## Summary

- **Sedra is a copy of Kaspa's Go node v0.12.15 (Verified).** After normalizing renames it differs from that tag by 580
  lines, fewer than from any other Kaspa version.
- **Sedra's consensus differences from Kaspa are small and fully listed (Verified):** the genesis block, network name,
  address prefixes, ports and seeds, a different subsidy table from month 8 on, and the two v2.0.0 rules (difficulty
  reset and treasury outputs). Proof of work, hashing, GHOSTDAG, difficulty adjustment, pruning, pruning proof, script
  engine and the network wire format are identical to Kaspa v0.12.15.
- **Sedra's genesis hash can be reproduced with rusty-kaspa's rules (Verified).** A small script reimplementing
  rusty-kaspa v1.0.1's hashing reproduces Sedra's mainnet genesis hash `7c380ae6…5ffa`, after first reproducing a Kaspa
  genesis as a control. Re-run independently during review.
- **The current rusty-kaspa cannot run Sedra's chain (Verified).** After v1.0.1, Kaspa deleted the 1-block-per-second
  rules Sedra still uses and the P2P protocol version 5 that Sedra's Go nodes speak (removed in `f25a737b`, first
  release without it: v1.1.0).
- **rusty-kaspa v1.0.1 (June 2025) is the natural base (Inferred).** All later Kaspa features sit behind one switch
  (`crescendo_activation`) that can be set to "never". The version-5 network code is still there; on mainnet it is
  blocked by a one-line condition (Verified).
- **zkas-rusty is not a good base (Verified).** It is based on a newer rusty-kaspa that lacks the old rules, and adds
  about 250,000 lines, mostly privacy code. Its merged-mining core (~1,200 lines) can be ported on its own.
- **One Go-vs-Rust difference found (Verified):** Go uses the genesis difficulty until the difficulty window holds 2641
  blocks; rusty-kaspa only below 150. Sedra's parameters must use 2641. It affects only blocks near genesis.
- **A normal sync never exercises the v2.0.0 rules (Inferred).** New nodes start from a recent pruning point, and the
  v2.0.0 windows are long below it. Those rules need dedicated tests.

## Decision

**Path A: a Rust node based on rusty-kaspa v1.0.1, in two steps.**

1. **Step 1, no fork:** a Rust node with exactly the same consensus as Sedra mainnet today, syncing and running next to
   the existing Go nodes. Proven milestone by milestone (M1-M9 below).
2. **Step 2, the merged-mining hard fork:** port the AuxPoW parts of ZKas into the proven Rust node (M10 onwards).

Why: the merged-mining code already exists in Rust; Kaspa's Go node has been unmaintained since 2023, so building on it
is a dead end; and a Rust base can later move towards newer Kaspa features through planned upgrades.

The cost, stated plainly: v1.0.1 is a frozen version. Nobody upstream maintains it, so security fixes from later Kaspa
releases must be reviewed and carried over by this project.

Fallback: if a milestone fails in a way that cannot be fixed, the project returns to path B (merged mining in the Go
node). The merged-mining design is the same for both paths.

## Milestones for Step 1

Each milestone is a yes/no check, tracked as an issue.

| # | Checkpoint | How it is verified |
|---|---|---|
| M0 | Sedra's genesis hash is reproducible with rusty-kaspa v1.0.1's hashing rules | **Done**: `archive/2026-11-05-0004-scripts/genesis_hash.py` prints `match=True` |
| M1 | rusty-kaspa v1.0.1 with Sedra's network: genesis, names, address prefixes, ports, seeds, subsidy table, later Kaspa features off, minimum difficulty window 2641 | it builds, tests pass, and a unit test asserts the genesis hash |
| M2 | Rust subsidy equals Go subsidy at every month boundary | table-driven test against values from sedrad |
| M3 | Real Sedra headers decode and validate offline: hashes, proof of work, GHOSTDAG, DAA score | headers exported from a local Go node |
| M4 | Network handshake with a local Go node over protocol version 5, no bans | logs on both sides |
| M5 | Full sync from the local Go node, then follows the tip | same tip and DAA score over at least an hour |
| M6 | The v2.0.0 rules (difficulty reset, treasury outputs) behave exactly like Go | dedicated tests mirroring sedrad's tests |
| M7 | Same UTXO commitment and circulating supply as the Go node at the same point | compare on both nodes |
| M8 | Blocks mined by the Rust node are accepted by the Go node and vice versa (isolated test setup) | local test mining only |
| M9 | Seven days next to Go nodes with no divergence | periodic comparison |

## Risks and open questions

Open questions are tracked in the project's question list under the IDs in brackets.

- **Subsidy table change in April 2025 (Unknown).** If it applied to months already mined, the chain contains two
  subsidy tables. A normal sync is not affected, but full verification from genesis would need the switch point (Q26).
- **Sedra's own copies of two libraries** (`sedracoin/go-muhash` v1.0.1, `sedracoin/go-secp256k1` v1.0.2) have not been
  compared with Kaspa's originals (Unknown). M7 would catch a difference in the first (Q28).
- **Coinbase output limit in the treasury windows (Inferred).** Why only 163 of 200 and 400 of 454 slots paid out is
  not explained; the Rust node must reproduce Go's behaviour exactly (Q29).
- **Maintenance burden** of a frozen base, and possible code paths that assume the disabled Kaspa features eventually
  activate (back-port triage: Q31).
- **Pool and explorer compatibility.** The Rust node's RPC differs from the Go node's. Miningcore already talks to
  rusty-kaspa nodes for Kaspa, which is encouraging, but the Sedra integration has not been checked (Q32).
- Further open questions from this research: an archival node from genesis (Q27), other Go-vs-Rust differences near
  genesis (Q30).

## What this does NOT mean

*Update 2026-11-09: since this note was written, milestones M0-M8 are done and M9 (seven days next to Go nodes) runs
until 2026-11-14; see SIP-0001 §3. The first point below describes the state on 2026-11-05.*

- A Rust Sedra node does not exist yet, and nothing has been shown to sync Sedra mainnet. Compatibility is inferred from
  source code; milestones M3-M9 are the proof.
- It says nothing about whether the merged-mining fork is safe, scheduled or agreed.
- It does not endorse Sedra's emission, the treasury amounts or the v2.0.0 decisions; it only describes how they are
  coded.

## Review notes

Re-checked independently on 2026-11-05: kaspad tag `v0.12.15` = `5a3b8a00` exists; rusty-kaspa `v1.0.1` = `fcd9c28f`
contains the v5 flows (`protocol/flows/src/flow_context.rs:796`) behind `connect_only_new_versions =
network_type() != Testnet` (`:784`); the first release tag containing `f25a737b` is `v1.1.0`; `genesis_hash.py`
re-run gives `7c380ae690f9eaa64f300451d5e466371113c38b96ed96fe3f1e934869355ffa` for Sedra mainnet, equal to
`genesisHash` in sedrad `domain/dagconfig/genesis.go:34-36` at `4a1153d`. Also re-checked: sedrad v2.0.0 builds and
passes its own tests (log published later with the project repository).
