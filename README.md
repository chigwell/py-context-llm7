[![PyPI version](https://badge.fury.io/py/py-context-llm7.svg)](https://badge.fury.io/py/py-context-llm7)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/py-context-llm7)](https://pepy.tech/project/py-context-llm7)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# py-context-llm7

`py-context-llm7` is a minimal Python client for the `https://api.context.llm7.io` service.
It lets you authenticate, manage **projects** and **contexts**, and **search** (retrieve relevant context for a query) with a tiny, dependency‑light API (built on `requests`).

---

## Installation

```bash
pip install py-context-llm7
```

---

## Quickstart

### Authenticate with a **personal token**

```python
import os
import time

from py_context_llm7 import ContextClient

client = ContextClient(bearer=os.environ["CONTEXT_TOKEN"])

print(client.me())
# {'user_id': '...', 'email': '...'}

pid = client.create_project_and_fetch_id("My project")
client.add_context(pid, "The capital of France is Paris.")
client.add_context(pid, "The capital of Germany is Berlin.")
client.add_context(pid, "The capital of Italy is Rome.")
client.add_context(pid, "The capital of Spain is Madrid.")
client.add_context(pid, "The capital of Portugal is Lisbon.")
client.add_context(pid, "The capital of the Netherlands is Amsterdam.")
client.add_context(pid, "The capital of Belgium is Brussels.")
client.add_context(pid, "The capital of Greece is Athens.")
client.add_context(pid, "The capital of Sweden is Stockholm.")

print(client.list_projects())
print(client.list_contexts(pid))

print(f"pid: {pid}")
time.sleep(5)  # allow a short delay for vector indexing

print(client.search(pid, "What is the capital of Italy?"))
# Example:
# {'context': 'The capital of Portugal is Lisbon.\nThe capital of Germany is Berlin.\nThe capital of Spain is Madrid.\nThe capital of Italy is Rome.\nThe capital of France is Paris.', 'query': 'What is the capital of Italy?'}
```

### First‑time setup via **Google ID token → app JWT → personal token**


Visit https://context.llm7.io/ and log in with your Google account. This will create an app JWT for you.

Then, you will be able to create a free token for API.


## Features

* **Simple auth**: Use a personal token directly or exchange a Google ID token for an app JWT.
* **Project management**: List, create, and delete projects.
* **Context management**: Add, list, and delete contexts (with a helper to delete by `vector_id`).
* **Search**: Query for relevant context across your stored items.
* **Minimal deps**: Only `requests`.
* **Clear errors**: Raises `ContextAPIError(status, message)` on non‑2xx responses.

---

## API Overview

```python
from py_context_llm7 import ContextClient, ContextAPIError
```

### Construction

* `ContextClient(base_url="https://api.context.llm7.io", bearer=None, timeout=30)`

### Auth

* `set_bearer(token: str) -> None`
  Set an app JWT or personal token.

* `verify_google_id_token(id_token: str) -> dict`
  GET `/verify?token=...` → returns `{"email": str, "token": "<app_jwt>"}` and sets bearer.

* `list_tokens() -> list[dict]` *(requires app JWT)*

* `create_personal_token(set_as_current: bool = True) -> dict` *(requires app JWT)*

* `delete_token(token_id: int) -> dict` *(requires app JWT)*

### User

* `me() -> dict`
  GET `/me` → `{"user_id": str, "email": str}`.

### Projects

* `list_projects() -> list[dict]`
* `create_project(name: str) -> dict`
* `create_project_and_fetch_id(name: str) -> int` *(create then re‑list; newest id)*
* `delete_project(project_id: int) -> dict`

### Contexts

* `list_contexts(project_id: int) -> list[dict]`
  Returns items like `{"id": int, "source": str, "vector_id": str}`.

* `add_context(project_id: int, source: str) -> dict`
  Returns `{"status": "added", "vector_id": "..."}`.

* `delete_context(project_id: int, context_id: int) -> dict`

* `delete_context_by_vector_id(project_id: int, vector_id: str) -> dict`

### Search

* `search(project_id: int, query: str) -> dict`
  Returns `{"context": "<joined sources>", "query": "..."}`.

### Error Handling

```python
try:
    client.add_context(pid, "Some text")
except ContextAPIError as e:
    print(e.status, e.message)
```

---

## Tips

* **Indexing delay:** after adding contexts, wait briefly (e.g., 2–5 seconds) before searching so the vectors are indexed.
* **Base URL:** override `base_url` if you run a self‑hosted deployment.
* **Security:** keep both app JWTs and personal tokens secret.

---

## Contributing

Issues and PRs are welcome. Please open them on the repo:

* Issues: [https://github.com/chigwell/py-context-llm7/issues](https://github.com/chigwell/py-context-llm7/issues)
* Source: [https://github.com/chigwell/py-context-llm7](https://github.com/chigwell/py-context-llm7)

---

## License

`py-context-llm7` is released under the [MIT License](https://choosealicense.com/licenses/mit/).

---

## Support

Email: **[support@llm7.io](mailto:support@llm7.io)**
