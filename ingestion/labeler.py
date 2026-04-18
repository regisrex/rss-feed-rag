import json
import logging
from dataclasses import dataclass

from ollama import Client

from ingestion.sources.rss import JobEntry

log = logging.getLogger(__name__)

_client = Client(host="http://207.102.87.207:53635")

_PROMPT = """\
Extract structured information from this job listing and return valid JSON.

Title: {title}
Summary: {summary}

Return a JSON object with exactly these fields:
{{
  "title": "job title",
  "company": "company name, or 'Unknown' if not found",
  "location": "city/country, or 'Remote' if fully remote",
  "is_remote": true or false,
  "job_type": "full-time" | "part-time" | "contract",
  "seniority": "junior" | "mid" | "senior" | "lead" | "unknown",
  "required_skills": ["skill1", "skill2"],
  "salary_range": "e.g. $80k-$120k, or empty string if unknown"
}}"""


@dataclass
class Opportunity:
    title: str
    company: str
    location: str
    is_remote: bool
    job_type: str
    seniority: str
    required_skills: list[str]
    salary_range: str


def label(entry: JobEntry) -> Opportunity:
    log.debug("Sending to llama3.2: %s", entry.title)
    response = _client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": _PROMPT.format(title=entry.title, summary=entry.summary),
            }
        ],
        format="json",
    )
    data = json.loads(response.message.content)
    log.debug("Labeled: %s", data)
    return Opportunity(
        title=data.get("title", entry.title),
        company=data.get("company", "Unknown"),
        location=data.get("location", ""),
        is_remote=bool(data.get("is_remote", False)),
        job_type=data.get("job_type", "full-time"),
        seniority=data.get("seniority", "unknown"),
        required_skills=data.get("required_skills", []),
        salary_range=data.get("salary_range", ""),
    )
