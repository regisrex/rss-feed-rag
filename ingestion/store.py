import logging

import gel as edgedb

from ingestion.labeler import Opportunity

log = logging.getLogger(__name__)
_client = edgedb.create_client()


def save_opportunity(opportunity: Opportunity, embedding: list[float], link: str, published: str) -> None:
    log.debug("Upserting %s (link: %s)", opportunity.title, link)
    _client.query(
        """
        insert JobOpportunity {
            title := <str>$title,
            company := <str>$company,
            location := <str>$location,
            is_remote := <bool>$is_remote,
            job_type := <str>$job_type,
            seniority := <str>$seniority,
            skills := <array<str>>$skills,
            salary_range := <str>$salary_range,
            link := <str>$link,
            published := <str>$published,
            embedding := <array<float32>>$embedding,
        }
        unless conflict on .link
        else (
            update JobOpportunity set {
                title := <str>$title,
                company := <str>$company,
                location := <str>$location,
                is_remote := <bool>$is_remote,
                job_type := <str>$job_type,
                seniority := <str>$seniority,
                skills := <array<str>>$skills,
                salary_range := <str>$salary_range,
                embedding := <array<float32>>$embedding,
            }
        )
        """,
        title=opportunity.title,
        company=opportunity.company,
        location=opportunity.location,
        is_remote=opportunity.is_remote,
        job_type=opportunity.job_type,
        seniority=opportunity.seniority,
        skills=opportunity.required_skills,
        salary_range=opportunity.salary_range,
        link=link,
        published=published,
        embedding=embedding,
    )
    log.debug("Upsert complete for %s", opportunity.title)
