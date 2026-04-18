import logging
import feedparser
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class JobEntry:
    title: str
    link: str
    published: str
    summary: str


def parse_rss_feed(url: str) -> list[JobEntry]:
    log.debug("Parsing RSS feed: %s", url)
    feed = feedparser.parse(url)
    if feed.bozo:
        log.warning("Feed parse warning for %s: %s", url, feed.bozo_exception)
    log.debug("Feed title: %s", feed.feed.get("title", "unknown"))
    return [
        JobEntry(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            published=entry.get("published", ""),
            summary=entry.get("summary", ""),
        )
        for entry in feed.entries
    ]
