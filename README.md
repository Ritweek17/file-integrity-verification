# File-Integrity Verification

**Student:** Ritweek Dubey  
**Institution:** ABES Engineering College  
**Programme:** B.Tech, Computer Science and Engineering — Second Year  
**Domain:** Cyber Analytics  
**Selected assignment:** Project 14 — File-Integrity Verification

A Python command-line utility that creates a SHA-256 baseline for a local folder and compares later scans. It classifies files as `UNCHANGED`, `MODIFIED`, `ADDED`, or `DELETED`, then saves a JSON report.

## Repository structure

```text
.
├── src/            # SHA-256 inventory and verification CLI
├── tests/          # Automated unit tests
├── sample_data/    # Harmless demonstration files
├── examples/       # Reference baselines and JSON reports
├── evidence/       # Command history and test results
├── docs/           # Project report
├── README.md
├── GITHUB_SETUP.md
├── LICENSE
└── requirements.txt
```

## Requirements

- Python 3.9 or newer
- Python standard library only; no third-party packages required
- Use only on folders you own or are authorised to monitor

## Run

From the repository root:

```bash
python3 src/integrity_checker.py init --target sample_data --baseline examples/baseline.json
python3 src/integrity_checker.py verify --target sample_data --baseline examples/baseline.json --report examples/unchanged_report.json
```

The included sample folder matches its baseline: three files are unchanged and no differences are detected.

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

Five tests cover unchanged, modified, added, and deleted files, as well as JSON report validity.

## Controlled demonstration

The recorded controlled scenario contains one modified file, one added file, one deleted file, and one unchanged file. The original `sample_data/` folder remains unchanged. See `evidence/command_history.txt` and `examples/controlled_change_report.json`.

An exit code of `1` means differences were found; it does not, by itself, prove malicious activity.

## Documentation

Read the report in [docs/Project_Report.md](docs/Project_Report.md). The repository guide is in [GITHUB_SETUP.md](GITHUB_SETUP.md).

## Student and repository

- GitHub profile: https://github.com/Ritweek17
- Project repository: https://github.com/Ritweek17/file-integrity-verification
