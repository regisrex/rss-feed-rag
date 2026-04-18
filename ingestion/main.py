import logging

from ingestion.embedder import embed, opportunity_to_text
from ingestion.labeler import label
from ingestion.sources.rss import parse_rss_feed
from ingestion.store import save_opportunity

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def run():
    RSS_FEEDS = [
        "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"
    ]

    for feed_url in RSS_FEEDS:
        log.info("Fetching feed: %s", feed_url)
        entries = parse_rss_feed(feed_url)
        log.info("Found %d entries", len(entries))

        for i, entry in enumerate(entries, 1):
            log.info("[%d/%d] Labeling: %s", i, len(entries), entry.title)
            opportunity = label(entry)

            log.info("[%d/%d] Embedding: %s @ %s", i, len(entries), opportunity.title, opportunity.company)
            embedding = embed(opportunity_to_text(opportunity))

            log.info("[%d/%d] Saving to DB", i, len(entries))
            save_opportunity(opportunity, embedding, link=entry.link, published=entry.published)

            log.info("[%d/%d] Done: %s @ %s", i, len(entries), opportunity.title, opportunity.company)
