# Systematic review — search and novelty phase

**Title:** Artificial Intelligence-Assisted Exercise Prescription and Camera-Based Movement Analysis in Stroke Rehabilitation: A Systematic Review of Clinical Applications, Measurement Validity, and Intervention Outcomes

**Phase completed:** novelty assessment + literature *identification* (PRISMA-S style logging).  
**Phase not started:** screening, extraction, risk of bias, synthesis. **No screening counts are reported.**

The repository had no “master systematic-review instructions” file (only a one-line README). Methods follow PRISMA 2020 / PRISMA-S / Cochrane search reporting.

## Contents

| Path | What it is |
|---|---|
| `00-protocol/00_SCOPE_AND_METHODS_SEARCH_PHASE.md` | Questions, planned eligibility, sources, dedup rules |
| `01-novelty-assessment/` | Coverage judgement + verified overlapping reviews |
| `02-search/` | Verbatim strategies, search log, API runner, raw exports |
| `03-library/` | Deduplicated CSV/RIS (n=2547 unique **identified** records) |
| `04-evidence-map/` | Keyword tags only |

## Headline findings of this phase

- **Novelty:** No PubMed-indexed systematic review jointly answers AI-assisted *exercise prescription* + *camera-based* movement analysis + applications/validity/outcomes in stroke. Closest indexed neighbours are listed in `01-novelty-assessment/verified_overlapping_reviews.csv`.  
- **Grey literature:** Figshare deposit DOI 10.6084/m9.figshare.33080168 overlaps pose-estimation telerehab; its counts are unverified.  
- **Access gap:** Embase, CINAHL, Scopus, Web of Science, IEEE Xplore, CENTRAL, and PEDro were **not searchable**. Do not claim a complete SR search.  
- **PubMed yields (identification):** S0 reviews 530; S1 AI-prescription 525; S2 camera 896; S3 AI∩camera 192; S4 Cochrane-via-PubMed 57.

## Reproduction

```bash
python3 systematic-review/02-search/run_bibliographic_search.py
python3 systematic-review/02-search/build_library_and_map.py
```

OpenAlex/Semantic Scholar may throttle. PubMed is the primary reproducible source.
