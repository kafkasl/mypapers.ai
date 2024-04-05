# mypapers.ai

Creation and querying of a knowledge graph built from academic papers. It automates the process of downloading papers, setting up a Neo4j database, ingesting the papers into the database, and querying the knowledge graph for insights.

[Follow me](https://x.com/pol_avec) while I build this project in public on [X](https://twitter.com/pol_avec/status/1776094859750985789)

The instructions below are a WIP.


## 1. Download papers

This will download a list of papers and their references into json format.
`python download.py`

## 2. Setup Neo4j

See this [X thread](https://x.com/pol_avec/status/1769365996115202298)

## 3. Ingest papers

`./knowledge_graph/ingest_papers.sh`

This will add a list of papers downloaded in 1. into the neo4j database.

## 4. Query the knowledge graph

`python knowledge_graph/advanced_queries.py 'Summarize papers written by Oriol Vinyals'`