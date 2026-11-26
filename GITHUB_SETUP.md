# GitHub repository

The public repository is available at:

https://github.com/Ritweek17/file-integrity-verification

The repository is owned by the GitHub account `Ritweek17`. The default branch is `main`.

## Clone

```bash
git clone https://github.com/Ritweek17/file-integrity-verification.git
cd file-integrity-verification
```

## Run

```bash
python3 src/integrity_checker.py init --target sample_data --baseline examples/baseline.json
python3 src/integrity_checker.py verify --target sample_data --baseline examples/baseline.json --report examples/unchanged_report.json
python3 -m unittest discover -s tests -v
```

## Repository layout

- `src/` — application source code
- `tests/` — automated tests
- `sample_data/` — harmless sample files
- `examples/` — baseline and JSON reports
- `evidence/` — command history and observed test outputs
- `docs/` — project report

## Updating the repository

The project uses the `main` branch. Clone the repository, make a focused change, run the tests, and commit the change with a descriptive message before pushing.

```bash
git add .
git commit -m "fix: describe the change"
git push origin main
```
