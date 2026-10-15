#!/usr/bin/env python3
"""Verified bibliographic retrieval for the Neuro-stride systematic review.

Sources queried via public APIs (no institutional subscriptions):
  - NCBI PubMed E-utilities
  - Europe PMC REST
  - OpenAlex
  - Crossref
  - ClinicalTrials.gov v2
  - Semantic Scholar Graph API (unauthenticated, may throttle)

Does NOT query (inaccessible here): Embase, CINAHL, Scopus, Web of Science,
IEEE Xplore full API, PEDro, AMED, PsycINFO, Cochrane Central full interface
beyond PubMed-indexed Cochrane records.

Outputs raw JSONL plus a combined candidate table. Database hit counts are
search yields, not screening counts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw-exports"
LOG = ROOT / "api_run_log.jsonl"
RAW.mkdir(parents=True, exist_ok=True)

UA = "NeuroStride-SR/0.1 (systematic-review; mailto:neurostride-sr@local)"
NCBI_TOOL = "neurostride_sr"
NCBI_EMAIL = "neurostride-sr@local"
SLEEP = 0.4
NOW = datetime.now(timezone.utc).isoformat()


def get(url: str, headers: dict | None = None, timeout: int = 60) -> tuple[int, bytes, str]:
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(), dict(resp.headers).get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"", str(e)
    except Exception as e:
        return 0, str(e).encode(), "error"


def log_event(event: dict) -> None:
    event["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def norm_doi(doi: str | None) -> str:
    if not doi:
        return ""
    d = doi.strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d, flags=re.I)
    return d.lower()


def norm_title(title: str | None) -> str:
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def rec_id(rec: dict) -> str:
    doi = rec.get("doi") or ""
    pmid = rec.get("pmid") or ""
    nct = rec.get("nct_id") or ""
    if doi:
        return "doi:" + doi
    if pmid:
        return "pmid:" + str(pmid)
    if nct:
        return "nct:" + nct
    key = (rec.get("title_norm") or rec.get("title") or "") + "|" + (rec.get("year") or "")
    return "hash:" + hashlib.sha1(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Search strategies (documented verbatim)
# ---------------------------------------------------------------------------
PUBMED_STRATEGIES = {
    "S0_novelty_reviews": {
        "label": "Novelty: existing systematic/scoping reviews and meta-analyses",
        "query": (
            '("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] '
            'OR "post-stroke"[tiab] OR poststroke[tiab]) AND '
            '("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] '
            'OR "machine learning"[tiab] OR "deep learning"[tiab] OR "computer vision"[tiab] '
            'OR "pose estimation"[tiab] OR Kinect[tiab] OR markerless[tiab] OR "exercise prescription"[tiab] '
            'OR "personalized exercise"[tiab] OR "personalised exercise"[tiab] OR "adaptive exercise"[tiab] '
            'OR "video-based"[tiab] OR "vision-based"[tiab] OR "camera-based"[tiab] OR "motion capture"[tiab]) AND '
            '("systematic review"[pt] OR "Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type] '
            'OR "scoping review"[tiab] OR "systematic review"[tiab] OR "meta-analysis"[tiab] '
            'OR "umbrella review"[tiab] OR "mapping review"[tiab] OR "rapid review"[tiab])'
        ),
    },
    "S1_ai_exercise_prescription": {
        "label": "AI-assisted / adaptive / personalized exercise prescription after stroke",
        "query": (
            '("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] '
            'OR "post-stroke"[tiab] OR poststroke[tiab]) AND '
            '("exercise prescription"[tiab] OR "prescribed exercise"[tiab] OR "exercise recommend*"[tiab] '
            'OR "personalized exercise"[tiab] OR "personalised exercise"[tiab] OR "individualized exercise"[tiab] '
            'OR "individualised exercise"[tiab] OR "adaptive exercise"[tiab] OR "exercise dose"[tiab] '
            'OR "exercise program*"[tiab] OR "home exercise"[tiab] OR "rehabilitation exercise"[tiab] '
            'OR "Exercise Therapy"[Mesh]) AND '
            '("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] '
            'OR "machine learning"[tiab] OR "deep learning"[tiab] OR "neural network*"[tiab] '
            'OR "reinforcement learning"[tiab] OR "decision support"[tiab] OR "recommender system"[tiab] '
            'OR "intelligent tutoring"[tiab] OR "closed-loop"[tiab] OR "algorithm-based"[tiab] '
            'OR "AI-assisted"[tiab] OR "AI-driven"[tiab])'
        ),
    },
    "S2_camera_movement_analysis": {
        "label": "Camera / markerless / pose-estimation movement analysis in stroke rehab",
        "query": (
            '("Stroke"[Mesh] OR stroke[tiab] OR "cerebrovascular accident"[tiab] OR hemiplegi*[tiab] '
            'OR "post-stroke"[tiab] OR poststroke[tiab]) AND '
            '(Kinect[tiab] OR "Azure Kinect"[tiab] OR OpenPose[tiab] OR MediaPipe[tiab] OR BlazePose[tiab] '
            'OR "pose estimation"[tiab] OR markerless[tiab] OR "computer vision"[tiab] OR "depth camera"[tiab] '
            'OR "RGB-D"[tiab] OR RGBD[tiab] OR webcam[tiab] OR "video-based"[tiab] OR "vision-based"[tiab] '
            'OR "camera-based"[tiab] OR "skeleton tracking"[tiab] OR "motion capture"[tiab] '
            'OR "movement analysis"[tiab] OR "movement assessment"[tiab] OR Theia3D[tiab] '
            'OR RealSense[tiab] OR "Leap Motion"[tiab] OR Orbbec[tiab] OR (monocular[tiab] AND pose[tiab])) AND '
            '(rehabilitat*[tiab] OR physiotherapy[tiab] OR "physical therapy"[tiab] OR assessment[tiab] '
            'OR validity[tiab] OR reliability[tiab] OR kinematics[tiab] OR gait[tiab] '
            'OR "upper limb"[tiab] OR "upper extremity"[tiab] OR "motor function"[tiab])'
        ),
    },
    "S3_ai_camera_intersection": {
        "label": "Intersection: AI/ML AND camera/vision AND stroke rehab",
        "query": (
            '("Stroke"[Mesh] OR stroke[tiab] OR hemiplegi*[tiab] OR "post-stroke"[tiab] OR poststroke[tiab]) AND '
            '("Artificial Intelligence"[Mesh] OR "Machine Learning"[Mesh] OR "artificial intelligence"[tiab] '
            'OR "machine learning"[tiab] OR "deep learning"[tiab] OR "neural network*"[tiab] '
            'OR "pose estimation"[tiab] OR OpenPose[tiab] OR MediaPipe[tiab]) AND '
            '(Kinect[tiab] OR camera[tiab] OR "computer vision"[tiab] OR video[tiab] OR markerless[tiab] '
            'OR "RGB"[tiab] OR webcam[tiab] OR "depth camera"[tiab]) AND '
            '(rehabilitat*[tiab] OR physiotherapy[tiab] OR assessment[tiab] OR exercise[tiab] OR kinematics[tiab])'
        ),
    },
    "S4_cochrane_subset": {
        "label": "Cochrane Database of Systematic Reviews records via PubMed",
        "query": (
            '("Stroke"[Mesh] OR stroke[tiab]) AND '
            '("virtual reality"[tiab] OR Kinect[tiab] OR "artificial intelligence"[tiab] OR "exercise"[tiab] '
            'OR "telerehabilitation"[tiab] OR "video game"[tiab]) AND '
            '"Cochrane Database Syst Rev"[ta]'
        ),
    },
}

EUROPEPMC_QUERIES = {
    "E0_reviews": (
        '(TITLE_ABS:(stroke OR hemiplegi* OR "cerebrovascular accident") AND '
        'TITLE_ABS:("artificial intelligence" OR "machine learning" OR "pose estimation" OR Kinect OR markerless '
        'OR "exercise prescription" OR "computer vision") AND '
        '(REVIEW:"Systematic Review" OR TITLE_ABS:"systematic review" OR TITLE_ABS:"scoping review" '
        'OR TITLE_ABS:"meta-analysis"))'
    ),
    "E1_ai_exercise": (
        '(TITLE_ABS:(stroke OR hemiplegi*) AND TITLE_ABS:("exercise prescription" OR "personalized exercise" '
        'OR "adaptive exercise" OR "home exercise" OR "exercise program") AND '
        'TITLE_ABS:("artificial intelligence" OR "machine learning" OR "deep learning" OR "neural network" '
        'OR "reinforcement learning" OR "AI-assisted"))'
    ),
    "E2_camera": (
        '(TITLE_ABS:(stroke OR hemiplegi*) AND TITLE_ABS:(Kinect OR OpenPose OR MediaPipe OR "pose estimation" '
        'OR markerless OR "computer vision" OR "depth camera" OR "camera-based" OR "video-based" '
        'OR "vision-based" OR "motion capture") AND TITLE_ABS:(rehabilitat* OR assessment OR kinematics '
        'OR physiotherapy OR gait))'
    ),
}

OPENALEX_QUERIES = {
    "O0_reviews": 'stroke AND ("systematic review" OR "scoping review") AND ("artificial intelligence" OR Kinect OR "pose estimation" OR "exercise prescription" OR "computer vision")',
    "O1_ai_exercise": 'stroke AND ("exercise prescription" OR "personalized exercise" OR "adaptive exercise") AND ("machine learning" OR "artificial intelligence" OR "deep learning")',
    "O2_camera": 'stroke AND (Kinect OR OpenPose OR MediaPipe OR "pose estimation" OR markerless OR "computer vision" OR "depth camera") AND (rehabilitation OR kinematics OR assessment)',
}

CROSSREF_QUERIES = {
    "C0_reviews": "stroke systematic review artificial intelligence Kinect pose estimation exercise prescription",
    "C1_ai_ex": "stroke artificial intelligence exercise prescription rehabilitation machine learning",
    "C2_camera": "stroke Kinect pose estimation camera movement analysis rehabilitation",
}

CTGOV_QUERIES = {
    "T1": {
        "query.cond": "stroke",
        "query.term": "artificial intelligence OR machine learning OR pose estimation OR Kinect OR computer vision OR camera-based OR markerless",
    }
}

SEMANTIC_SCHOLAR_QUERIES = {
    "SS0": "stroke rehabilitation systematic review artificial intelligence camera pose estimation",
    "SS1": "AI exercise prescription stroke rehabilitation",
    "SS2": "Kinect OpenPose MediaPipe stroke rehabilitation validity",
}


def pubmed_search(name: str, query: str, retmax_cap: int = 2000) -> dict:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": "0",
        "tool": NCBI_TOOL,
        "email": NCBI_EMAIL,
    }
    url = base + "esearch.fcgi?" + urllib.parse.urlencode(params)
    status, body, _ = get(url)
    time.sleep(SLEEP)
    payload = json.loads(body.decode("utf-8", errors="replace")) if body else {}
    count = int(payload.get("esearchresult", {}).get("count", 0) or 0)
    webenv = payload.get("esearchresult", {}).get("webenv")
    qk = payload.get("esearchresult", {}).get("querykey")
    log_event({"source": "PubMed", "strategy": name, "url": url, "http_status": status, "hit_count": count, "query": query})

    ids: list[str] = []
    fetch_n = min(count, retmax_cap)
    for start in range(0, fetch_n, 200):
        p = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retstart": str(start),
            "retmax": str(min(200, fetch_n - start)),
            "tool": NCBI_TOOL,
            "email": NCBI_EMAIL,
        }
        u = base + "esearch.fcgi?" + urllib.parse.urlencode(p)
        st, b, _ = get(u)
        time.sleep(SLEEP)
        js = json.loads(b.decode("utf-8", errors="replace"))
        batch = js.get("esearchresult", {}).get("idlist", [])
        ids.extend(batch)
        log_event({"source": "PubMed", "strategy": name, "step": "idpage", "start": start, "n": len(batch), "http_status": st})

    records = []
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        p = {
            "db": "pubmed",
            "id": ",".join(batch),
            "retmode": "xml",
            "rettype": "abstract",
            "tool": NCBI_TOOL,
            "email": NCBI_EMAIL,
        }
        u = base + "efetch.fcgi?" + urllib.parse.urlencode(p)
        st, b, _ = get(u, timeout=120)
        time.sleep(SLEEP + 0.2)
        xml = b.decode("utf-8", errors="replace")
        records.extend(parse_pubmed_xml(xml, source_strategy=name))
        log_event({"source": "PubMed", "strategy": name, "step": "efetch", "batch_start": i, "http_status": st, "bytes": len(b)})

    out = {
        "strategy": name,
        "query": query,
        "hit_count": count,
        "retrieved": len(records),
        "capped": count > retmax_cap,
        "webenv": webenv,
        "querykey": qk,
        "retrieved_at_utc": NOW,
        "records": records,
    }
    write_json(RAW / f"pubmed_{name}.json", {k: v for k, v in out.items() if k != "records"})
    with (RAW / f"pubmed_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out


def parse_pubmed_xml(xml: str, source_strategy: str) -> list[dict]:
    # Lightweight split on PubmedArticle without requiring lxml
    articles = xml.split("<PubmedArticle>")
    recs = []
    for chunk in articles[1:]:
        def tag(name, default=""):
            m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", chunk, re.S)
            return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else default

        pmid = tag("PMID")
        title = tag("ArticleTitle")
        year = tag("Year")
        if not year:
            y = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", chunk, re.S)
            year = y.group(1) if y else ""
        journal = tag("Title")
        abstract = tag("AbstractText")
        # multiple AbstractText
        abs_parts = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", chunk, re.S)
        if abs_parts:
            abstract = " ".join(re.sub(r"<[^>]+>", "", a).strip() for a in abs_parts)
        dois = re.findall(r'<ArticleId IdType="doi">(.*?)</ArticleId>', chunk, re.I)
        pmc = re.findall(r'<ArticleId IdType="pmc">(.*?)</ArticleId>', chunk, re.I)
        ptypes = re.findall(r"<PublicationType(?: UI=\"[^\"]*\")?>(.*?)</PublicationType>", chunk)
        authors = []
        for last, fore in re.findall(r"<LastName>(.*?)</LastName>\s*<ForeName>(.*?)</ForeName>", chunk):
            authors.append(f"{last} {fore}")
        doi = dois[0] if dois else ""
        recs.append(
            {
                "source": "PubMed",
                "strategy": source_strategy,
                "pmid": pmid,
                "pmc": pmc[0] if pmc else "",
                "doi": norm_doi(doi),
                "title": title,
                "title_norm": norm_title(title),
                "year": year,
                "journal": journal,
                "authors": authors,
                "author_string": "; ".join(authors[:20]),
                "publication_types": ptypes,
                "abstract": abstract[:4000],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                "doi_url": f"https://doi.org/{norm_doi(doi)}" if doi else "",
                "verification": "verified_from_pubmed_xml",
            }
        )
    return recs


def europepmc_search(name: str, query: str, page_size: int = 100, max_pages: int = 10) -> dict:
    records = []
    hit_count = None
    for page in range(1, max_pages + 1):
        params = {
            "query": query,
            "format": "json",
            "pageSize": str(page_size),
            "cursorMark": "*" if page == 1 else "",
            "resultType": "core",
        }
        # Europe PMC uses page
        params = {
            "query": query,
            "format": "json",
            "pageSize": str(page_size),
            "page": str(page),
            "resultType": "core",
        }
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(params)
        st, b, _ = get(url, timeout=90)
        time.sleep(SLEEP)
        try:
            js = json.loads(b.decode("utf-8", errors="replace"))
        except Exception:
            log_event({"source": "EuropePMC", "strategy": name, "http_status": st, "parse_error": True, "url": url})
            break
        hit_count = int(js.get("hitCount") or 0)
        results = js.get("resultList", {}).get("result", []) or []
        log_event({"source": "EuropePMC", "strategy": name, "page": page, "http_status": st, "hit_count": hit_count, "n": len(results), "query": query if page == 1 else None})
        if not results:
            break
        for r in results:
            doi = norm_doi(r.get("doi"))
            title = r.get("title") or ""
            authors = []
            al = r.get("authorList", {}) or {}
            for a in al.get("author", []) or []:
                nm = a.get("fullName") or " ".join(filter(None, [a.get("lastName"), a.get("firstName")]))
                if nm:
                    authors.append(nm)
            pmid = str(r.get("pmid") or r.get("id") or "")
            if r.get("source") != "MED" and not r.get("pmid"):
                pmid = ""
            records.append(
                {
                    "source": "EuropePMC",
                    "strategy": name,
                    "pmid": str(r.get("pmid") or ""),
                    "pmcid": r.get("pmcid") or "",
                    "doi": doi,
                    "title": title,
                    "title_norm": norm_title(title),
                    "year": str(r.get("pubYear") or ""),
                    "journal": r.get("journalTitle") or "",
                    "authors": authors,
                    "author_string": "; ".join(authors[:20]),
                    "publication_types": [r.get("pubType")] if r.get("pubType") else [],
                    "abstract": (r.get("abstractText") or "")[:4000],
                    "url": r.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url") if isinstance(r.get("fullTextUrlList"), dict) else "",
                    "doi_url": f"https://doi.org/{doi}" if doi else (f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}" if r.get("id") else ""),
                    "epmc_id": f"{r.get('source')}:{r.get('id')}",
                    "verification": "verified_from_europepmc_api",
                }
            )
        if page * page_size >= hit_count:
            break
    write_json(RAW / f"europepmc_{name}_meta.json", {"hit_count": hit_count, "retrieved": len(records), "query": query})
    with (RAW / f"europepmc_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"strategy": name, "query": query, "hit_count": hit_count, "retrieved": len(records), "records": records}


def openalex_search(name: str, query: str, per_page: int = 50, max_pages: int = 8) -> dict:
    records = []
    meta_count = None
    cursor = "*"
    for page in range(max_pages):
        params = {
            "search": query,
            "per_page": str(per_page),
            "cursor": cursor,
            "mailto": NCBI_EMAIL,
            "select": "id,doi,title,display_name,publication_year,authorships,primary_location,type,open_access,ids,abstract_inverted_index",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        st, b, _ = get(url, timeout=90)
        time.sleep(SLEEP)
        try:
            js = json.loads(b.decode("utf-8", errors="replace"))
        except Exception:
            log_event({"source": "OpenAlex", "strategy": name, "http_status": st, "parse_error": True})
            break
        meta_count = (js.get("meta") or {}).get("count")
        results = js.get("results") or []
        log_event({"source": "OpenAlex", "strategy": name, "page": page + 1, "http_status": st, "hit_count": meta_count, "n": len(results), "query": query if page == 0 else None})
        for r in results:
            doi = norm_doi(r.get("doi"))
            title = r.get("display_name") or r.get("title") or ""
            authors = []
            for a in r.get("authorships") or []:
                nm = (a.get("author") or {}).get("display_name")
                if nm:
                    authors.append(nm)
            loc = r.get("primary_location") or {}
            src = (loc.get("source") or {}) if isinstance(loc.get("source"), dict) else {}
            ids = r.get("ids") or {}
            pmid = ""
            if ids.get("pmid"):
                pmid = str(ids["pmid"]).split("/")[-1]
            records.append(
                {
                    "source": "OpenAlex",
                    "strategy": name,
                    "pmid": pmid,
                    "openalex_id": r.get("id") or "",
                    "doi": doi,
                    "title": title,
                    "title_norm": norm_title(title),
                    "year": str(r.get("publication_year") or ""),
                    "journal": src.get("display_name") or "",
                    "authors": authors,
                    "author_string": "; ".join(authors[:20]),
                    "publication_types": [r.get("type")] if r.get("type") else [],
                    "abstract": "",
                    "url": loc.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else r.get("id") or ""),
                    "doi_url": f"https://doi.org/{doi}" if doi else "",
                    "verification": "verified_from_openalex_api",
                }
            )
        cursor = (js.get("meta") or {}).get("next_cursor")
        if not cursor or not results:
            break
    write_json(RAW / f"openalex_{name}_meta.json", {"hit_count": meta_count, "retrieved": len(records), "query": query})
    with (RAW / f"openalex_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"strategy": name, "query": query, "hit_count": meta_count, "retrieved": len(records), "records": records}


def crossref_search(name: str, query: str, rows: int = 100, max_offset: int = 300) -> dict:
    records = []
    total = None
    for offset in range(0, max_offset, rows):
        params = {
            "query": query,
            "rows": str(rows),
            "offset": str(offset),
            "select": "DOI,title,author,issued,container-title,type,URL,abstract,ISSN,published",
            "mailto": NCBI_EMAIL,
        }
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        st, b, _ = get(url, timeout=90)
        time.sleep(SLEEP + 0.2)
        try:
            js = json.loads(b.decode("utf-8", errors="replace"))
        except Exception:
            log_event({"source": "Crossref", "strategy": name, "http_status": st, "parse_error": True})
            break
        msg = js.get("message") or {}
        total = msg.get("total-results")
        items = msg.get("items") or []
        log_event({"source": "Crossref", "strategy": name, "offset": offset, "http_status": st, "hit_count": total, "n": len(items), "query": query if offset == 0 else None})
        if not items:
            break
        for it in items:
            doi = norm_doi(it.get("DOI"))
            titles = it.get("title") or [""]
            title = titles[0] if titles else ""
            authors = []
            for a in it.get("author") or []:
                nm = " ".join(filter(None, [a.get("family"), a.get("given")]))
                if nm:
                    authors.append(nm)
            year = ""
            issued = (it.get("issued") or {}).get("date-parts") or [[]]
            if issued and issued[0]:
                year = str(issued[0][0])
            journal = (it.get("container-title") or [""])[0]
            records.append(
                {
                    "source": "Crossref",
                    "strategy": name,
                    "pmid": "",
                    "doi": doi,
                    "title": title,
                    "title_norm": norm_title(title),
                    "year": year,
                    "journal": journal,
                    "authors": authors,
                    "author_string": "; ".join(authors[:20]),
                    "publication_types": [it.get("type")] if it.get("type") else [],
                    "abstract": re.sub(r"<[^>]+>", " ", it.get("abstract") or "")[:4000],
                    "url": it.get("URL") or (f"https://doi.org/{doi}" if doi else ""),
                    "doi_url": f"https://doi.org/{doi}" if doi else "",
                    "verification": "verified_from_crossref_api",
                }
            )
        if offset + rows >= (total or 0):
            break
    write_json(RAW / f"crossref_{name}_meta.json", {"hit_count": total, "retrieved": len(records), "query": query})
    with (RAW / f"crossref_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"strategy": name, "query": query, "hit_count": total, "retrieved": len(records), "records": records}


def ctgov_search(name: str, q: dict, page_size: int = 100) -> dict:
    records = []
    params = {
        "format": "json",
        "pageSize": str(page_size),
        "countTotal": "true",
        "fields": "NCTId,BriefTitle,OfficialTitle,OverallStatus,StudyType,StartDate,CompletionDate,Condition,InterventionName,InterventionType,BriefSummary,LeadSponsorName",
    }
    params.update(q)
    url = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode(params)
    st, b, _ = get(url, timeout=90)
    time.sleep(SLEEP)
    try:
        js = json.loads(b.decode("utf-8", errors="replace"))
    except Exception:
        log_event({"source": "ClinicalTrials.gov", "strategy": name, "http_status": st, "parse_error": True, "url": url})
        return {"strategy": name, "hit_count": None, "retrieved": 0, "records": [], "error": True}
    total = js.get("totalCount")
    studies = js.get("studies") or []
    log_event({"source": "ClinicalTrials.gov", "strategy": name, "http_status": st, "hit_count": total, "n": len(studies), "query": q})
    token = js.get("nextPageToken")
    studies_all = list(studies)
    while token and len(studies_all) < 500:
        params2 = dict(params)
        params2["pageToken"] = token
        url2 = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode(params2)
        st2, b2, _ = get(url2, timeout=90)
        time.sleep(SLEEP)
        js2 = json.loads(b2.decode("utf-8", errors="replace"))
        batch = js2.get("studies") or []
        studies_all.extend(batch)
        token = js2.get("nextPageToken")
        log_event({"source": "ClinicalTrials.gov", "strategy": name, "http_status": st2, "page_n": len(batch)})
        if not batch:
            break
    for s in studies_all:
        proto = (s.get("protocolSection") or {})
        ident = proto.get("identificationModule") or {}
        status = proto.get("statusModule") or {}
        design = proto.get("designModule") or {}
        desc = proto.get("descriptionModule") or {}
        nct = ident.get("nctId") or ""
        title = ident.get("briefTitle") or ident.get("officialTitle") or ""
        records.append(
            {
                "source": "ClinicalTrials.gov",
                "strategy": name,
                "pmid": "",
                "nct_id": nct,
                "doi": "",
                "title": title,
                "title_norm": norm_title(title),
                "year": str((status.get("startDateStruct") or {}).get("date") or "")[:4],
                "journal": "ClinicalTrials.gov",
                "authors": [((proto.get("sponsorCollaboratorsModule") or {}).get("leadSponsor") or {}).get("name") or ""],
                "author_string": ((proto.get("sponsorCollaboratorsModule") or {}).get("leadSponsor") or {}).get("name") or "",
                "publication_types": [design.get("studyType") or "trial_registration"],
                "abstract": (desc.get("briefSummary") or "")[:4000],
                "url": f"https://clinicaltrials.gov/study/{nct}" if nct else "",
                "doi_url": "",
                "study_status": status.get("overallStatus") or "",
                "verification": "verified_from_clinicaltrials_gov_api",
            }
        )
    write_json(RAW / f"ctgov_{name}_meta.json", {"hit_count": total, "retrieved": len(records), "query": q})
    with (RAW / f"ctgov_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"strategy": name, "query": q, "hit_count": total, "retrieved": len(records), "records": records}


def s2_search(name: str, query: str, limit: int = 100) -> dict:
    params = {
        "query": query,
        "limit": str(min(limit, 100)),
        "fields": "title,year,authors,externalIds,publicationTypes,abstract,url,venue,publicationDate",
    }
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    st, b, _ = get(url, timeout=90)
    time.sleep(1.0)
    records = []
    total = None
    try:
        js = json.loads(b.decode("utf-8", errors="replace"))
    except Exception:
        log_event({"source": "SemanticScholar", "strategy": name, "http_status": st, "parse_error": True, "body": b[:300].decode("utf-8", "replace")})
        return {"strategy": name, "query": query, "hit_count": None, "retrieved": 0, "records": [], "error": True, "http_status": st}
    total = js.get("total")
    for r in js.get("data") or []:
        ext = r.get("externalIds") or {}
        doi = norm_doi(ext.get("DOI"))
        pmid = str(ext.get("PubMed") or "")
        title = r.get("title") or ""
        authors = [a.get("name") for a in (r.get("authors") or []) if a.get("name")]
        records.append(
            {
                "source": "SemanticScholar",
                "strategy": name,
                "pmid": pmid,
                "s2_id": r.get("paperId") or "",
                "doi": doi,
                "title": title,
                "title_norm": norm_title(title),
                "year": str(r.get("year") or ""),
                "journal": r.get("venue") or "",
                "authors": authors,
                "author_string": "; ".join(authors[:20]),
                "publication_types": r.get("publicationTypes") or [],
                "abstract": (r.get("abstract") or "")[:4000],
                "url": r.get("url") or "",
                "doi_url": f"https://doi.org/{doi}" if doi else "",
                "verification": "verified_from_semanticscholar_api" if st == 200 else "unverified_s2_error",
            }
        )
    log_event({"source": "SemanticScholar", "strategy": name, "http_status": st, "hit_count": total, "retrieved": len(records), "query": query})
    write_json(RAW / f"s2_{name}_meta.json", {"hit_count": total, "retrieved": len(records), "query": query, "http_status": st})
    with (RAW / f"s2_{name}.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"strategy": name, "query": query, "hit_count": total, "retrieved": len(records), "records": records, "http_status": st}


def prospero_search() -> dict:
    """PROSPERO has no stable public JSON API. Attempt HTML search endpoints and record access status."""
    queries = [
        "stroke artificial intelligence rehabilitation",
        "stroke pose estimation",
        "stroke Kinect rehabilitation",
        "stroke exercise prescription artificial intelligence",
        "stroke computer vision rehabilitation",
        "stroke markerless motion",
    ]
    results = []
    for q in queries:
        url = "https://www.crd.york.ac.uk/prospero/search.asp?" + urllib.parse.urlencode({"mode": "input", "criteria": q})
        # newer UI
        url2 = "https://www.crd.york.ac.uk/PROSPERO/#searchadvanced"
        st, b, ctype = get(
            "https://www.crd.york.ac.uk/prospero/rest/api/search?" + urllib.parse.urlencode({"q": q}),
            timeout=30,
        )
        time.sleep(0.5)
        log_event({"source": "PROSPERO", "attempt": "rest_api_search", "query": q, "http_status": st, "content_type": ctype, "bytes": len(b)})
        results.append({"query": q, "http_status": st, "bytes": len(b), "snippet": b[:200].decode("utf-8", "replace")})
    # known record fetched earlier
    known = ["CRD42022323670", "CRD420323670"]
    for crd in ["CRD42022323670"]:
        u = f"https://www.crd.york.ac.uk/PROSPERO/view/{crd.replace('CRD','')}" if False else f"https://www.crd.york.ac.uk/prospero/display_record.php?ID={crd}"
        st, b, _ = get(u, timeout=30)
        log_event({"source": "PROSPERO", "attempt": "display_record", "id": crd, "http_status": st, "bytes": len(b)})
        results.append({"id": crd, "url": u, "http_status": st})
    write_json(RAW / "prospero_access.json", {"note": "No public bulk API confirmed", "attempts": results})
    return {"source": "PROSPERO", "access": "limited_html_only", "attempts": results}


def main():
    if LOG.exists():
        LOG.unlink()
    summary = {"run_started_utc": NOW, "sources": []}
    all_records = []

    for name, spec in PUBMED_STRATEGIES.items():
        print(f"PubMed {name}...", flush=True)
        out = pubmed_search(name, spec["query"], retmax_cap=1500 if name != "S0_novelty_reviews" else 800)
        summary["sources"].append({"source": "PubMed", "strategy": name, "hit_count": out["hit_count"], "retrieved": out["retrieved"], "capped": out.get("capped")})
        all_records.extend(out["records"])

    for name, q in EUROPEPMC_QUERIES.items():
        print(f"EuropePMC {name}...", flush=True)
        out = europepmc_search(name, q)
        summary["sources"].append({"source": "EuropePMC", "strategy": name, "hit_count": out["hit_count"], "retrieved": out["retrieved"]})
        all_records.extend(out["records"])

    for name, q in OPENALEX_QUERIES.items():
        print(f"OpenAlex {name}...", flush=True)
        out = openalex_search(name, q)
        summary["sources"].append({"source": "OpenAlex", "strategy": name, "hit_count": out["hit_count"], "retrieved": out["retrieved"]})
        all_records.extend(out["records"])

    for name, q in CROSSREF_QUERIES.items():
        print(f"Crossref {name}...", flush=True)
        out = crossref_search(name, q, rows=100, max_offset=200)
        summary["sources"].append({"source": "Crossref", "strategy": name, "hit_count": out["hit_count"], "retrieved": out["retrieved"]})
        all_records.extend(out["records"])

    for name, q in CTGOV_QUERIES.items():
        print(f"CT.gov {name}...", flush=True)
        out = ctgov_search(name, q)
        summary["sources"].append({"source": "ClinicalTrials.gov", "strategy": name, "hit_count": out["hit_count"], "retrieved": out["retrieved"]})
        all_records.extend(out["records"])

    for name, q in SEMANTIC_SCHOLAR_QUERIES.items():
        print(f"S2 {name}...", flush=True)
        out = s2_search(name, q)
        summary["sources"].append({"source": "SemanticScholar", "strategy": name, "hit_count": out.get("hit_count"), "retrieved": out["retrieved"], "http_status": out.get("http_status")})
        all_records.extend(out["records"])

    print("PROSPERO access probe...", flush=True)
    pr = prospero_search()
    summary["sources"].append({"source": "PROSPERO", "access": pr.get("access")})

    summary["run_finished_utc"] = datetime.now(timezone.utc).isoformat()
    summary["raw_record_rows"] = len(all_records)
    write_json(RAW / "search_run_summary.json", summary)

    # dump combined pre-dedup
    fields = [
        "source", "strategy", "pmid", "doi", "nct_id", "title", "year", "journal",
        "author_string", "publication_types", "url", "doi_url", "verification",
        "title_norm", "abstract",
    ]
    with (RAW / "all_raw_records.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in all_records:
            row = dict(r)
            if isinstance(row.get("publication_types"), list):
                row["publication_types"] = "|".join(str(x) for x in row["publication_types"] if x)
            w.writerow(row)
    write_json(RAW / "all_raw_records_lite.json", [{"source": r.get("source"), "strategy": r.get("strategy"), "pmid": r.get("pmid"), "doi": r.get("doi"), "title": r.get("title"), "year": r.get("year")} for r in all_records])
    print(f"Done. raw rows={len(all_records)}", flush=True)


if __name__ == "__main__":
    main()
