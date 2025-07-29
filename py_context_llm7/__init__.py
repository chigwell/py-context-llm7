# pyright: strict
# ruff: noqa
# Requires: requests
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import requests


class ContextAPIError(RuntimeError):
    """Raised on non-2xx responses with the API's error message."""

    def __init__(self, status: int, message: str):
        super().__init__(f"{status}: {message}")
        self.status = status
        self.message = message


@dataclass
class ContextClient:
    """
    Minimal client for https://api.context.llm7.io/.

    - If you already have a personal token, pass it as `bearer`.
    - If you have a Google ID token, call `verify_google_id_token(...)`
      to obtain an app JWT; then optionally call `create_personal_token(...)`.
    """

    base_url: str = "https://api.context.llm7.io"
    bearer: Optional[str] = None
    timeout: int = 30

    # ---------- internal ----------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Any:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        headers: Dict[str, str] = {"accept": "application/json"}
        if require_auth:
            if not self.bearer:
                raise ContextAPIError(401, "Missing bearer token; call set_bearer(...)")
            headers["Authorization"] = f"Bearer {self.bearer}"
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=self.timeout,
        )
        if 200 <= resp.status_code < 300:
            if resp.content:
                return resp.json()
            return None
        try:
            data = resp.json()
            msg = str(data.get("error") or data)
        except Exception:
            msg = resp.text or resp.reason
        raise ContextAPIError(resp.status_code, msg)

    # ---------- auth ----------

    def set_bearer(self, token: str) -> None:
        """Set bearer (app JWT or personal token)."""
        self.bearer = token

    def verify_google_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Exchange a Google ID token for an **app JWT** via GET /verify?token=...
        Returns: {"email": "...", "token": "<app_jwt>"}
        """
        data = self._request(
            "GET",
            "/verify",
            params={"token": id_token},
            require_auth=False,
        )
        # Set bearer to the app JWT so follow-ups (like /tokens) work.
        tok = str(data.get("token") or "")
        if not tok:
            raise ContextAPIError(502, "verify returned no token")
        self.bearer = tok
        return data

    # The /tokens endpoints require that you're authenticated with **app JWT**
    # (not a personal token). The server enforces this.

    def list_tokens(self) -> List[Dict[str, Any]]:
        """GET /tokens -> list of {"id": int, "token": str} (requires app JWT)."""
        return self._request("GET", "/tokens")

    def create_personal_token(self, set_as_current: bool = True) -> Dict[str, Any]:
        """
        POST /tokens -> {"id": int, "token": str} (requires app JWT).
        If set_as_current=True, switches this client to use the new personal token.
        """
        data = self._request("POST", "/tokens")
        token = str(data.get("token") or "")
        if not token:
            raise ContextAPIError(502, "token creation returned no token")
        if set_as_current:
            self.bearer = token
        return data

    def delete_token(self, token_id: int) -> Dict[str, Any]:
        """DELETE /tokens with {"id": token_id} (requires app JWT)."""
        return self._request("DELETE", "/tokens", json={"id": token_id})

    # ---------- user ----------

    def me(self) -> Dict[str, Any]:
        """GET /me -> {"user_id": str, "email": str}."""
        return self._request("GET", "/me")

    # ---------- projects ----------

    def list_projects(self) -> List[Dict[str, Any]]:
        """GET /projects -> [{"id": int, "name": str, "namespace": str}, ...]."""
        return self._request("GET", "/projects")

    def create_project(self, name: str) -> Dict[str, Any]:
        """POST /projects with {"name": name} -> {"status": "created"}."""
        return self._request("POST", "/projects", json={"name": name})

    def create_project_and_fetch_id(self, name: str) -> int:
        """
        Convenience: create project then re-list and return the newest project's id.
        Server returns only {"status": "created"}, so we pick the top-most item.
        """
        self.create_project(name)
        projects = self.list_projects()
        if not projects:
            raise ContextAPIError(502, "No projects after creation")
        # API orders by id DESC, so the first one is the newest.
        return int(projects[0]["id"])

    def delete_project(self, project_id: int) -> Dict[str, Any]:
        """DELETE /projects with {"project_id": id} -> {"status":"deleted"}."""
        return self._request("DELETE", "/projects", json={"project_id": project_id})

    # ---------- contexts ----------

    def list_contexts(self, project_id: int) -> List[Dict[str, Any]]:
        """
        GET /contexts?project_id=... -> [{"id": int, "source": str, "vector_id": str}, ...]
        """
        return self._request("GET", "/contexts", params={"project_id": project_id})

    def add_context(self, project_id: int, source: str) -> Dict[str, Any]:
        """
        POST /contexts with {"project_id": id, "source": text}
        -> {"status":"added","vector_id":"..."}
        """
        return self._request(
            "POST", "/contexts", json={"project_id": project_id, "source": source}
        )

    def delete_context(self, project_id: int, context_id: int) -> Dict[str, Any]:
        """DELETE /contexts with {"project_id": id, "context_id": id}."""
        return self._request(
            "DELETE",
            "/contexts",
            json={"project_id": project_id, "context_id": context_id},
        )

    def delete_context_by_vector_id(self, project_id: int, vector_id: str) -> Dict[str, Any]:
        """
        Helper: find a context by its vector_id and delete it.
        This is useful because add_context returns vector_id (not db id).
        """
        items = self.list_contexts(project_id)
        match = next((c for c in items if c.get("vector_id") == vector_id), None)
        if not match:
            raise ContextAPIError(404, f"context with vector_id {vector_id} not found")
        return self.delete_context(project_id, int(match["id"]))

    # ---------- chat ----------

    def search(self, project_id: int, query: str) -> Dict[str, Any]:
        """
        POST /search with {"project_id": id, "query": "..."}
        -> {"context": "<joined sources>", "query": "..."}
        """
        return self._request(
            "POST", "/search", json={"project_id": project_id, "query": query}
        )
