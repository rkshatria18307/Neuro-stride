# Inaccessible databases and unverified records

## A. Core systematic-review sources **not accessible** in this environment

No institutional credentials, API keys, or licensed interfaces were available for:

| Source | Consequence |
|---|---|
| Embase (Elsevier) | Misses conference papers and European rehab trials not in MEDLINE |
| CINAHL | Misses nursing/physio journals |
| Scopus | Misses citation index unique records |
| Web of Science Core Collection | Same |
| IEEE Xplore controlled search | High risk of missing ICORR/EMBC/ICVR camera papers (some leak into PubMed/Crossref) |
| Cochrane CENTRAL (Wiley) | Trial identification incomplete; CDSR partly via PubMed S4 |
| PEDro | Physiotherapy RCT index not searched |
| AMED, PsycINFO, SPORTDiscus | Not searched |
| WHO ICTRP | Only ClinicalTrials.gov queried |
| Google Scholar | Not used (non-reproducible ranks) |
| Semantic Scholar | HTTP 429 this run |
| PROSPERO bulk | API unusable; HTML is JS-only |
| OpenAlex full cursor | Page 2+ HTTP 401/429 |

**A librarian re-run on Embase, CINAHL, Scopus, WoS, IEEE Xplore, CENTRAL, and PEDro is required before protocol lock or any completeness claim.**

## B. Sources accessed but **not equivalent to Boolean bibliographic search**

- **Crossref `query=`:** multi-million `total-results`; treated as a ranked sample of 200×3.  
- **OpenAlex `search=`:** Boolean ignored; 50-record pages only.  
- **Europe PMC E0:** 2807 hits, 1000 retrieved; noisy review filter.  
- **Web search / publisher HTML:** used only to locate and verify specific novelty-set titles.

## C. Unverified or incompletely verified records

| Item | Status |
|---|---|
| Screening counts (title/abstract, full text) | **Not performed. None reported.** |
| Figshare Verma 2026 included-study list and pooled FMA | Deposit page verified; **data unverified** |
| IndoJPMR Caesarani 2026 included five trials | Publisher + Crossref verified; **studies not re-extracted**; not in PubMed |
| PROSPERO CRD records | URLs found; full XML/JSON not downloaded |
| Dimaguila 2017 DOI 10.3233/978-1-61499-830-3-1216 | Europe PMC only |
| Pinheiro WP abstract DOI 10.82161/m6en-k684 | Publisher HTML only; Crossref 404 |
| Boukhennoufa 2022 PMID | Crossref DOI verified; PubMed DOI search empty |
| 15 library rows with no DOI, PMID, or NCT | Conference abstracts / OpenAlex stubs — see library README |
| OpenAlex abstracts | Not requested (inverted index omitted) |
| Any record whose only source is Crossref after keyword filter | Bibliographic metadata verified by Crossref; **on-topic status unverified** |

## D. Parser limitations (documented, not hidden)

- PubMed exporter split on `<PubmedArticle>` only; NIHR books skipped then recovered by PMID.  
- Europe PMC E2 retrieved 700 vs hitCount 678.  
- Author names may retain XML entities (e.g. `Jos&#xe9;`) if present in source XML.
