#!/usr/bin/env python3
import argparse
import base64
import json
import os
import time
import urllib.parse
import urllib.request


TARGET_KEYS = [
    "sub",
    "repository",
    "repository_id",
    "repository_owner",
    "repository_owner_id",
    "workflow_ref",
    "workflow_sha",
    "job_workflow_ref",
    "job_workflow_sha",
    "aud",
    "ref",
    "ref_type",
    "actor",
    "event_name",
    "run_id",
    "run_attempt",
    "check_run_id",
]


def b64url_decode(value: str) -> bytes:
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value.encode())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audience", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    request_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
    url = request_url + "&audience=" + urllib.parse.quote(args.audience)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + request_token})

    with urllib.request.urlopen(req, timeout=20) as resp:
        token = json.loads(resp.read())["value"]

    header_b64, payload_b64, _sig = token.split(".", 2)
    payload = json.loads(b64url_decode(payload_b64))
    selected = {key: payload.get(key) for key in TARGET_KEYS}
    selected["_captured_at"] = int(time.time())
    selected["_github_repository_env"] = os.getenv("GITHUB_REPOSITORY")
    selected["_github_workflow_ref_env"] = os.getenv("GITHUB_WORKFLOW_REF")
    selected["_github_run_id_env"] = os.getenv("GITHUB_RUN_ID")
    selected["_token_header"] = json.loads(b64url_decode(header_b64))
    selected["_raw_payload"] = payload

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
