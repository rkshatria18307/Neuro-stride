# Novelty assessment (search phase)

**Proposed title:** Artificial Intelligence-Assisted Exercise Prescription and Camera-Based Movement Analysis in Stroke Rehabilitation: A Systematic Review of Clinical Applications, Measurement Validity, and Intervention Outcomes

**Assessment date:** 15 October 2026 (UTC)  
**Question:** Does a completed, peer-reviewed systematic review already answer this title’s three questions in one synthesis?

**Answer:** No indexed, peer-reviewed systematic review was verified that *jointly* covers (i) AI-assisted *exercise prescription*, (ii) *camera-based* movement analysis (RGB / RGB-D / markerless pose estimation), and (iii) the triad of clinical applications, measurement validity, and intervention outcomes in stroke. Overlap exists in fragments. A 2026 Figshare deposit is the closest grey-literature neighbour for pose-estimation telerehabilitation but is not PubMed-indexed and its study list was not retrieved.

This is a **coverage map**, not a claim that primary studies are absent, and not a PRISMA included-study count.

---

## 1. Proposed unique contribution (a priori)

| Arm | What would be new if done rigorously |
|---|---|
| A. Clinical applications | Map *how* AI prescription engines and camera/pose systems are used in stroke physiotherapy (setting, limb, phase, supervision). |
| B. Measurement validity | COSMIN/QUADAS-style synthesis of camera/markerless index tests vs optical MoCap, clinician scales, or wearables **in stroke**. |
| C. Intervention outcomes | Effects of AI-prescribed or camera-guided exercise vs usual care (motor, activity, adherence, safety, dose). |

Existing reviews typically take **one** of: Kinect-as-game, VR, wearables, skeleton action-scoring on mixed rehab datasets, or generic AI-in-stroke.

## 2. Method of the novelty search

- PubMed strategy `S0_novelty_reviews`: **530 hits** (529 journal XML records + 2 NIHR *PubmedBookArticle* records; see search log).  
- Supplementary: Europe PMC `E0_reviews` (hitCount 2807, retrieval capped at 1000 — **low precision**, many imaging/diagnosis reviews).  
- OpenAlex page-1 sample only (Boolean not respected; hitCount not interpretable).  
- Targeted DOI/PMID verification via Crossref and PubMed E-utilities for the closest titles.  
- PROSPERO: **no bulk API**; individual records located via public web search and listed as **partially verified**.

Keyword tagging of the whole identified library found **381** records tagged `review_overlap_candidate`. That tag is **not** an included-review count; it includes off-topic stroke+AI imaging reviews.

## 3. Closest verified reviews (do they preempt?)

Bibliographic fields and verification flags are in `verified_overlapping_reviews.csv`. Summary:

### 3.1 Camera / markerless / Kinect / pose

| Review | Why it does not close the proposed title |
|---|---|
| Shenoy et al. 2026, *DIGITAL HEALTH* (PMID 42553385) | Upper-limb markerless assessment; not prescription; not intervention meta-analysis. |
| Fisher et al. 2026, *Clin Rehabil* (PMID 41739542) | All MoCap modalities for UL assessment, including IMUs. |
| Zhou et al. 2025, *Sensors* (PMID 40096440) | Depth-camera physiotherapy, **not stroke-only**. |
| Sauerzopf et al. 2024, *Clin Rehabil* (PMID 38839104) | Tele-assessment psychometrics; mixed sensors. |
| Almasi et al. 2022 Kinect scoping (PMID 35386303); Xavier-Rocha et al. 2020 Xbox/Kinect (PMID 32520231); Webster & Celik 2014 (PMID 24996956); Knippenberg et al. 2017 (PMID 28646914); Dimaguila et al. 2017 (PMID 29295303) | Kinect / early markerless generations; little OpenPose/MediaPipe/Azure Kinect; no AI prescription arm. |
| Sardari et al. 2023 skeleton RAE (PMID 37019012) | Mixed disability; computational action scoring. |
| Cherry-Allen et al. 2023 (PMID 36634334) | Perspective, not SR. |

### 3.2 AI rehabilitation / prescription / telerehab outcomes

