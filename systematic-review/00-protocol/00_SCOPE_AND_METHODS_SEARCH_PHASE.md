# Search-phase protocol (no results synthesis)

**Working title:** Artificial Intelligence-Assisted Exercise Prescription and Camera-Based Movement Analysis in Stroke Rehabilitation: A Systematic Review of Clinical Applications, Measurement Validity, and Intervention Outcomes

**Repository:** Neuro-stride  
**Phase:** Novelty assessment + literature identification only  
**Date of search execution:** 15 October 2026 (UTC)  
**Reporting standards applied:** PRISMA 2020; PRISMA-S (search reporting); Cochrane Handbook (search methods); PRESS-style documentation of concept blocks. Risk-of-bias tools (RoB 2, ROBINS-I, COSMIN, QUADAS-2) are specified for a later phase and are **not applied in this deposit**.

**Note on master instructions:** No file named “master systematic-review instructions” was present in this repository at the start of work (only `README.md`). Methods below follow those reporting standards. This deposit **does not draft review Results** and **does not invent title/abstract or full-text screening counts**.

---

## 1. Review questions (a priori)

Three linked questions, not a single pooled effect:

1. **Clinical applications:** How have AI-assisted exercise-prescription systems and camera-based movement-analysis systems been used in stroke rehabilitation (setting, body region, phase post-stroke, clinician vs unsupervised use)?
2. **Measurement validity:** What is the measurement-property evidence (reliability, criterion/construct validity, measurement error, clinical utility) for camera-based / markerless / pose-estimation assessment versus accepted references (optical motion capture, clinician scales, wearables)?
3. **Intervention outcomes:** What are the effects of AI-assisted prescription and/or camera-guided exercise on motor function, activity, participation, adherence, safety, and dose, relative to usual care or non-AI comparators?

## 2. Eligibility framework (for later screening; not applied here)

| Element | Include (planned) | Exclude (planned) |
|---|---|---|
| Population | Adults after ischaemic or haemorrhagic stroke or TIA with motor sequelae; mixed neuro samples only if stroke data are separable | Paediatric-only; animal; purely healthy-volunteer method papers **unless** they are measurement-property studies of a system later used in stroke (flag, do not automatically include) |
| Concept A | AI/ML/DL used to recommend, adapt, dose, or personalise exercise | AI used only for imaging diagnosis, prognosis from EHR, or robot control **without** an exercise-prescription or camera-assessment component |
| Concept B | Camera, RGB, RGB-D/depth, webcam, Kinect/Azure Kinect, markerless optical, 2D/3D pose estimation (OpenPose, MediaPipe, BlazePose, Theia3D, etc.) | Wearable-only IMU/EMG/pressure systems **without** a camera/vision stream; marker-based lab MoCap as the **index** test (allowed as **reference** standard) |
| Outcomes | Applications description; COSMIN-relevant properties; clinical/functional outcomes; adverse events; usability | Pure computer-vision benchmarks on non-clinical datasets with no stroke or rehab task |
| Designs | RCTs, quasi-experimental, observational, measurement studies, mixed-methods, trial registrations, protocols | Editorials, letters without data. Reviews are **retained for novelty mapping**, not as primary studies |
| Language / date | No date limit in identification. English full text planned for extraction; non-English records **retained in the library** and flagged | None at identification |

Dual independent screening is **not performed in this phase**. Records below are **identified candidates**.

## 3. Information sources

### Accessed and used for bibliographic retrieval

| Source | Interface | Status |
|---|---|---|
| PubMed/MEDLINE | NCBI E-utilities | Accessed; records retrieved |
| Europe PMC | REST API | Accessed; records retrieved |
| OpenAlex | Works API | Accessed; records retrieved |
| Crossref | Works API | Accessed; records retrieved |
| ClinicalTrials.gov | API v2 | Accessed; records retrieved |
| Semantic Scholar | Graph API | Attempted; see search log for HTTP status |
| PROSPERO | HTML/REST probe | **No usable public bulk API**; access limited |
| Publisher/PMC landing pages | Used only to verify previously identified review records | Selective verification of novelty-set items |

### Specified as core SR sources but **not accessible** in this environment

| Source | Reason |
|---|---|
| Embase (Elsevier) | No institutional login / API key |
| Scopus | No institutional login |
| Web of Science Core Collection | No institutional login |
| CINAHL (EBSCO) | No institutional login |
| IEEE Xplore (full controlled search) | No IEEE API key; some IEEE papers appear via PubMed/OpenAlex/Crossref if indexed |
| Cochrane CENTRAL (Wiley) | No Cochrane Library institutional access; Cochrane reviews partly captured via PubMed `Cochrane Database Syst Rev[ta]` |
| PEDro | No scripted API used |
| AMED, PsycINFO, SPORTDiscus | Not subscribed |
| Google Scholar | Not used as a reproducible database (rank instability; ToS); **citation chasing not completed in this phase** |
| ICTRP (WHO) | Not queried beyond ClinicalTrials.gov |
| Grey literature (ProQuest dissertations, conference proceedings not in Crossref) | Incomplete |

**Implication:** Identification is **MEDLINE-heavy plus open scholarly graphs**. Engineering-venue papers (IEEE ICORR, EMBC) and Embase-only physiotherapy trials are at high risk of being missed. A librarian re-run on Embase, CINAHL, Scopus, WoS, IEEE Xplore, CENTRAL, and PEDro is required before any claim of search completeness.

## 4. Concept blocks (PRESS-style)

- **P:** stroke / CVA / hemiplegia / post-stroke  
- **I1:** artificial intelligence, machine learning, deep learning, neural networks, reinforcement learning, decision support, recommender, AI-assisted prescription, closed-loop adaptation  
- **I2:** exercise prescription / programme / dose / personalised / adaptive / home exercise / exercise therapy  
- **I3:** Kinect, Azure Kinect, OpenPose, MediaPipe, BlazePose, pose estimation, markerless, computer vision, depth camera, RGB-D, webcam, camera-based, video-based, skeleton tracking, motion capture  
- **Review filter (novelty only):** systematic review, scoping review, meta-analysis, umbrella/mapping/rapid review  

Boolean strings as executed are stored verbatim in `02-search/strategies/` and in API metadata JSON.

## 5. Deduplication rules (applied to the library)

1. Match on normalised DOI (strip resolver prefix; lowercase).  
2. Else match on PMID.  
3. Else match on NCT number.  
4. Else match on normalised title + year.  
5. Keep the richest bibliographic record (prefer PubMed XML > Europe PMC > OpenAlex > Crossref > Semantic Scholar > ClinicalTrials.gov).  
6. Preserve `sources_seen` and `strategies_seen` on the surviving record.

Deduplication is **bibliographic**, not eligibility screening.

## 6. Evidence-map rules (this phase)

The map classifies **deduplicated identified records** using title/abstract keywords only:

- Domain: AI-prescription vs camera/vision vs both vs review vs trial registry vs unclear/off-topic-likely  
- Likely design tokens: RCT, protocol, review, measurement/validation, etc.  
- Stroke-token present vs absent  

This is **not** included-study counting. Cells are keyword tags. Off-topic leakage from Crossref/OpenAlex keyword search is expected and flagged.

## 7. What this phase will not do

- Dual screening, PRISMA flow numbers beyond database yields  
- Data extraction, risk of bias, meta-analysis, GRADE  
- Invented sample sizes or “n included”  
- Drafting of Results/Discussion of the review
