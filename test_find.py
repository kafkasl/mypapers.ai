import pytest
import json
from find import search, search_by_title, search_by_author, search_by_id

def format_results(results):
    # Format the results to a consistent structure for snapshot testing
    return [
        {"id": r.entry_id.split('/')[-1], "title": r.title}
        for r in results
    ]

def test_search(snapshot):
    query = "test query"
    results = search(query)
    formatted_results = format_results(results)
    # Serialize to JSON string
    results_json = json.dumps(formatted_results, sort_keys=True, indent=4)
    snapshot.assert_match(results_json, f'search_{query}.snapshot')

def test_search_by_title(snapshot):
    title = "test title"
    results = search_by_title(title)
    formatted_results = format_results(results)
    # Serialize to JSON string
    results_json = json.dumps(formatted_results, sort_keys=True, indent=4)
    snapshot.assert_match(results_json, f'search_by_title_{title}.snapshot')

def test_search_by_author(snapshot):
    author = "test author"
    results = search_by_author(author)
    formatted_results = format_results(results)
    # Serialize to JSON string
    results_json = json.dumps(formatted_results, sort_keys=True, indent=4)
    snapshot.assert_match(results_json, f'search_by_author_{author}.snapshot')

def test_search_by_id(snapshot):
    paper_id = "1234.5678"
    results = search_by_id(paper_id)
    formatted_results = format_results(results)
    # Serialize to JSON string
    results_json = json.dumps(formatted_results, sort_keys=True, indent=4)
    snapshot.assert_match(results_json, f'search_by_id_{paper_id}.snapshot')
