import logging

from ollama import Client

from ingestion.labeler import Opportunity

log = logging.getLogger(__name__)
_client = Client(host="http://207.102.87.207:53635")


def embed(text: str) -> list[float]:
    log.debug("Embedding text (%d chars)", len(text))
    response = _client.embed(model="nomic-embed-text", input=text)
    vector = response.embeddings[0]
    log.debug("Got vector of length %d", len(vector))
    return vector


def opportunity_to_text(opportunity: Opportunity) -> str:
    """Converts an opportunity into a single string for embedding."""
    skills = ", ".join(opportunity.required_skills)
    return (
        f"{opportunity.title} at {opportunity.company}. "
        f"Location: {opportunity.location}. "
        f"Remote: {opportunity.is_remote}. "
        f"Type: {opportunity.job_type}. "
        f"Seniority: {opportunity.seniority}. "
        f"Skills: {skills}. "
        f"Salary: {opportunity.salary_range}."
    )