| Review | Gap vs proposed title |
|---|---|
| Al Tawil et al. 2026 *Front Rehabil Sci* (PMID 42381640) | ML **inside VR** closed-loop adaptation. |
| Senadheera et al. 2024 *Sensors* (PMID 39460066) | Broad AI-stroke scoping (704 studies claimed). |
| Rahman et al. 2023 *IEEE TNSRE* (PMID 36327176) | Robot/VR + ML assessment; authors’ own dataset experiments mixed with the review. |
| Mahmoud et al. 2023 *Eur Rev Med Pharmacol Sci* (PMID 37318455) | AI/ML PT vs conventional UL outcomes. |
| Laver et al. 2025 Cochrane VR (PMID 40537150) | VR/gaming RCTs; camera not the index test. |
| Caesarani et al. 2026 *IndoJPMR* (DOI 10.36803/indojpmr.v15i1.538) | AI telerehab vs conventional UL; **not in PubMed**. |
| Pinheiro et al. WP Congress abstract DOI 10.82161/m6en-k684 | Tailored **clinician** prescription; **excludes** the AI construct; Crossref 404; not PubMed. |

### 3.3 Explicit contrast (wearable, not camera)

Boukhennoufa et al. 2022 *BSPC* (DOI 10.1016/j.bspc.2021.103197): wearable ML assessment. **Verified in Crossref; PubMed DOI lookup returned 0 PMIDs.** Keep as contrast, not competitor.

### 3.4 Grey literature that must be named

**Verma 2026 Figshare** DOI `10.6084/m9.figshare.33080168` (posted 24 Jul 2026). Publisher page verified. Title overlaps pose estimation + accuracy + clinical outcomes in stroke telerehab. **Not in PubMed. Not a Crossref journal article. Included studies were not obtained.** Reported “27 studies / 1,482 participants” and pooled FMA 8.3 points are **the deposit’s claims and remain unverified**. Treat as a competing *attempt*, not as an indexed SR that closes the question. The proposed review is still distinguishable by adding **AI-assisted exercise prescription** and by requiring a librarian-grade multi-database search (Embase, CINAHL, IEEE, CENTRAL) that this environment cannot yet run.

## 4. PROSPERO / protocols (partial)

Located via web search; PROSPERO REST API returned header errors (see search log). Records **not bulk-downloaded**:

| ID / URL | Scope vs this title |
|---|---|
| [CRD420261298450](https://www.crd.york.ac.uk/PROSPERO/view/CRD420261298450) | ML adaptive personalization **in VR** stroke rehab (matches Al Tawil 2026). |
| [CRD420323670](https://www.crd.york.ac.uk/PROSPERO/view/323670) | Digital video exercise prescription for locomotor conditions; **excludes algorithm-determined programmes**. |
| [CRD420251027928](https://www.crd.york.ac.uk/PROSPERO/view/CRD420251027928) | Home digital UL rehab in acute/subacute stroke (broad digital tech). |
| [CRD42024610482](https://www.crd.york.ac.uk/PROSPERO/view/CRD42024610482) | VR immersion levels including Kinect/Wii vs conventional UL training. |

No PROSPERO record was verified that uses the same three-arm title. **Registration of this review on PROSPERO is still advisable** before screening.

## 5. Novelty judgement (methodological)

**Proceed** with the systematic review, with these constraints:

1. Position against Shenoy 2026, Fisher 2026, Zhou 2025, Rahman 2023, Al Tawil 2026, and Laver 2025 so the protocol’s eligibility criteria *exclude* a mere Kinect-games or VR-only rerun.  
2. Define **AI-assisted exercise prescription** operationally (algorithm recommends or adapts type/dose/difficulty/feedback without requiring a VR headset).  
3. Define **camera-based movement analysis** as RGB, RGB-D/depth, or markerless pose estimation as the **index** sensing modality (wearable-only out).  
4. Split synthesis a priori into applications / COSMIN-style validity / intervention outcomes.  
5. Cite Verma 2026 Figshare as grey literature in the protocol’s “related reviews” section; do not treat its numbers as evidence until the included-study list is independently checked.  
6. Do **not** claim an empty field: PubMed `S2_camera_movement_analysis` yielded **896** records and `S3_ai_camera_intersection` **192** records (identification yields, not includes).

## 6. What was not done

- Dual appraisal of whether each of the 381 keyword-tagged reviews is on-topic.  
- Citation chasing of included lists inside Rahman, Shenoy, or Zhou.  
- Embase/CINAHL/Scopus/WoS/IEEE novelty search (inaccessible).
