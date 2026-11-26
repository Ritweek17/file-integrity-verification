# System architecture

## Components

| Component | Responsibility |
|---|---|
| `src/integrity_checker.py` | CLI parsing, hashing, inventory creation, baseline validation, comparison, and JSON output |
| `sample_data/` | Harmless example files used by the documented run |
| `examples/` | Reference baseline and verification reports |
| `tests/` | Isolated unit tests using temporary directories |
| `evidence/` | Recorded command history, result summaries, and terminal-style evidence |
| `assets/` | Workflow illustration |
| `docs/` | Six-section academic project report |

## Data flow

1. The operator selects a target directory and baseline output path.
2. The scanner walks the folder recursively in sorted path order.
3. Each regular file is read in 1 MiB chunks and hashed with SHA-256.
4. The baseline stores the relative path, size, digest, algorithm, schema version, and UTC creation time.
5. During verification, a new inventory is compared with the saved baseline.
6. Each path is classified as unchanged, modified, added, or deleted.
7. The program writes a JSON report and returns an exit status suitable for scripts.

## Design safeguards

- Baselines and reports are required to be outside the monitored target directory.
- Symbolic links are skipped instead of following them.
- File content is streamed in chunks to avoid reading large files into memory.
- The utility has no network functionality and uses the Python standard library.
- A detected difference is reported for human review; the program does not infer intent or attribute the change to a user.

## Exit status

| Code | Meaning |
|---:|---|
| 0 | Baseline creation succeeded, or verification found no differences |
| 1 | Verification completed and found one or more differences |
| 2 | Invalid input or operational error |

