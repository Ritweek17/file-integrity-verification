# File-Integrity Verification

**Student:** Ritweek Dubey  
**Institution:** ABES Engineering College  
**Programme:** B.Tech, Computer Science and Engineering — Second Year  
**Domain:** Cyber Analytics

A Python command-line tool that creates a SHA-256 baseline for a local directory and compares later scans. It reports files as `UNCHANGED`, `MODIFIED`, `ADDED`, or `DELETED`.

## Requirements
- Python 3.9 or newer
- Standard library only; no third-party packages required

## Run

```bash
python3 src/integrity_checker.py init --target sample_data --baseline examples/baseline.json
python3 src/integrity_checker.py verify --target sample_data --baseline examples/baseline.json --report examples/verification_report.json
```

Run the tests with:

```bash
python3 -m unittest discover -s tests -v
```

The included sample folder is designed to match its baseline. Controlled-change evidence in `evidence/` documents a separate demonstration with one modified, one added, and one deleted file.

## Structure

```text
src/          CLI implementation
 tests/       automated tests
sample_data/  harmless sample files
examples/     reference baselines and reports
evidence/     terminal captures and test results
assets/       project illustrations
 docs/        academic report (PDF and DOCX)
```

## Interpretation
A verification exit code of `1` means differences were found; it does not, by itself, prove malicious activity. Protect the baseline separately from the monitored directory.

## Student
- GitHub: https://github.com/Ritweek17
- Repository: https://github.com/Ritweek17/file-integrity-verification
