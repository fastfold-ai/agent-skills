#!/usr/bin/env python3
"""
Create a FastFold job via POST /v1/jobs. Prints job ID to stdout (and optional JSON).

Usage:
    create_job.py --name "My Job" --sequence MALW... [--model boltz-2] [--api-key KEY] [--base-url URL]
    create_job.py --name "Human insulin" --sequence MALWMRLLPLL... --model boltz-2

Requires: requests (pip install requests)
Environment: FASTFOLD_API_KEY (or --api-key)
"""

import argparse
import json
import os
import sys


def create_job(
    base_url: str,
    api_key: str,
    name: str,
    sequence: str,
    model_name: str = "boltz-2",
) -> dict:
    import requests
    url = f"{base_url.rstrip('/')}/v1/jobs"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "name": name,
        "sequences": [{"proteinChain": {"sequence": sequence}}],
        "params": {"modelName": model_name},
    }
    r = requests.post(url, headers=headers, json=body, timeout=30)
    if r.status_code == 401:
        sys.exit("Error: Unauthorized. Check FASTFOLD_API_KEY or --api-key.")
    if r.status_code in (400, 429):
        try:
            err = r.json()
            sys.exit(f"Error: {r.status_code} - {err.get('message', r.text)}")
        except Exception:
            sys.exit(f"Error: {r.status_code} - {r.text}")
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description="Create a FastFold fold job.")
    ap.add_argument("--name", required=True, help="Job name")
    ap.add_argument("--sequence", required=True, help="Protein sequence (one letter codes)")
    ap.add_argument("--model", default="boltz-2", help="Model name (default: boltz-2)")
    ap.add_argument("--api-key", default=os.environ.get("FASTFOLD_API_KEY"), help="API key")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--json", action="store_true", help="Print full response JSON")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY or pass --api-key.")

    data = create_job(
        args.base_url,
        args.api_key,
        args.name,
        args.sequence,
        args.model,
    )
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(data.get("jobId", ""))


if __name__ == "__main__":
    main()
