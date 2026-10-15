# Deduplicated reference library

**File:** `deduplicated_reference_library.csv`  
**RIS:** `deduplicated_reference_library.ris`  
**Stats:** `dedup_stats.json`

This is a **bibliographic identification library**, not a list of included studies.

## Counts (15 October 2026)

| Metric | n |
|---|---:|
| Raw rows from all APIs | 5023 |
| Crossref sample rows dropped as off-topic (no stroke+(AI\|camera\|prescription) token) | 542 |
| Rows entering dedup | 4481 |
| **Unique records after DOI / PMID / NCT / title+year merge** | **2547** |
| With DOI | 2114 |
| With PMID | 2032 |
| With NCT | 371 |
| Missing DOI and PMID and NCT | 15 |

Preferred source when duplicates collide: PubMed XML > Europe PMC > OpenAlex > ClinicalTrials.gov > Semantic Scholar > Crossref.

`duplicate_count` is how many raw rows collapsed into that unique record (including same paper retrieved by several strategies).

## Columns

`record_uid`, `title`, `authors`, `year`, `journal`, `doi`, `pmid`, `nct_id`, `publication_types`, `study_design_reported`, `map_domain`, `map_design_token`, stroke/ai/camera/prescription tokens, URLs, `source_preferred`, `sources_seen`, `strategies_seen`, `duplicate_count`, `verification`, `abstract`.

`map_*` fields are **keyword tags** from title/abstract (see evidence map). They are not eligibility decisions.

`verification` values include `verified_from_pubmed_xml`, `verified_from_europepmc_api`, `verified_from_openalex_api`, `verified_from_clinicaltrials_gov_api`, `verified_from_crossref_api_but_low_precision_query_filtered`.

## How to use next

Import the RIS or CSV into Covidence/Rayyan. Screen **after** the Embase/CINAHL/IEEE top-up. Do not treat 2547 as the PRISMA identification total until those databases are run and re-deduplicated.
