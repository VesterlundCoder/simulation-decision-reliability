# Simulation Decision Reliability

Manuscript: **Assessing Decision Reliability in Discrete-Event Simulation: A Quantum-Network Case Study**

Author: David Vesterlund (Vesterlund Ventures, WestQuant Open)

Target journal: Applications of Modelling and Simulation (AMS) — eISSN 2600-8084

## Status

This repository is prepared for a public reproducibility release. The manuscript is under final revision. The raw simulation datasets, frozen simulator, dependency lockfile, complete seed/configuration ledger, and figure-generation scripts will be deposited before submission.

## Format

The manuscript uses the official AMS Journal LaTeX class (`ams-journal.cls`). Compile with:

```bash
cd manuscript
tectonic paper_2_ams.tex
```

## Repository Structure

```
simulation-decision-reliability/
├── manuscript/              # LaTeX source and compiled PDF
│   ├── ams-journal.cls      # AMS Journal class file
│   ├── AMS_style.bst        # AMS bibliography style
│   ├── template_images/     # AMS header/footer logos
│   ├── figures/             # Figure files
│   ├── paper_2_ams.tex      # Main manuscript source
│   ├── references.bib       # BibTeX references
│   └── paper_2_ams.pdf      # Compiled PDF
├── docs/                    # Documentation
│   ├── REMAINING_WORK.txt
│   ├── CHANGES.txt
│   ├── SOURCE_AUDIT.txt
│   ├── claim_ledger.csv
│   ├── cover_letter.txt
│   └── submission_checklist.txt
├── data/                    # Simulation data (to be deposited)
├── scripts/                 # Analysis and figure-generation scripts
├── submission/              # Highlights, cover letter
└── README.md
```

## Reproducibility

A public release URL, commit identifier, checksums, and archival DOI will identify the completed deposit before submission.

## License

Manuscript: © 2026 David Vesterlund
Code: MIT License (to be confirmed at release)
