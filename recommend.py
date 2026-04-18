import math
import sys

import gel as edgedb

from ingestion.embedder import embed

_client = edgedb.create_client()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def recommend(query: str, limit: int = 5):
    query_embedding = embed(query)

    jobs = _client.query(
        """
        select JobOpportunity {
            title, company, location, is_remote,
            job_type, seniority, skills, salary_range, link, embedding
        }
        """
    )

    ranked = sorted(
        jobs,
        key=lambda j: _cosine_similarity(query_embedding, list(j.embedding)),
        reverse=True,
    )

    for job in ranked[:limit]:
        score = _cosine_similarity(query_embedding, list(job.embedding))
        print(f"Title:     {job.title}")
        print(f"Company:   {job.company}")
        print(f"Location:  {job.location} ({'remote' if job.is_remote else 'on-site'})")
        print(f"Seniority: {job.seniority}  |  Type: {job.job_type}")
        print(f"Skills:    {', '.join(job.skills)}")
        print(f"Salary:    {job.salary_range or 'N/A'}")
        print(f"Link:      {job.link}")
        print(f"Score:     {score:.3f}")
        print("-" * 60)


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "remote senior software engineer"
    print(f"Finding jobs for: {query}\n")
    recommend(query)
