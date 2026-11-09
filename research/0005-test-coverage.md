# 0005: Test coverage of the Go node and the Rust node

| | |
|---|---|
| Date | 2026-11-06 |
| Measured | sedrad `v2.0.0` = `4a1153d` (Go 1.26.8) and sedra-rusty `dev` = `e481e23f` (M1 plus build fix; rustc 1.99.1, cargo-llvm-cov 0.9.1) |
| Where | Test VM `sedra-dev` (Ubuntu 26.04, 6 cores) |
| Raw reports | [archive/2026-11-06-coverage/](archive/2026-11-06-coverage/) |

Labels: **Verified** = measured, with the report in the archive. **Inferred** = interpretation, could be wrong.

## What coverage means here, and what it does not

Coverage counts which lines or statements the tests **execute**. It says nothing about whether the tests check the
right results. A test that compares code with its own output can reach 100 % and prove nothing. For this project, what
counts most is the consensus code and the parity tests against the Go node (milestones M2-M7), whose expected values
come from sedrad or real chain data.

## Results (Verified)

**Overall**

| | Measure | Covered |
|---|---|---|
| Go node, sedrad v2.0.0 | statements, all tests counted for all packages (`-coverpkg=./...`) | **51.0 %** (17,133 / 33,611) |
| Rust node, sedra-rusty | lines (`cargo llvm-cov report`, TOTAL) | **57.6 %** (42,613 / 74,002) |
| Rust node, sedra-rusty | regions / functions | 55.1 % / 49.3 % |

**By area** (Go: statements, merged per code block; Rust: lines, summed per file from the llvm-cov JSON export)

| Area | Go (sedrad) | Rust (sedra-rusty) |
|---|---|---|
| Consensus processes (coinbase, difficulty, GHOSTDAG, pruning, ...) | 77.9 % | 82.1 % |
| Consensus pipeline (block and header validation) | (part of processes) | 90.8 % |
| Consensus utilities / core types | 84.4 % (utils), 93.5 % (model) | 77.3 % (`consensus/core`) |
| Proof of work | (part of utils) | 95.1 % |
| Script engine (txscript) | (part of utils) | 94.9 % |
| MuHash / Merkle / hashes | (part of utils) | 95.6 % / 96.0 % / 83.3 % |
| Mining (block templates, mempool) | 74.4 % | 80.4 % |
| P2P protocol flows | 68.1 % | 43.7 % (**protocol v5: 23.2 %**) |
| RPC | 53.1 % | 71.4 % (`rpc/core`) |
| Network infrastructure | 32.5 % | 63.1 % (`protocol/p2p`) |
| Wallet | 19.4 % (`cmd/sedrawallet`) | 26.1 % (`wallet/core`), 53.8 % (`wallet/keys`) |
| Addresses (bech32) | 100 % (`util/bech32`) | 62.3 % (`crypto/addresses`) |
| Sedra-specific: subsidy (`coinbase.rs`) | — | 79.7 % |
| Sedra-specific: difficulty (`difficulty.rs`) | — | 89.9 % |

The two codebases are organised differently, so the area rows are an approximate mapping, not a like-for-like
comparison.

## Findings

1. **The consensus core is well covered in both nodes (Verified):** 78-95 % in the areas that decide which blocks are
   valid. That is where it matters most.
2. **The P2P protocol v5 code in the Rust node is the least tested part that matters (Verified: 23.2 %).** It is exactly
   the code the Rust node needs to talk to Sedra's Go nodes, and Kaspa removed it in later releases. Milestones M4
   (handshake) and M5 (full sync against a local Go node) exercise it for real; they are the right next priority after
   the offline milestones. (Inferred)
3. **Wallets are weakly covered in both (Verified: 19-54 %).** Not consensus-relevant for Step 1.
4. **An inherited bug in Sedra's Go node (Verified).** `go vet` in Go 1.26 rejects
   `domain/consensus/datastructures/headersselectedchainstore/headers_selected_chain_staging_shard.go:85`:
   `isStaged()` checks `len(addedByIndex) != 0` twice and never `len(removedByIndex) != 0`. The same mistake is in
   Kaspa's Go node v0.12.15, which Sedra copied; Kaspa fixed it later (current kaspad has `removedByIndex`). Effect:
   pending changes that consist **only** of index removals are not committed. Those removals normally come together with
   other changes, so the practical impact is probably small (Inferred), but it is a real defect in the Go node.
   *Update 2026-11-06:* checked in the code; it has no practical effect (question Q36). The only write to
   `removedByIndex` is always paired with a write to `removedByHash`, so `isStaged()` still returns true. The Rust
   node has its own implementation and is not affected. Because of this, the Go figures above were measured with
   `-vet=off`; with the check on, that one package fails to build for tests and the total is otherwise unchanged
   (51.0 %).

## What this does NOT mean

- High coverage does not mean the code is correct, and low coverage does not mean it is wrong.
- The Rust figures do not include the browser (wasm) and PSKT wallet crates, which are excluded from the test run.
- Nothing here has been tested against the live Sedra network.

## Reproducing

- Go: `go test -vet=off -coverpkg=./... -coverprofile=go.out ./...` then `go tool cover -func=go.out` in sedrad at
  `4a1153d`.
- Rust: `cargo llvm-cov --release --no-fail-fast --workspace --exclude kaspa-wasm --exclude kaspa-wallet-pskt` in
  sedra-rusty at `e481e23f`.
