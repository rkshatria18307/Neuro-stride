# Search log (identification only)

**Run started (UTC):** 2026-10-15T08:44:31  
**Run finished (UTC):** 2026-10-15T08:46:45  
**Operator:** automated E-utilities / open APIs from this environment  
**Strings:** `strategies/search_strategies.md` and `run_bibliographic_search.py`  
**Raw payloads:** `raw-exports/`  
**Event log:** `api_run_log.jsonl`

These numbers are **database yields and retrieval counts**. They are **not** title/abstract screening counts and **not** included-study counts.

---

## 1. PubMed / MEDLINE (NCBI E-utilities)

Interface: `esearch.fcgi` + `efetch.fcgi` (`retmode=xml`).  
No date or language limits. `tool=neurostride_sr`.

| Strategy | Hit count (esearch) | Journal XML records parsed | Notes |
|---|---:|---:|---|
| S0_novelty_reviews | 530 | 529 | Two additional hits are `PubmedBookArticle` (NIHR monographs), not parsed by the journal-article splitter: PMID 25642500 (DOI 10.3310/hsdr02400); PMID 30020591 (DOI 10.3310/eme05030). |
| S1_ai_exercise_prescription | 525 | 525 | Full retrieval |
| S2_camera_movement_analysis | 896 | 895 | Same book-article gap: PMID 30020591 is in S2 |
| S3_ai_camera_intersection | 192 | 192 | Full retrieval |
| S4_cochrane_subset | 57 | 57 | CDSR via PubMed journal tag only |

PubMed raw JSONL rows (sum of strategy files): **2198** (strategies overlap; not unique).

Record-level verification: title, authors, year, PMID, DOI (when present in XML), publication types, PubMed URL from NCBI XML.

---

## 2. Europe PMC REST

| Strategy | hitCount | Retrieved | Notes |
|---|---:|---:|---|
| E0_reviews | 2807 | 1000 | Capped at 10 pages × 100. Precision poor (diagnosis/imaging leakage). |
| E1_ai_exercise | 4 | 4 | Full retrieval; very specific TITLE_ABS intersection |
| E2_camera | 678 | 700 | Page window exceeded hitCount (likely last-page overlap). Deduplicated later. |

Verification: Europe PMC core JSON (`pmid`, `doi`, `title`, `authorList`, `pubYear`).

---

## 3. OpenAlex Works API

| Strategy | API `meta.count` | Retrieved | Notes |
|---|---:|---:|---|
| O0_reviews | 73330 (page 1) then first-page 50 kept | 50 | Keyword `search=` does **not** honour Boolean; count is not a comparable yield |
| O1_ai_exercise | 1541 | 50 | Cursor page 2 returned HTTP 401 |
| O2_camera | 31381 (retry page 1) | 50 | First attempt page 2 HTTP 429 |

**Treat OpenAlex as a 150-record supplementary sample, not a database search.**

---

## 4. Crossref Works API (`query=`, relevance ranked)

| Strategy | `total-results` | Retrieved | Notes |
|---|---:|---:|---|
| C0_reviews | 1,388,345 | 200 | Bag-of-words; **not** a Boolean yield |
| C1_ai_ex | 5,469,553 | 200 | Same |
| C2_camera | 8,273,153 | 200 | Sample titles included non-clinical camera-pose papers |

**Do not report Crossref `total-results` as identification n.**  
Post-filter: 542/600 Crossref rows dropped because title/abstract lacked stroke plus (camera or AI or prescription) tokens. **58 Crossref rows entered deduplication.**

---

## 5. ClinicalTrials.gov API v2

| Strategy | totalCount | Retrieved |
|---|---:|---:|
| T1 (`query.cond=stroke` AND AI/ML/pose/Kinect/vision/markerless term) | 371 | 371 |

Verification: NCT ID, brief title, sponsor, study type, status, registry URL.

Many of these 371 will be imaging/triage AI rather than rehab cameras. Keyword map tagged **370** as `trial_registry` after dedup (one may have merged). **Not screened.**

---

## 6. Semantic Scholar Graph API

| Strategy | HTTP | Retrieved |
|---|---:|---:|
| SS0, SS1, SS2 | **429 Too Many Requests** | 0 |

**Inaccessible this run.**

---

## 7. PROSPERO

Attempted `https://www.crd.york.ac.uk/prospero/rest/api/search` — HTTP 200 body: `header value undefined`.  
HTML UI requires JavaScript. Bulk export **not possible**.  
Individual records listed in the novelty assessment were found via web search and are **partially verified** (URL exists; structured fields not API-confirmed).

---

## 8. Targeted verification of overlapping reviews

See `../01-novelty-assessment/verified_overlapping_reviews.csv`.  
PubMed HTML search pages returned 403 from the fetch tool; verification used E-utilities and Crossref JSON instead.

Known failures:

| Record | Issue |
|---|---|
| DOI 10.82161/m6en-k684 | Crossref 404; World Physiotherapy abstract page OK |
| DOI 10.3389/fneur.2024.1452431 | Guessed DOI; Crossref 404; **not used** |
| DOI 10.1177/02692155241287870 | Guessed DOI; Crossref 404; tele-assessment actual DOI is 10.1177/02692155241258867 |
| Boukhennoufa 2022 DOI 10.1016/j.bspc.2021.103197 | Crossref OK; PubMed `[doi]` lookup count 0 |
| Dimaguila 2017 PMID 29295303 | PubMed XML has no DOI; Europe PMC supplies 10.3233/978-1-61499-830-3-1216 (Crossref not confirmed) |
| Figshare 10.6084/m9.figshare.33080168 | Landing page verified; not a journal article |

---

## 9. Combined identification (before unique-ing across strategies)

| Source | Raw rows written |
|---|---:|
| PubMed | 2198 |
| Europe PMC | 1704 |
| OpenAlex | 150 |
| ClinicalTrials.gov | 371 |
| Semantic Scholar | 0 |
| Crossref | 600 |
| **Total raw rows** | **5023** |

After dropping 542 off-topic Crossref sample rows: **4481** rows entered bibliographic deduplication.  
Deduplicated library: **2547** unique records (`../03-library/dedup_stats.json`).

---

## 10. Updates after the main runner

- OpenAlex O2 file was regenerated after a 429 wiped an empty overwrite; 50 records restored.  
- Two NIHR book PMIDs identified as the PubMed journal-XML gaps.  
- Targeted Crossref/PubMed checks for novelty-set titles (separate from the 08:44 bulk run).
