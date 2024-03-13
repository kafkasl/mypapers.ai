from glob import glob
import json
from datasets import Dataset

# Function to load all documents from the specified directory
def load_documents(directory_path: str) -> list:
    files = glob(f"{directory_path}/*.json")
    documents = []
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as file:
            documents.append(json.load(file))
    return documents

# Load documents from the './papers' directory
data = load_documents("./papers")

# len(data[0]["content"])

"""Then we must format it into the format we need (`["id", "text", "source", "metadata"]`):"""
data = list(map(lambda x: {
    "id": x.get("id", ""),
    "text": x.get("content", ""),
    "source": x.get("source", ""),
    "metadata": {
        "title": x.get("title", ""),
        "primary_category": x.get("primary_category", ""),
        "published": x.get("published", ""),
        "updated": x.get("updated", ""),
    }
}, data))

import json

def save_entries_to_separate_jsonl(data: list, directory_path: str) -> None:
    for entry in data:
        file_path = f"{directory_path}/{entry['id']}.jsonl"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f)

def save_to_jsonl(data: list, file_path: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')


save_to_jsonl(data, f"./papers/papers_{len(data)}.jsonl")
# save_entries_to_separate_jsonl(data, "./papers")

"""## Jump into Canopy!

From here we can switch across to Canopy CLI (or other method) and run:

```
canopy
canopy upsert ./papers/papers.jsonl
```

Then we begin chatting by first starting the Canopy Server:

```
canopy start
```

Then begin chatting with:

```
canopy chat
```

_(we can also add the `--no-rag` flag to see how our RAG vs. non-RAG results compare!)_
"""