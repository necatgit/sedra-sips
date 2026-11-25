# SIP-0003: A public testnet for merged mining

| | |
|---|---|
| Status | **Draft, open for public comment** (since 2026-11-17). Q46-Q50 decided by Nec 2026-11-10; Q51 and Q52 asked to the Sedra team on 2026-11-10, **open**: the team's reply of 2026-11-17 (a draft for team approval) accepts the two-week minimum and the criteria as a starting checklist, subject to agreement before launch (Q51), and promises Q52 by 2026-12-14. Not final, not scheduled, not agreed with the Sedra team |
| Author | Nec |
| Created | 2026-11-10 |
| Type | Process (no consensus change of its own) |
| Discussion | [Issues of this repository](https://github.com/necatgit/sedra-sips/issues) |
| Depends on | [SIP-0001](SIP-0001-merged-mining.md) (the rules being tested), [sedra-rusty](https://github.com/necatgit/sedra-rusty) v0.1.0 (2026-11-14) |

Labels as in SIP-0001: **Verified** (checked in code or data), **Inferred** (reasoned, could be wrong), **Unknown**.
Choices marked **Proposed** are this draft's recommendation and wait for a decision.

## 1. Summary

Before merged mining can be activated on Sedra mainnet, it runs on a public test network that anyone can join: their
own node, their own miner, their own pool. The testnet shows in the open that the rules work, that the switch-over at
activation works, and what happens to nodes that did not upgrade. Its results are the basis for choosing a mainnet
activation date together with the Sedra team.

## 2. Why

- **Sedra's condition.** The Sedra team has made its support depend on a public testnet, a written proposal
  (SIP-0001, done) and an activation date announced well in advance (SIP-0001 §10, Q3).
- **Evidence others can check.** Everything so far ran on our machines (a private devnet). A public testnet lets
  pools, the exchange and the Sedra team try it themselves instead of trusting our reports.
- **The risky moment is the switch, not the steady state.** Activation, the self-parent ban two days before it, and
  old nodes falling off are exactly what a local test cannot show convincingly.

## 3. What the testnet has to show (Proposed exit criteria)

1. Activation at the announced DAA score without a split among upgraded nodes; the self-parent ban starts
   `2 × finality_depth` earlier, as specified (SIP-0001 §4.5, §5).
2. Merged-mined and natively mined blocks side by side, accepted by every upgraded node.
3. Old nodes behave as predicted: before activation they follow the chain, after it they reject merged-mined blocks
   and stop following (only possible if Go nodes can join, see 4.2).
4. A node started from scratch after activation syncs, including the pruning proof with merged-mined headers.
5. A pool pays both coins correctly (Kaspa testnet coins and Sedra testnet coins) and per-miner addresses work.
6. Wallets: the Go `sedrawallet` sends and receives (tested on devnet 2026-11-10, repeated here in public).
7. At least one participant outside this project runs a node or mines, and reports what they saw.
8. At least two weeks after activation without a consensus failure. Every problem found is fixed and re-tested.
9. *Proposed addition (2026-11-25, Nec), not part of the eight criteria the Sedra team accepted:* one Kaspa
   testnet-10 coinbase carries both a ZKas and a Sedra commitment, as the mainnet pool would after activation. Both
   auxiliary chains accept blocks from the same parent work, neither commitment disturbs the other, and no share is
   credited twice. ZKas runs as a private test chain for the testnet pool only. Reason: this combination was never
   tested against real nodes (SIP-0001 §9, correction of 2026-11-25).

## 4. Decisions

### 4.1 Which Kaspa network is the parent? (Q46)

Merged mining needs Kaspa blocks whose coinbase carries the Sedra commitment. Someone has to mine those Kaspa blocks.

| Option | For | Against |
|---|---|---|
| **A. Kaspa's public testnet** (testnet-10) | Real Kaspa software and a real, independent network; nothing to build on the Kaspa side; Kaspa upgrades its testnet before mainnet, so header changes reach us early (SIP-0001 §4.6) | Not under our control (it can be reset or upgraded mid-test); testnet coins are worthless, so the hashrate depends on who mines it; its current block rate, version and difficulty are **Unknown** here and must be checked before deciding |
| **B. Our own Kaspa test network** | Full control, CPU mining is enough, cheap; already done privately (devnet) | Proves little to outsiders: we would control both chains; everyone who joins must also run our Kaspa nodes |
| **C. Kaspa mainnet** (a Sedra testnet merged-mined by real Kaspa miners) | Real hashrate and real miners, who keep earning KAS while testing: the strongest evidence | A mainnet pool has to carry a testnet commitment, which touches a production pool; a mistake there costs real money; only miners of that one pool take part |

**Decided 2026-11-10 (Q46):** A as the testnet. C later and optionally, as a short dress rehearsal on PuddlePool only, after A has
passed and with Nec's explicit go. B stays our private test bench.

### 4.2 Which Sedra test chain? (Q47)

| Option | For | Against |
|---|---|---|
| **A. The testnet already in the code** (`testnet-10`, `sedratest:` addresses; same genesis in sedrad and sedra-rusty, **Verified**) | Unchanged Go `sedrad` v2.0.0 can join with `--testnet`, so we can show in public what happens to nodes that did not upgrade (criterion 3) | Its genesis is Kaspa's old testnet genesis (payload "kaspa-testnet", **Verified**); whether its rules match mainnet's v2.0.0 rules in Go and Rust alike is **Unknown** and must be checked first; it has no seeders, and whether anyone runs it is **Unknown** (Q52, asked to the Sedra team, open) |
| **B. A new test chain with its own genesis** | Clean start under a clear name; no surprises from old data | Go nodes cannot join without a modified build, so criterion 3 cannot be shown with unmodified software |
| **C. A copy of mainnet's state** | Realistic balances and history | Complex (a genesis from a snapshot), and it copies real balances into a test network: not worth it |

**Decided 2026-11-10 (Q47):** A, if a parity check (Go and Rust on the existing testnet with the same rules) passes; otherwise B.
Whatever the chain, its parameters stay those of mainnet (block rate, finality depth, rewards) so the timing of the
ban window and the activation is tested as it will happen.

### 4.3 When does merged mining activate on the testnet? (Q48)

| Option | For | Against |
|---|---|---|
| **A. From the first block** | Simple, merged mining from day one | The switch-over, the ban window and old nodes falling off are never tested |
| **B. After a native phase** (e.g. activation a few days after launch, announced in advance) | Tests exactly the mainnet sequence: announcement, upgrade, ban start, activation | The testnet takes a few days longer |

**Decided 2026-11-10 (Q48):** B, with the activation score announced at launch, the same way it would be announced on
mainnet. The announcement should come from the Sedra team if they are willing (asked together with Q51, open).

### 4.4 Who runs the infrastructure? (Q49)

Needed: at least two nodes reachable from the internet, a stratum pool that merge-mines KAS-testnet and SDR-testnet, a
faucet so that people without miners get test coins, and a way to look at blocks (an explorer, or at least a status
page).

| Option | For | Against |
|---|---|---|
| **A. This project runs all of it** | Fast, no dependencies | One operator, one host: a single point of failure; less convincing |
| **B. This project starts it, others join** (Sedra team, pools, anyone) | More realistic and independent; others gain experience before mainnet | Depends on others' time; coordination |

**Decided 2026-11-10 (Q49):** B. This project provides the first nodes, the pool (a separate Miningcore instance, never the production
pool), the faucet and a status page, and invites the Sedra team, the known SDR pools (SIP-0001 §10, Q21) and the exchange to run a
node or a pool. A full explorer is optional; a status page with recent blocks may be enough.

### 4.5 How do outsiders join? (Q50)

- **Node:** a testnet release of sedra-rusty, built and verified like v0.1.0
  ([`docs/RELEASE.md`](https://github.com/necatgit/sedra-rusty/blob/main/docs/RELEASE.md)), with a one-page
  guide: download, verify, start with `--testnet`.
- **Miners:** point a Kaspa miner or ASIC at the testnet pool with a Kaspa testnet address and a Sedra testnet address
  in the login (as on the devnet run).
- **Pools:** the Miningcore changes as a public reference (to be published), with the configuration used on the testnet.
- **Reports:** GitHub issues in a public repository; a community channel only if the Sedra team wants one.

**Decided 2026-11-10 (Q50):** as above. Open: whether the testnet guide lives in the Sedra team's channels as well (their decision).

### 4.6 How long, and what counts as passed? (Q51)

**Proposed to the Sedra team (Q51, Nec 2026-11-10):** at least two weeks after activation, with the exit criteria of
section 3, as the starting point; the Sedra team may change the duration and the criteria, since they set the condition. The results go into a dated
report; the mainnet activation date is chosen with the Sedra team only after that report (SIP-0001 §5, Q33). A serious
problem means fix, new testnet release and, if needed, a reset and a new activation on the testnet.

**Open:** no answer from the Sedra team yet (as of 2026-11-16).

## 5. Rough timeline (Inferred, depends on the decisions)

| Step | Earliest |
|---|---|
| sedra-rusty v0.1.0 (step 1, no merged mining) | 2026-11-14 |
| Decisions Q46-Q51; parity check of the existing testnet (4.2) | the week after |
| Testnet release, nodes, pool, faucet, guide | about one to two weeks later |
| Launch, then activation a few days later | |
| Two weeks of running after activation, report | roughly mid to late December 2026 |

## 6. Costs and risks

- **Machines:** at least one more VM for testnet nodes and pool (all pool VMs share one host today, so "two nodes" on
  it are not independent; a second location would be better). A Kaspa testnet node needs disk space (**Unknown** how
  much; to be measured).
- **Production stays separate:** the testnet pool, nodes and wallets never share a machine role, database or wallet
  with the production pool. Option C in 4.1 is the only exception and needs its own decision.
- **Attention:** a public testnet invites people to break it. That is the point, but reports need answers.

## 7. Open questions

The IDs in brackets refer to the project's question list. Comments on any of them are welcome in the issues.

1. ~~Which Kaspa network is the parent?~~ Decided 2026-11-10 (Q46): Kaspa's public testnet (4.1).
2. ~~Which Sedra test chain?~~ Decided 2026-11-10 (Q47): the existing `testnet-10` if the parity check passes,
   otherwise a new one (4.2).
3. ~~When does merged mining activate on the testnet?~~ Decided 2026-11-10 (Q48): after a native phase, announced at
   launch (4.3).
4. ~~Who runs the infrastructure?~~ Decided 2026-11-10 (Q49): this project starts it, others are invited (4.4).
5. ~~How do outsiders join?~~ Decided 2026-11-10 (Q50): release, guide, pool, issues (4.5).
6. How long does the testnet run and what counts as passed? (Q51) Proposed in 4.6; asked to the Sedra team, open.
7. Does anyone run Sedra's existing testnet, and do its rules match mainnet's v2.0.0 rules? (Q52) Asked to the Sedra
   team, open; the rules part is also checked by the parity check (4.2).

## Disclosure

Nec holds about 250M SDR (roughly 1% of circulating supply) and has a direct interest in Sedra succeeding. The
testnet itself creates nothing of value for anyone, Nec included.

## What this does NOT mean

- It does not schedule merged mining on mainnet. The mainnet date comes after the testnet, agreed with the Sedra team.
- It does not mean the Sedra team or any pool has agreed to take part.
- Testnet coins have no value and never will.
