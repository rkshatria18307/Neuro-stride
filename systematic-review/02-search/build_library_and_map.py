#!/usr/bin/env python3
"""Deduplicate identified records and build a keyword evidence map.

This is bibliographic processing only. It does not screen for inclusion.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

RAW = Path("/workspace/systematic-review/02-search/raw-exports")
LIB = Path("/workspace/systematic-review/03-library")
MAP = Path("/workspace/systematic-review/04-evidence-map")
LIB.mkdir(parents=True, exist_ok=True)
MAP.mkdir(parents=True, exist_ok=True)

SOURCE_RANK = {
    "PubMed": 0,
    "EuropePMC": 1,
    "OpenAlex": 2,
    "ClinicalTrials.gov": 3,
    "SemanticScholar": 4,
    "Crossref": 5,
}

STROKE_RE = re.compile(
    r"\b(stroke|hemipleg|hemipares|cerebrovascular accident|\bcva\b|post[- ]stroke|poststroke)\b",
    re.I,
)
AI_RE = re.compile(
    r"\b(artificial intelligence|\bai\b|machine learning|deep learning|neural network|"
    r"reinforcement learning|pose estimation|openpose|mediapipe|blazepose|"
    r"algorithm[- ]based|recommender|decision support|intelligent tutoring)\b",
    re.I,
)
CAMERA_RE = re.compile(
    r"\b(kinect|azure kinect|openpose|mediapipe|blazepose|pose estimation|markerless|"
    r"computer vision|depth camera|rgb-?d|webcam|video[- ]based|vision[- ]based|"
    r"camera[- ]based|skeleton tracking|motion capture|realsense|leap motion|"
    r"theia3d|orbbec|monocular)\b",
    re.I,
)
PRESCRIPTION_RE = re.compile(
    r"\b(exercise prescription|prescribed exercise|personalized exercise|personalised exercise|"
    r"individualized exercise|individualised exercise|adaptive exercise|exercise dose|"
    r"exercise program|home exercise|recommender|closed[- ]loop|difficulty adaptation|"
    r"adaptive personalization)\b",
    re.I,
)
REVIEW_RE = re.compile(
    r"\b(systematic review|scoping review|meta[- ]analysis|umbrella review|mapping review|"
    r"rapid review|narrative review|comprehensive review)\b",
    re.I,
)
RCT_RE = re.compile(r"\b(randomized|randomised|rct)\b", re.I)
PROTOCOL_RE = re.compile(r"\b(protocol|prospero|trial registration)\b", re.I)
VALIDITY_RE = re.compile(
    r"\b(validit|reliabilit|psychometric|measurement properties|accuracy|agreement|"
    r"criterion|cosmin|icc\b|rmse|mae\b|correlation)\b",
    re.I,
)
INTERVENTION_RE = re.compile(
    r"\b(effectiveness|efficacy|outcome|trial|intervention|fma|fugl[- ]meyer|barthel|"
    r"wolf motor|arat\b|berg balance)\b",
    re.I,
)


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    recs = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def blob(r: dict) -> str:
    return " ".join(
        [
            r.get("title") or "",
            r.get("abstract") or "",
            " ".join(r.get("publication_types") or [])
            if isinstance(r.get("publication_types"), list)
            else str(r.get("publication_types") or ""),
        ]
    )


def classify(r: dict) -> dict:
    text = blob(r)
    stroke = bool(STROKE_RE.search(text))
    ai = bool(AI_RE.search(text))
    camera = bool(CAMERA_RE.search(text))
    rx = bool(PRESCRIPTION_RE.search(text))
    is_review = bool(REVIEW_RE.search(text)) or any(
        "review" in str(x).lower() or "meta" in str(x).lower()
        for x in (r.get("publication_types") or [])
    )
    domain = "unclear_or_offtopic_keyword"
    if is_review and stroke and (ai or camera or rx):
        domain = "review_overlap_candidate"
    elif r.get("source") == "ClinicalTrials.gov":
        domain = "trial_registry"
    elif stroke and camera and (ai or rx):
        domain = "both_ai_or_rx_and_camera"
    elif stroke and camera:
        domain = "camera_movement_analysis"
    elif stroke and rx and ai:
        domain = "ai_exercise_prescription"
    elif stroke and ai:
        domain = "ai_stroke_other"
    elif stroke:
        domain = "stroke_other"
    design = "unspecified"
    if r.get("source") == "ClinicalTrials.gov":
        design = "trial_registration"
    elif is_review:
        design = "review"
    elif PROTOCOL_RE.search(text):
        design = "protocol_or_registration"
    elif RCT_RE.search(text):
        design = "rct_token"
    elif VALIDITY_RE.search(text):
        design = "measurement_token"
    elif INTERVENTION_RE.search(text):
        design = "intervention_token"
    return {
        "stroke_token": stroke,
        "ai_token": ai,
        "camera_token": camera,
        "prescription_token": rx,
        "map_domain": domain,
        "map_design_token": design,
        "keyword_map_only": True,
    }


def merge_keep(a: dict, b: dict) -> dict:
    ra = SOURCE_RANK.get(a.get("source"), 99)
    rb = SOURCE_RANK.get(b.get("source"), 99)
    keep, other = (a, b) if ra <= rb else (b, a)
    # richer abstract
    if len(other.get("abstract") or "") > len(keep.get("abstract") or ""):
        keep["abstract"] = other["abstract"]
    if not keep.get("doi") and other.get("doi"):
        keep["doi"] = other["doi"]
        keep["doi_url"] = other.get("doi_url") or keep.get("doi_url")
    if not keep.get("pmid") and other.get("pmid"):
        keep["pmid"] = other["pmid"]
        if not keep.get("url"):
            keep["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{keep['pmid']}/"
    if not keep.get("nct_id") and other.get("nct_id"):
        keep["nct_id"] = other["nct_id"]
    sources = set(keep.get("sources_seen") or [keep.get("source")])
    sources.add(other.get("source"))
    keep["sources_seen"] = sorted(sources)
    strats = set(keep.get("strategies_seen") or [keep.get("strategy")])
    strats.add(other.get("strategy"))
    keep["strategies_seen"] = sorted(x for x in strats if x)
    keep["duplicate_count"] = keep.get("duplicate_count", 1) + other.get("duplicate_count", 1)
    return keep


def key_for(r: dict) -> str:
    doi = (r.get("doi") or "").strip().lower()
    pmid = str(r.get("pmid") or "").strip()
    nct = str(r.get("nct_id") or "").strip().upper()
    if doi:
        return "doi:" + doi
    if pmid:
        return "pmid:" + pmid
    if nct:
        return "nct:" + nct
    tn = (r.get("title_norm") or "").strip()
    yr = str(r.get("year") or "").strip()
    if tn and yr:
        return f"titleyear:{tn}|{yr}"
    if tn:
        return "title:" + tn
    return "row:" + str(id(r))


def main():
    files = {
        "PubMed": list(RAW.glob("pubmed_*.jsonl")),
        "EuropePMC": list(RAW.glob("europepmc_*.jsonl")),
        "OpenAlex": list(RAW.glob("openalex_*.jsonl")),
        "ClinicalTrials.gov": list(RAW.glob("ctgov_*.jsonl")),
        "SemanticScholar": list(RAW.glob("s2_SS*.jsonl")),
        "Crossref": list(RAW.glob("crossref_*.jsonl")),
    }

    raw_n = Counter()
    all_rows = []
    for source, paths in files.items():
        for p in paths:
            recs = load_jsonl(p)
            raw_n[source] += len(recs)
            all_rows.extend(recs)

    # Crossref is a ranked sample with massive false-positive yield.
    # Keep Crossref rows only if title/abstract has stroke AND (camera OR AI OR prescription).
    filtered = []
    crossref_dropped = 0
    for r in all_rows:
        if r.get("source") == "Crossref":
            t = blob(r)
            if not (STROKE_RE.search(t) and (CAMERA_RE.search(t) or AI_RE.search(t) or PRESCRIPTION_RE.search(t))):
                crossref_dropped += 1
                continue
            r["verification"] = "verified_from_crossref_api_but_low_precision_query_filtered"
        filtered.append(r)

    merged = {}
    for r in filtered:
        r = dict(r)
        r["sources_seen"] = [r.get("source")]
        r["strategies_seen"] = [r.get("strategy")]
        r["duplicate_count"] = 1
        k = key_for(r)
        if k in merged:
            merged[k] = merge_keep(merged[k], r)
        else:
            merged[k] = r

    records = []
    for r in merged.values():
        r.update(classify(r))
        if not r.get("url"):
            if r.get("pmid"):
                r["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{r['pmid']}/"
            elif r.get("doi"):
                r["url"] = f"https://doi.org/{r['doi']}"
            elif r.get("nct_id"):
                r["url"] = f"https://clinicaltrials.gov/study/{r['nct_id']}"
        records.append(r)

    records.sort(key=lambda x: (x.get("year") or "0000", x.get("title") or ""), reverse=True)

    fields = [
        "record_uid",
        "title",
        "authors",
        "year",
        "journal",
        "doi",
        "pmid",
        "nct_id",
        "publication_types",
        "study_design_reported",
        "map_domain",
        "map_design_token",
        "stroke_token",
        "ai_token",
        "camera_token",
        "prescription_token",
        "url",
        "doi_url",
        "source_preferred",
        "sources_seen",
        "strategies_seen",
        "duplicate_count",
        "verification",
        "abstract",
    ]
    out_rows = []
    for i, r in enumerate(records, 1):
        ptypes = r.get("publication_types") or []
        if isinstance(ptypes, list):
            ptypes_s = " | ".join(str(x) for x in ptypes if x)
        else:
            ptypes_s = str(ptypes)
        uid = r.get("doi") and f"doi:{r['doi']}" or (r.get("pmid") and f"pmid:{r['pmid']}") or (
            r.get("nct_id") and f"nct:{r['nct_id']}"
        ) or f"uid:{i}"
        out_rows.append(
            {
                "record_uid": uid,
                "title": r.get("title") or "",
                "authors": r.get("author_string") or "; ".join(r.get("authors") or []),
                "year": r.get("year") or "",
                "journal": r.get("journal") or "",
                "doi": r.get("doi") or "",
                "pmid": r.get("pmid") or "",
                "nct_id": r.get("nct_id") or "",
                "publication_types": ptypes_s,
                "study_design_reported": ptypes_s or r.get("map_design_token") or "",
                "map_domain": r.get("map_domain"),
                "map_design_token": r.get("map_design_token"),
                "stroke_token": r.get("stroke_token"),
                "ai_token": r.get("ai_token"),
                "camera_token": r.get("camera_token"),
                "prescription_token": r.get("prescription_token"),
                "url": r.get("url") or "",
                "doi_url": r.get("doi_url") or "",
                "source_preferred": r.get("source") or "",
                "sources_seen": " | ".join(r.get("sources_seen") or []),
                "strategies_seen": " | ".join(r.get("strategies_seen") or []),
                "duplicate_count": r.get("duplicate_count"),
                "verification": r.get("verification") or "",
                "abstract": (r.get("abstract") or "").replace("\n", " ")[:3000],
            }
        )

    with (LIB / "deduplicated_reference_library.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    # RIS
    with (LIB / "deduplicated_reference_library.ris").open("w", encoding="utf-8") as f:
        for r in out_rows:
            f.write("TY  - JOUR\n")
            if r["title"]:
                f.write("TI  - " + r["title"][:500] + "\n")
            for au in (r["authors"] or "").split("; "):
                if au.strip():
                    f.write("AU  - " + au.strip()[:200] + "\n")
            if r["year"]:
                f.write("PY  - " + str(r["year"])[:4] + "\n")
            if r["journal"]:
                f.write("JO  - " + r["journal"] + "\n")
            if r["doi"]:
                f.write("DO  - " + r["doi"] + "\n")
            if r["pmid"]:
                f.write("AN  - PMID:" + r["pmid"] + "\n")
            if r["url"]:
                f.write("UR  - " + r["url"] + "\n")
            f.write("ER  - \n\n")

    # Evidence map counts (keyword tags, not inclusion)
    domain_counts = Counter(r["map_domain"] for r in out_rows)
    design_counts = Counter(r["map_design_token"] for r in out_rows)
    year_counts = Counter((r["year"] or "unknown")[:4] for r in out_rows)
    cross = Counter((r["map_domain"], r["map_design_token"]) for r in out_rows)

    stats = {
        "note": "These counts are DEDUPLICATED IDENTIFIED RECORDS after keyword tagging. They are NOT screened-in study counts.",
        "raw_rows_by_source": dict(raw_n),
        "crossref_rows_dropped_as_offtopic_sample": crossref_dropped,
        "rows_entering_dedup": len(filtered),
        "deduplicated_records": len(out_rows),
        "with_doi": sum(1 for r in out_rows if r["doi"]),
        "with_pmid": sum(1 for r in out_rows if r["pmid"]),
        "with_nct": sum(1 for r in out_rows if r["nct_id"]),
        "keyword_domain_counts": dict(domain_counts),
        "keyword_design_token_counts": dict(design_counts),
        "records_missing_doi_and_pmid_and_nct": sum(
            1 for r in out_rows if not r["doi"] and not r["pmid"] and not r["nct_id"]
        ),
    }
    (LIB / "dedup_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    with (MAP / "evidence_map_counts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["map_domain", "map_design_token", "n_identified_records", "note"])
        for (dom, des), n in sorted(cross.items()):
            w.writerow([dom, des, n, "keyword tag only; not inclusion"])

    with (MAP / "evidence_map_by_year.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "n_identified_records"])
        for y in sorted(year_counts):
            w.writerow([y, year_counts[y]])

    # overlap candidate reviews for novelty file
    reviews = [
        r
        for r in out_rows
        if r["map_domain"] == "review_overlap_candidate"
        and r["stroke_token"]
        and (r["camera_token"] or r["prescription_token"] or r["ai_token"])
    ]
    with (MAP / "novelty_review_candidates.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "title",
                "authors",
                "doi",
                "pmid",
                "journal",
                "url",
                "camera_token",
                "ai_token",
                "prescription_token",
                "verification",
            ],
        )
        w.writeheader()
        for r in reviews:
            w.writerow({k: r.get(k) for k in w.fieldnames})

    both = [r for r in out_rows if r["map_domain"] == "both_ai_or_rx_and_camera"]
    with (MAP / "intersection_ai_camera_identified.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["year", "title", "authors", "doi", "pmid", "nct_id", "journal", "url", "map_design_token", "verification"],
        )
        w.writeheader()
        for r in both:
            w.writerow({k: r.get(k) for k in w.fieldnames})

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
