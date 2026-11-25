# SIP-0002: Network resilience

| | |
|---|---|
| Status | **Draft, open for public comment** (since 2026-11-25); no code yet. Was an idea from 2026-11-07 to 2026-11-25. Stage 4 dropped by Nec on 2026-11-25 |
| Author | Nec |
| Discussion | [Issues of this repository](https://github.com/necatgit/sedra-sips/issues); tracking issue [necatgit/sedra-project#30](https://github.com/necatgit/sedra-project/issues/30) |
| Created | 2026-11-07 |
| Consensus change | **None.** Every stage works with old and new nodes side by side |

## Goal

Sedra's own roadmap says (stage "Built to last"): *"Many people run nodes, not only the team. … If any single server
goes down, ours included, Sedra stays up."* This proposal is a staged plan to make that true for the node network,
smallest and cheapest stage first.

## Where Sedra stands (re-measured 2026-11-25)

Evidence for every line: [research/archive/2026-11-25-0030-network-measurements.md](https://github.com/necatgit/sedra-project/blob/main/research/archive/2026-11-25-0030-network-measurements.md).

- **Reachable nodes (Verified, 2026-11-25 18:30 UTC):** the network map on the test VM (TCP probe of every address
  its Go node knows, every six hours) found **3** nodes that accept P2P connections: the two fallback peers built into
  sedrad and this project's public Rust node. Since 2026-11-14 the count has been between 3 and 5; on 2026-11-25
  00:30 UTC a fourth, outside node was still reachable, from 06:30 UTC it was not.
- **DNS seeders (Verified, 2026-11-25 21:57 UTC, same answer from 1.1.1.1 and 8.8.8.8):** `sedra-seed-1` returns one
  fixed address (TTL 3600), which is one of the two fallback peers. `sedra-seed-2` and `sedra-seed-3` return **no
  address**. None of the three is a crawling seeder that hands out many current nodes; they are fixed DNS records.
- **Fallback peers (Verified):** the Go node has two hard-coded fallback peers (`169.58.126.141`, `169.58.111.191`,
  sedrad `domain/dagconfig/params.go:266-268@4a1153d8`), used only when the operator gives no `--addpeer` or
  `--connect`. Both are in the same /17 network of one hosting provider (RIPE RDAP, 2026-11-25). The Rust node has
  **no** fallback peers (sedra-rusty `dev@00757c4e`), only the three seeders. Whether the fallback peers serve a
  complete sync is still being checked by the Sedra team (Q5, result promised by 2026-12-14).
- **So, today (Inferred from the three points above):** a brand-new Rust node without `--addpeer` gets exactly one
  address from DNS; a brand-new Go node gets two addresses, both at one provider. If those two machines are down,
  new nodes cannot join without someone giving them an address by hand.
- **This project's public node (Verified, 2026-11-25 21:58 UTC):** it still gets inbound peers (6 connected at that
  moment, 12 different outside addresses since 2026-11-18 22:00 UTC, 4 in the last 24 hours). Outbound it reaches
  only three outside nodes, because there are no more reachable ones.
- **Address book (Verified in both code bases):** each node keeps up to 4096 addresses with one number per address,
  the count of failed connection attempts. There is no "last seen", no uptime and no preferred peers. An address is
  **deleted after 4 failed attempts** (Go `addressmanager.go:20`) or **more than 3** (Rust
  `components/addressmanager/src/lib.rs:28`). Outbound peers (8 by default) are chosen at random, weighted by that
  count. DNS seeders are asked when the address book cannot fill the 8 slots.
- **Consequence (Inferred):** a public node that is down for a few hours is deleted from the address books of the
  nodes that tried to reach it, and is found again only through new gossip or the seeders. With only three reachable
  nodes, one outage can leave nodes with no peers, mining on an isolated chain until connections return.

Earlier measurements, kept as published: on 2026-11-07 a long-running pool node had connected to only three outside
nodes in 60 hours, two of them the fallback peers. On 2026-11-15 18:31 UTC the network map knew 1,001 addresses and
4 accepted a connection. When the public node started on 2026-11-14, two of the three DNS seeders returned no
addresses (release checklist step 7); they still return none on 2026-11-25.

What stays true from the first version: there is no "master node" in the code; every node validates every block and
all nodes are equal (same design as Kaspa). Nodes exchange up to 1000 known addresses when they connect (sedrad
`app/protocol/flows/v5/addressexchange/`, Rust `protocol/flows/src/v5/address.rs`). Nodes behind a router without an
open P2P port can connect out, but nobody can connect to them. Opening a Go node's P2P port is currently risky
([research 0007](https://github.com/necatgit/sedra-project/blob/main/research/0007-go-node-security.md), Q37); the Rust node does not have the sync-serving freeze (Q38).

## The plan in four stages

| Stage | What | Consensus change | Node release needed | Earliest start |
|---|---|---|---|---|
| 1 | A second independent public node + seeder records + a guide for operators | No | No | After the testnet report (~2026-12-21) |
| 2 | More seeders and fallback peers in the node code, with listing rules | No | Yes (both nodes) | When Stage 1 runs and there are operators |
| 3 | Peer memory ("parents and children") in the Rust node | No | Yes (Rust node) | Design now; code after the testnet |
| 4 | Opt-in "I am alive" announcements | — | — | **Dropped** (Nec, 2026-11-25; see Stage 4) |

No dates are promised. "Earliest start" is the first moment the stage can begin, not a plan to finish.

### Stage 1: a second independent node, seeder records, a guide (operations only)

**What.**

1. **The rented VPS becomes an independent public mainnet node** after the public testnet. It runs the testnet seed
   until the testnet report (~2026-12-21, [testnet/HOSTING.md](https://github.com/necatgit/sedra-project/blob/main/testnet/HOSTING.md)); after that it also runs the
   released Rust node (`sedra-rusty` mainnet release, currently 0.1.1) as a P2P node:
   - P2P **TCP 22111 open**, RPC 22110 on localhost only, no mining (the host's terms forbid it), no wallet, no keys.
   - `--utxoindex` off unless needed; resources measured 2026-11-24: 3.0 GB data, 2.2 GiB memory, which fits the VPS
     (4 vCPU, 8 GB, 128 GB).
   - Monitoring: a check every 10 minutes that compares its block count with the home node and counts inbound peers;
     a public monthly line (uptime, inbound peers) in the dated updates.
   - Cost: none for the project; the VPS is already paid for 12 months by Nec (see HOSTING.md). Whether it stays after
     the minimum term is decided separately.
   - Different hardware, network and country from the home node and from the pool, so this is the first node of this
     project that is independent hardware, not only an independent node ([ROADMAP](https://github.com/necatgit/sedra-project/blob/main/ROADMAP.md) Phase 2 open item).
2. **Ask the Sedra team to put independent nodes into the seeder records.** `sedra-seed-2` and `sedra-seed-3` are
   empty. The team already accepted in principle (reply draft of 2026-11-23, letter item A11) to add this project's
   home Rust node as an extra peer after their check; this project sends the address. Stage 1 adds a second request:
   after the testnet, add the VPS node too. Proposed for the next version of the open-items letter, not sent yet.
   Goal: each of the three seeder names returns at least one working address, and not all of them at one operator.
3. **A short guide "Run a public Sedra node"** (appendix A below) that invites community operators, with an issue
   where an operator can say "my node is public" so it can be measured and later listed (Stage 2).

**What it fixes.** New nodes get more than one or two first contacts; one machine or one provider going down no
longer cuts new nodes off.

**Risks.** A public node is a target for connection floods (mitigated: the Rust node, firewall with only the needed
ports, no RPC exposed). Both of this project's nodes are run by one person, so they add independence from the team,
not independence from Nec; more operators are needed for that (Q40). The seeder records depend on the team acting
(A11 still open on 2026-11-25).

**Effort (Inferred).** VPS setup half a day (the hardening and the testnet node already exist); guide half a day;
monitoring a few hours. Ongoing: updates with each node release.

**Who acts.** Nec: decide the VPS role at the ~12-21 review, send the addresses. Claude: set-up, monitoring, guide.
Sedra team: add the records (A11 and the new item). Operators: run nodes.

**Success, measured.** (a) The network map shows at least 2 reachable nodes that are neither the team's nor on one
provider, for 30 days. (b) `sedra-seed-2` and `sedra-seed-3` each return at least one working address. (c) The VPS
node has inbound peers and at least 99 % uptime over 30 days.

### Stage 2: more seeders and fallback peers in the node code

**What.**

1. **Fallback peers in the Rust node**, the same mechanism as sedrad v1.1.0 (used only when the operator gives no
   `--addpeer`/`--connect`). Today the Rust node has none.
2. **A real crawling DNS seeder** run by someone other than the team, under its own domain, added as a fourth seeder
   name in both nodes. Upstream Kaspa has one (`kaspanet/dnsseeder`, Go); no Sedra version is public (checked
   2026-11-25), so it needs Sedra's network parameters (Inferred: a small fork).
3. **Listing rules**, written down before anything is listed:
   - the node runs a current release and has been reachable at least 95 % of the time for 30 days, measured by the
     network map from at least two places;
   - the operator is named publicly (a name or handle) with a contact, and promises four weeks' notice before shutting
     down;
   - at most one listed entry per operator and per hosting provider (network), so no single company or person can be
     the whole list;
   - for fallback peers: the node serves a complete sync (the Q5 check; the two current fallback peers are not added
     to the Rust node before the team's answer to Q5).
4. **How the list is updated.** The list is code, so it changes only with a node release: a pull request in
   `sedra-rusty` (and in sedrad when it gets a maintenance release) with the measurement evidence. An entry that has
   been unreachable for 30 days is removed in the next release. Seeder records (DNS) can change without a release.

**What it fixes.** The first contact no longer depends on one operator; a seeder returns current nodes instead of a
fixed address.

**Risks.** Listed nodes are trusted for the first contact, so a bad listed node could feed a new node only hostile
addresses (mitigated: several independent entries; the node keeps asking the seeders while it is short of peers).
Lists in released code go stale (mitigated: removal rule, plus seeders that update themselves).

**Effort (Inferred).** Rust fallback peers: about a day with tests. Seeder fork and hosting: a few days. Then a node
release.

**Who acts.** Operators (they must exist first, Q40). Nec: approve listings, release. The Sedra team: the same list in
sedrad's next maintenance release, and seeder DNS records.

**Success, measured.** A fresh node with one listed operator blocked still finds peers within 5 minutes (test on
devnet or testnet). At least 3 operators on at least 3 providers.

### Stage 3: peer memory ("parents and children") in the Rust node

Nec's idea: a node remembers the peers it had good, long connections with and goes back to them first after a
restart or an outage. **Parents** are peers this node connected *to* (outbound), **children** are peers that
connected *to it* (inbound). This is a P2P change only: no new messages, no consensus change, old and new nodes work
together. Planned for the Rust node only; the Go node keeps its current behaviour.

**Data stored** (a new, separate store in the node's database, so the existing address entries keep their format):

| Field | Meaning |
|---|---|
| address | IP and port |
| role | parent or child |
| first_seen, last_success | when the first and the latest successful connection happened (seconds) |
| connected_secs | total connected time, capped |
| sessions | number of successful connections |
| good | the peer delivered valid blocks during the connection and was never banned |

**Who is remembered.**
- Parents: outbound peers that stayed connected at least 1 hour and delivered valid blocks.
- Children: inbound peers only if they are reachable: the address they announce accepts a connection from us (one
  test connection, at most once a day per child). Children behind a router are not remembered; they cannot be
  reached anyway.
- At most 8 remembered peers in total (4 parents, 4 children), at most one per network prefix (the Rust node already
  groups addresses by prefix for its random choice).
- A record expires 14 days after the last success. A ban, or invalid data from the peer, deletes it at once.

**Start-up order.**
1. Up to 2 **anchors**: the last two good parents, tried first (as Bitcoin Core does with `anchors.dat`, 2 anchors).
2. The other remembered peers, ahead of the random choice, filling at most **half** of the 8 outbound slots.
3. The rest of the address book, chosen at random as today.
4. DNS seeders and fallback peers, as today, when the node is still short of peers.

**Not forgetting good peers.** Remembered peers are not deleted from the address book after 3 failed attempts;
they are retried with a growing pause (1 min, 2, 4 … up to 1 hour) until their record expires. This is the change that
helps most with Sedra's few nodes: a public node that is down for a day is still known when it returns.

**Limits against eclipse attacks** (an attacker trying to be all of a node's peers):
- remembered peers take at most half of the outbound slots; the other half is always chosen at random;
- one remembered peer per network prefix, so many addresses in one network count as one;
- an inbound peer cannot make itself a child without being reachable and delivering valid blocks, and inbound peers
  never become anchors;
- a `--reset-peer-memory` switch (like upstream's proposed `--reset-address-stores`, rusty-kaspa #812) and a log line at
  start that lists the anchors used.

**Tests.** Unit: store round-trip, expiry, prefix limit, start-up order, no deletion of remembered peers. Integration
(devnet, 3 to 5 nodes): after a restart with seeders blocked the node reconnects to its parents first; with all
parents down it falls back to the address book and seeders; a node returning after 24 hours down gets its children
back; an attacker with 100 addresses in one network gets at most one remembered slot; mixed old and new nodes stay in
sync. Then on a test network before any mainnet release.

**Upstream friendly? (Inferred: yes, if kept separate.)** Upstream rusty-kaspa (`master@68bd2e91`, 2026-11-23) still
stores only the failure count. Its open pull request #796 (Perigee peer selection, not merged, no reviews, last updated
2026-05-06) adds a separate persisted list of ranked peers and a "priority list" in front of the random choice
(`iterate_prioritized_random_addresses(priorities, exceptions)`). Stage 3 should use the same shape (a separate store
and a priority list), so that it does not collide with #796 and could be offered upstream as a small "anchors and
peer memory" change. Before writing code, open a discussion upstream that points to #796 and #812. Perigee itself
(choosing peers by block delivery speed) is a different goal and not part of this SIP.

**What it fixes.** Restarts and short outages no longer depend on the seeders; good public nodes are not forgotten.

**Risks.** Remembered peers make a node's connections more predictable (mitigated by the limits above). A bug in
connection handling can isolate a node (mitigated by tests, test network first, and the switch to turn it off).

**Effort (Inferred).** About 500 to 900 lines with tests, one to two weeks of work, plus a test network run.

**Who acts.** Claude writes the code, Nec reviews and releases; upstream maintainers if it is offered upstream.

**Success, measured.** On devnet/testnet: after a restart with all seeders blocked, at least 4 outbound peers within 2
minutes when any remembered peer is up. A node that was down 24 hours has inbound peers again within 1 hour of
returning.

### Stage 4: opt-in "I am alive" announcements: dropped

The idea (Nec, 2026-11-11): an operator lets the node report that it is alive and reachable, so others can find it;
off by default, documented, the operator's choice because it reveals the IP address.

**Analysis.** Whoever keeps such a list must check every announcement by connecting back to the node, and the list
must not be one central server. A crawling DNS seeder (Stage 2) does exactly that: it connects to nodes, keeps the
reachable ones and hands them out, and several independent seeders avoid one central point. Nodes already announce
their own reachable address to their peers through gossip (`--externalip`). An announcement only adds something for
a node that has no connection at all, and that node is helped by Stage 2 and Stage 1's guide.

**Decision (Nec, 2026-11-25): dropped** as a separate mechanism. Its goal is covered by: crawling seeders (Stage 2), operators who
say "my node is public" in an issue (Stage 1 guide; checked by the network map before any listing), and peer memory
(Stage 3). This answers Q53. If Stages 1 to 3 do not bring enough reachable nodes, this can be
revisited.

## The first contact cannot be avoided

A brand-new node has no memory, so its very first peer has to come from somewhere: the DNS seeders, the fallback peers,
or an address the operator gives by hand (`--addpeer` / `--connect`). Stage 3 makes sure a node needs that only once;
Stages 1 and 2 make sure that first contact depends on more than a few servers of one operator.

Easy installation (release binaries with checksums, then packages and a Docker image) also helps more people run
nodes. Release binaries with checksums exist since v0.1.0; packages and a Docker image are not planned yet.

## What this does NOT mean

- No consensus rules, no coins, no fork. Every stage is node software or operations; old and new nodes keep working
  together.
- A draft is not a decision. No stage has a date. Stage 1 needs Nec's decision on the VPS role at the testnet review and
  the Sedra team's action on the seeder records; neither has happened (2026-11-25).
- More public nodes run by this project make Sedra less dependent on the team's servers, not on one person: two of the
  planned nodes are Nec's. Real resilience needs other operators (Q40).
- The fallback peers are not said to be bad. Their sync completeness is an open question (Q5) that the team promised to
  answer.
- Stage 3 has not been designed together with the rusty-kaspa maintainers; "upstream friendly" is this project's
  reading of upstream's code and open pull requests, not their agreement.

## Open questions

- Who besides this project would run public nodes and seeders? (Q40)
- Do the fallback peers serve a complete sync? (Q5, by 2026-12-14)
- Who runs the seeders and fallback peers, and who can edit the seeder records? (Q7; service map promised by 2026-11-30)

## Appendix A: Run a public Sedra node (draft guide)

A public node is a normal node that others can connect to. It needs no coins, no wallet and no mining.

1. **Machine.** Linux x86_64, 2 or more cores, 4 GB RAM or more, 20 GB free disk (measured use 2026-11-24: 3.0 GB
   data, 2.2 GiB RAM), a stable connection. A rented server or a home machine with a port forward both work.
2. **Download and check.** Take the latest mainnet release from
   [necatgit/sedra-rusty releases](https://github.com/necatgit/sedra-rusty/releases) (not a `testnet` pre-release) and
   check it against `SHA256SUMS`: `sha256sum -c SHA256SUMS --ignore-missing`.
3. **Run.** `./kaspad --yes` (add `--utxoindex` only if you also serve a wallet, pool or explorer). Run it as a service
   (for example a systemd unit with `Restart=always`) under its own user.
4. **Open the P2P port.** Allow and forward **TCP 22111** to the node. **Never expose 22110 (RPC)** to the internet.
   If the node is behind a router, give it your public address with `--externalip=<your-ip>:22111` so it can tell
   others where to find it.
5. **Check.** After an hour the log should show lines "Connected to incoming peer". No incoming peers means the port is
   not reachable.
6. **Keep it updated.** Follow the releases; a public node should run the current one.
7. **Tell us (optional).** Open an issue in [necatgit/sedra-project](https://github.com/necatgit/sedra-project/issues)
   with the address and how long you plan to run it. It will be measured by the network map; listing in the node code
   follows the Stage 2 rules. Publishing your node's address is your choice.

Use the Rust node for a public node. The Go node `sedrad` v2.0.0 has known problems with an open P2P port ([research
0007](https://github.com/necatgit/sedra-project/blob/main/research/0007-go-node-security.md), Q37).
