# Sedra Improvement Proposals (SIPs)

Proposals for changes to the **Sedra (SDR)** network, published for public comment.

| SIP | Title | Status |
|---|---|---|
| [SIP-0001](SIP-0001-merged-mining.md) | Merged mining of Sedra with Kaspa | Draft, open for public comment |
| [SIP-0002](SIP-0002-network-resilience.md) | Network resilience (staged plan, no consensus change) | Draft, open for public comment (since 2026-11-25) |
| [SIP-0003](SIP-0003-public-testnet.md) | A public testnet for merged mining | Draft, open for public comment |

## How to comment

Open an [issue](https://github.com/necatgit/sedra-sips/issues) or comment on an existing one. Questions, objections
and corrections are all welcome. Please name the section you refer to (for example "SIP-0001 §4.3"). Decisions taken
after comments are recorded in the SIP itself with their date.

A draft is not a decision. Nothing in these proposals is scheduled, and SIP-0001 is not agreed with the Sedra team; for SIP-0003 the
team agreed on 2026-11-24 to run the testnet as proposed.

## Who

Written by **Nec** ([@necatgit](https://github.com/necatgit)), who also runs the PuddlePool mining pool.

**Disclosure:** Nec holds about 250M SDR (roughly 1% of circulating supply) and has a direct interest in Sedra
succeeding. None of the SIPs creates new coins for Nec: no premine, no developer fee. Nec will not sell SDR from the public
announcement of the activation date until 30 days after activation.

This work is done together with an AI, and that is stated openly: **Claude** (by Anthropic, used through Claude Code)
does most of the research, code and writing; Nec sets the goals, makes the decisions and reviews the results.

The research behind SIP-0001 is in [research/](research/). The project's roadmap, all research (including the review of
the v2.0.0 relaunch), questions and progress updates are in [necatgit/sedra-project](https://github.com/necatgit/sedra-project)
(public since 2026-11-21); the Rust node code is in [necatgit/sedra-rusty](https://github.com/necatgit/sedra-rusty).
