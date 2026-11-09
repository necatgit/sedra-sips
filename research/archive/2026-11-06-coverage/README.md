# Coverage raw reports (2026-11-06)

Measured on the test VM (Ubuntu 26.04). Reviewed summary: [../../0005-test-coverage.md](../../0005-test-coverage.md).

| File | Content |
|---|---|
| `summary.txt` | Run log: versions, commits, exit codes |
| `go-per-package.txt` | `go test -cover ./...` with `go vet` on: one package fails to build because of the inherited `isStaged()` bug |
| `go-per-package-novet.txt` | The same with `-vet=off` |
| `go-func-novet.txt` | `go tool cover -func` for `-coverpkg=./...`: per function and the total (51.0 %) |
| `rust-file-summary.txt` | `cargo llvm-cov report --summary-only`: per file and TOTAL (lines 57.58 %) |

The 41 MB llvm-cov JSON export used for the per-area figures stays on the test VM
(`/data/logs/coverage-20261106T063841Z/rust-cov.json`); it can be regenerated with the command in the summary.
