"""Onshape HTTP client with HMAC-SHA256 request signing."""

import base64
import hashlib
import hmac
import os
import secrets
import string
import tempfile
import time
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx

BASE_URL = os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com")


def _keychain(account: str) -> str:
    import subprocess
    result = subprocess.run(
        ["security", "find-generic-password", "-s", "onshape", "-a", account, "-w"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _credentials() -> tuple[str, str]:
    access_key = os.environ.get("ONSHAPE_ACCESS_KEY") or _keychain("access-key")
    secret_key = os.environ.get("ONSHAPE_SECRET_KEY") or _keychain("secret-key")
    if not access_key or not secret_key:
        raise RuntimeError(
            "Onshape credentials not found. Set ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY "
            "environment variables, or store them in macOS Keychain under service 'onshape' "
            "with accounts 'access-key' and 'secret-key'."
        )
    return access_key, secret_key


def _make_headers(
    method: str,
    path: str,
    query: str = "",
    content_type: str = "application/json",
) -> dict:
    access_key, secret_key = _credentials()
    nonce = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(25))
    date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    signing_string = (
        "\n".join([
            method.lower(),
            nonce.lower(),
            date.lower(),
            content_type.lower(),
            path.lower(),
            query.lower(),
        ])
        + "\n"
    )

    digest = hmac.new(
        secret_key.encode("utf-8"),
        signing_string.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature = base64.b64encode(digest).decode("utf-8")

    return {
        "Date": date,
        "On-Nonce": nonce,
        "Authorization": f"On {access_key}:HmacSHA256:{signature}",
        "Content-Type": content_type,
        "Accept": "application/json;charset=UTF-8; qs=0.09",
    }


def _request(
    method: str,
    path: str,
    params: dict | None = None,
    json: dict | None = None,
    content_type: str = "application/json",
    binary: bool = False,
) -> dict | list | bytes:
    query = urlencode(params) if params else ""
    headers = _make_headers(method.upper(), path, query, content_type)
    url = f"{BASE_URL}{path}"

    with httpx.Client(timeout=30) as client:
        resp = client.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json,
        )
        resp.raise_for_status()
        if binary:
            return resp.content
        if resp.content:
            return resp.json()
        return {}


def get(path: str, **params) -> dict | list:
    return _request("GET", path, params=params or None)


def post(path: str, data: dict | None = None, **params) -> dict:
    return _request("POST", path, params=params or None, json=data or {})


def put(path: str, data: dict | None = None, **params) -> dict:
    return _request("PUT", path, params=params or None, json=data or {})


def delete(path: str, **params) -> dict:
    return _request("DELETE", path, params=params or None)


def get_binary(path: str, **params) -> bytes:
    return _request("GET", path, params=params or None, binary=True)


def poll_translation(translation_id: str, timeout: int = 120) -> dict:
    """Poll a translation until DONE or FAILED, with exponential back-off."""
    deadline = time.time() + timeout
    delay = 2.0
    while time.time() < deadline:
        result = get(f"/api/v10/translations/{translation_id}")
        state = result.get("requestState")
        if state == "DONE":
            return result
        if state == "FAILED":
            raise RuntimeError(
                f"Translation failed: {result.get('failureReason', 'unknown reason')}"
            )
        time.sleep(min(delay, deadline - time.time()))
        delay = min(delay * 1.5, 10.0)
    raise TimeoutError(f"Translation {translation_id} did not complete within {timeout}s")


def download_external_data(did: str, external_data_id: str, suffix: str = ".bin") -> str:
    """Download a translation result blob and save it to a temp file. Returns the file path."""
    data = get_binary(f"/api/v10/documents/d/{did}/externaldata/{external_data_id}")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(data)
        return f.name
