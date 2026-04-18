# jobs-rag

A job recommendation engine that ingests RSS feeds, extracts structured data with an LLM, embeds listings with a text embedding model, stores them in Gel (EdgeDB), and surfaces results via vector similarity or LLM-powered reasoning search.

## Architecture

```
RSS Feed
   ↓
parse_rss_feed()       →  JobEntry (title, link, summary, published)
   ↓
label()                →  Opportunity (structured fields via llama3.2)
   ↓
embed()                →  vector[768] (nomic-embed-text)
   ↓
Gel (EdgeDB)           →  stores Opportunity + embedding
   ↓
recommend / search     →  cosine similarity  |  LLM reasoning
```

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/)
- [Gel CLI](https://geldata.com/docs/intro/cli)
- Ollama server with `llama3.2` and `nomic-embed-text` pulled

## Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Configure Ollama host

The Ollama server is configured in two places:

| File | Variable | Purpose |
|------|----------|---------|
| `ingestion/labeler.py` | `_client` host | LLM labeling (llama3.2) |
| `ingestion/embedder.py` | `_client` host | Embeddings (nomic-embed-text) |
| `reasoned-recommend.py` | `_llm` host | LLM reasoning search |

Update the host URLs to point at your Ollama instance.

### 3. Initialize the database

```bash
# Initialize a local Gel instance for this project
gel project init

# Apply migrations (creates the JobOpportunity type)
gel migrate
```

### 4. Ingest jobs

Fetches RSS feeds, labels each listing with the LLM, embeds it, and upserts into Gel.

```bash
poetry run python -m ingestion
```

Output per entry:
```
20:49:21 [INFO] ingestion.main: [1/25] Labeling: Finance Expert - Portfolio Management
20:49:26 [INFO] ingestion.main: [1/25] Embedding: Finance Expert @ xAI
20:49:27 [INFO] ingestion.main: [1/25] Saving to DB
20:49:27 [INFO] ingestion.main: [1/25] Done: Finance Expert @ xAI
```

## Usage

### Vector similarity search (fast)

Embeds the query and returns the closest matches by cosine similarity.

```bash
poetry run python recommend.py "remote senior finance role"
```

### Reasoning search (slower, with explanations)

Retrieves the top N candidates by vector similarity, then passes them to the LLM to reason about fit and re-rank with explanations.

```bash
poetry run python reasoned-recommend.py "200k on-site software engineering job"
```

Output includes a fit score and reasoning per result:
```
#1  Finance Manager @ Acme Corp
    Location:  New York (on-site)
    Seniority: senior  |  Type: full-time
    Skills:    Excel, SQL, Financial Modeling
    Fit score: 0.87
    Reasoning: Strong match — senior finance role in a major city...
```

## Project structure

```
jobs-rag/
├── dbschema/
│   ├── default.gel          # Gel schema
│   └── migrations/          # Applied migrations
├── ingestion/
│   ├── __main__.py          # Entry point: python -m ingestion
│   ├── main.py              # Pipeline orchestration
│   ├── labeler.py           # LLM structured extraction (llama3.2)
│   ├── embedder.py          # Text embeddings (nomic-embed-text)
│   ├── store.py             # Gel upsert
│   └── sources/
│       └── rss.py           # RSS parsing
├── recommend.py             # Vector similarity search
└── reasoned-recommend.py    # LLM reasoning search
```

## Adding more RSS feeds

Edit `RSS_FEEDS` in `ingestion/main.py`:

```python
RSS_FEEDS = [
    "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss",
    "https://example.com/jobs.rss",
]
```

Re-run `poetry run python -m ingestion` — existing entries are upserted by link, so no duplicates.
