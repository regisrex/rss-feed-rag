import json
import math
import sys

import gel as edgedb
from ollama import Client

from ingestion.embedder import embed

_db = edgedb.create_client()
_llm = Client(host="http://207.102.87.207:53635")

_REASONING_PROMPT = """\
A user is looking for a job. Your task is to analyze the candidates and reason \
about which ones are the best fit.

User query: {query}

Candidates:
{candidates}

For each candidate, reason about:
- How well it matches the query
- Any strengths or concerns
- A fit score from 0.0 to 1.0

Return a JSON array ordered from best to worst fit:
[
  {{
    "rank": 1,
    "title": "...",
    "company": "...",
    "fit_score": 0.95,
    "reasoning": "This role matches because..."
  }},
  ...
]
"""


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _format_candidates(jobs) -> str:
    lines = []
    for i, job in enumerate(jobs, 1):
        lines.append(
            f"{i}. {job.title} @ {job.company}\n"
            f"   Location: {job.location} | Remote: {job.is_remote}\n"
            f"   Type: {job.job_type} | Seniority: {job.seniority}\n"
            f"   Skills: {', '.join(job.skills)}\n"
            f"   Salary: {job.salary_range or 'N/A'}"
        )
    return "\n\n".join(lines)


def search(query: str, retrieve: int = 10, show: int = 5):
    print(f"[1/3] Embedding query...")
    query_embedding = embed(query)

    print(f"[2/3] Retrieving top {retrieve} candidates by vector similarity...")
    all_jobs = _db.query(
        """
        select JobOpportunity {
            title, company, location, is_remote,
            job_type, seniority, skills, salary_range, link, embedding
        }
        """
    )

    candidates = sorted(
        all_jobs,
        key=lambda j: _cosine_similarity(query_embedding, list(j.embedding)),
        reverse=True,
    )[:retrieve]

    if not candidates:
        print("No jobs found in the database. Run `python -m ingestion` first.")
        return

    print(f"[3/3] Reasoning over {len(candidates)} candidates with llama3.2...")
    prompt = _REASONING_PROMPT.format(
        query=query,
        candidates=_format_candidates(candidates),
    )

    response = _llm.chat(
        model="gpt-oss:20b",
        messages=[{"role": "user", "content": prompt}],
        format="json",
    )

    data = json.loads(response.message.content)
    # LLM sometimes wraps the array in an object e.g. {"results": [...]}
    ranked = data if isinstance(data, list) else next(
        (v for v in data.values() if isinstance(v, list)), []
    )

    # build a lookup to enrich ranked results with full job data
    job_index = {(j.title, j.company): j for j in candidates}

    print(f"\nTop {show} results for: \"{query}\"\n" + "=" * 60)
    for item in ranked[:show]:
        job = job_index.get((item.get("title"), item.get("company")))
        print(f"#{item.get('rank', '?')}  {item.get('title')} @ {item.get('company')}")
        if job:
            print(f"    Location:  {job.location} ({'remote' if job.is_remote else 'on-site'})")
            print(f"    Seniority: {job.seniority}  |  Type: {job.job_type}")
            print(f"    Skills:    {', '.join(job.skills)}")
            print(f"    Salary:    {job.salary_range or 'N/A'}")
            print(f"    Link:      {job.link}")
        fit = item.get("fit_score")
        print(f"    Fit score: {fit:.2f}" if isinstance(fit, float) else "    Fit score: N/A")
        print(f"    Reasoning: {item.get('reasoning', '')}")
        print("-" * 60)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "remote finance role, no experience required"
    search(query)
