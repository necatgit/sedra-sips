# AGENTS.md: working rules for sedra-sips

Rules for people and AI agents working in this repository.

## What this repository is

`necatgit/sedra-sips` (public): the Sedra Improvement Proposals published for public comment, with the research notes
they cite (`research/`). Comments come in as issues here.

## One fact, one source

- **The SIPs are owned by the project repository** `necatgit/sedra-project` (`proposals/SIP-*.md`). Change the text
  there first, then copy the change here in the same session. The two copies must say the same in substance; this
  copy only leaves out links to notes that are not public and points discussion to this repository's issues.
- The notes in `research/` are copies of the project's `research/` notes and follow the same rule: change them there
  first.
- The status column in `README.md` mirrors each SIP's own Status line.
- Questions are cited by their ID in the project's `QUESTIONS.md` ("Q51"); no separate list here.
- Decisions taken after comments are recorded in the SIP with their date. Corrections get a dated note, never a
  silent rewrite. Never write "Verified" or "done" before the check ran.
- When a fact changes, search this repository, `sedra-project` and `sedra-rusty` for the old wording and fix every
  live copy. The shared rule is described in `sedra-project`'s `AGENTS.md`, section "Keeping documentation current".

## Public identity and privacy

- Everything is published as **Nec** (GitHub `necatgit`) with the GitHub noreply address; check `git config user.name`
  and `git config user.email` before every commit, and `git diff --cached` for personal data.
- Never write a real name, private email, wallet address, holdings detail beyond the README disclosure, or anything
  from private notes or correspondence into this repository.
- Substance changes to a SIP (rules, activation, emission, treasury stance) are published only after Nec's OK.

## Commits and pushes

Branch `main`; push from WSL (`git push origin main` in the WSL checkout or via `wsl -d Ubuntu-24.04`). Never silence
push errors. Never force-push, rewrite history or delete branches without explicit approval.
