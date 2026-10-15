# Executed search strategies (verbatim)

Search date (planned execution): **15 October 2026 (UTC)**.  
No date limits, no language limits at identification.  
Human translation of concept blocks is in `00-protocol/00_SCOPE_AND_METHODS_SEARCH_PHASE.md`.

## PubMed / MEDLINE (NCBI E-utilities)

### S0_novelty_reviews

```
("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] OR "post-stroke"[tiab] OR poststroke[tiab]) AND ("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR "computer vision"[tiab] OR "pose estimation"[tiab] OR Kinect[tiab] OR markerless[tiab] OR "exercise prescription"[tiab] OR "personalized exercise"[tiab] OR "personalised exercise"[tiab] OR "adaptive exercise"[tiab] OR "video-based"[tiab] OR "vision-based"[tiab] OR "camera-based"[tiab] OR "motion capture"[tiab]) AND ("systematic review"[pt] OR "Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type] OR "scoping review"[tiab] OR "systematic review"[tiab] OR "meta-analysis"[tiab] OR "umbrella review"[tiab] OR "mapping review"[tiab] OR "rapid review"[tiab])
```

### S1_ai_exercise_prescription

```
("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] OR "post-stroke"[tiab] OR poststroke[tiab]) AND ("exercise prescription"[tiab] OR "prescribed exercise"[tiab] OR "exercise recommend*"[tiab] OR "personalized exercise"[tiab] OR "personalised exercise"[tiab] OR "individualized exercise"[tiab] OR "individualised exercise"[tiab] OR "adaptive exercise"[tiab] OR "exercise dose"[tiab] OR "exercise program*"[tiab] OR "home exercise"[tiab] OR "rehabilitation exercise"[tiab] OR "Exercise Therapy"[Mesh]) AND ("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR "neural network*"[tiab] OR "reinforcement learning"[tiab] OR "decision support"[tiab] OR "recommender system"[tiab] OR "intelligent tutoring"[tiab] OR "closed-loop"[tiab] OR "algorithm-based"[tiab] OR "AI-assisted"[tiab] OR "AI-driven"[tiab])
```

### S2_camera_movement_analysis

```
("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] OR "post-stroke"[tiab] OR poststroke[tiab]) AND (Kinect[tiab] OR "Azure Kinect"[tiab] OR OpenPose[tiab] OR MediaPipe[tiab] OR BlazePose[tiab] OR "pose estimation"[tiab] OR markerless[tiab] OR "computer vision"[tiab] OR "depth camera"[tiab] OR "RGB-D"[tiab] OR RGBD[tiab] OR webcam[tiab] OR "video-based"[tiab] OR "vision-based"[tiab] OR "camera-based"[tiab] OR "skeleton tracking"[tiab] OR "motion capture"[tiab] OR "movement analysis"[tiab] OR "movement assessment"[tiab] OR Theia3D[tiab] OR RealSense[tiab] OR "Leap Motion"[tiab] OR Orbbec[tiab] OR (monocular[tiab] AND pose[tiab])) AND (rehabilitat*[tiab] OR physiotherapy[tiab] OR "physical therapy"[tiab] OR assessment[tiab] OR validity[tiab] OR reliability[tiab] OR kinematics[tiab] OR gait[tiab] OR "upper limb"[tiab] OR "upper extremity"[tiab] OR "motor function"[tiab])
```

### S3_ai_camera_intersection

```
("Stroke"[Mesh] OR stroke[tiab] OR hemiplegi*[tiab] OR "post-stroke"[tiab] OR poststroke[tiab]) AND ("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] OR "machine learning"[tiab] OR "deep learning"[tiab] OR "neural network*"[tiab] OR "pose estimation"[tiab] OR OpenPose[tiab] OR MediaPipe[tiab]) AND (Kinect[tiab] OR camera[tiab] OR "computer vision"[tiab] OR video[tiab] OR markerless[tiab] OR "RGB"[tiab] OR webcam[tiab] OR "depth camera"[tiab]) AND (rehabilitat*[tiab] OR physiotherapy[tiab] OR assessment[tiab] OR exercise[tiab] OR kinematics[tiab])
```

### S4_cochrane_subset

```
("Stroke"[Mesh] OR stroke[tiab]) AND ("virtual reality"[tiab] OR Kinect[tiab] OR "artificial intelligence"[tiab] OR "exercise"[tiab] OR "telerehabilitation"[tiab] OR "video game"[tiab]) AND "Cochrane Database Syst Rev"[ta]
```

## Europe PMC

See `run_bibliographic_search.py` `EUROPEPMC_QUERIES` (E0_reviews, E1_ai_exercise, E2_camera).

## OpenAlex

Keyword `search=` parameter (not Boolean MEDLINE syntax). High recall, lower precision. Treat as supplementary.

## Crossref

Bibliographic `query=` (relevance ranked). High off-topic leakage expected. Treat as supplementary; do not interpret hit counts as comparable to PubMed.

## ClinicalTrials.gov API v2

- `query.cond`: stroke  
- `query.term`: artificial intelligence OR machine learning OR pose estimation OR Kinect OR computer vision OR camera-based OR markerless  

## Semantic Scholar Graph API

Natural-language queries SS0–SS2 in the runner. Unauthenticated; may return HTTP 429.

## Not run (inaccessible)

Embase, Scopus, Web of Science, CINAHL, IEEE Xplore controlled vocabulary search, Cochrane CENTRAL native, PEDro, AMED, PsycINFO, WHO ICTRP, Google Scholar citation chasing.
