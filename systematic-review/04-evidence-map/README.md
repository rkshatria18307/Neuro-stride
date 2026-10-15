# Evidence map (keyword tags on identified records)

**Not a map of included studies.** Dual screening has not been done. Cell counts are unique library records whose title/abstract (or publication type) matched simple regular expressions.

## Files

- `evidence_map_counts.csv` — domain × design-token  
- `evidence_map_by_year.csv`  
- `novelty_review_candidates.csv` — 381 records tagged as reviews with stroke plus AI/camera/prescription tokens  
- `intersection_ai_camera_identified.csv` — 138 records tagged as stroke **and** camera **and** (AI or prescription)

## Domain definitions (tokens, not eligibility)

| `map_domain` | n unique | Meaning |
|---|---:|---|
| stroke_other | 812 | Stroke token without camera/AI/prescription match (includes many S1/S4/CT leakage) |
| camera_movement_analysis | 489 | Stroke + camera/pose/Kinect token, no simultaneous AI/prescription token |
| review_overlap_candidate | 381 | Review-like + stroke + (AI or camera or prescription) |
| trial_registry | 370 | ClinicalTrials.gov survivors |
| unclear_or_offtopic_keyword | 240 | Failed stroke token (Crossref/OpenAlex/Europe PMC noise) |
| both_ai_or_rx_and_camera | 138 | Stroke + camera + (AI or prescription) |
| ai_stroke_other | 112 | Stroke + AI, not camera, not prescription phrase |
| ai_exercise_prescription | 5 | Stroke + prescription phrase + AI, not camera |

The **5** `ai_exercise_prescription` rows are an **under-count**: many prescription-adjacent papers are tagged `review_overlap_candidate`, `both_*`, or `ai_stroke_other` because the regex for “exercise prescription” is strict. They are:

1. TeleRehaB DSS protocol, BMJ Open 2026, PMID 42350021, DOI 10.1136/bmjopen-2025-108821  
2. Forecasting dropout in home-based movement rehab, IEEE TNSRE 2026, PMID 42113670  
3. AI and digital technologies across the stroke continuum, Medicina 2026, PMID 42512797  
4. Automatic identification of UL exercise type and dose with **body-worn** sensors, PMID 34414353 (likely **out** of camera concept)  
5. Web-based UL home rehab with **smartwatch** + ML, JMIR 2020, PMID 32480361 (wearable)

## Design tokens

Regex hits on words such as randomized, validity/reliability, protocol, review, Fugl-Meyer, etc. `unspecified` means no token fired.

## How to read this in a protocol

Use the map to **justify** three synthesis streams (applications, measurement, interventions) and to show that camera+AI intersection records exist (**138 tagged**, not 138 included). Do not quote these cells as results of the review.
