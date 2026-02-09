#!/usr/bin/env python3
"""
Print the FastFold cloud viewer URL for a job. User can open this in a browser to view
the structure (must be logged in to the same account if the job is private).

Usage:
    get_viewer_link.py JOB_ID [--api-key KEY] [--base-url URL]

Output: single line with URL, e.g. https://cloud.fastfold.ai/mol/new?from=jobs&job_id=550e8400-e29b-41d4-a716-446655440000

Requires: requests (pip install requests) for optional status check.
Environment: FASTFOLD_API_KEY (optional; only needed if you pass --check to verify job exists).
"""

import argparse
import os
import sys

from load_env import load_dotenv

VIEWER_URL_TEMPLATE = "https://cloud.fastfold.ai/mol/new?from=jobs&job_id={job_id}"


def get_results(base_url: str, api_key: str, job_id: str) -> dict:
    import requests
    url = f"{base_url.rstrip('/')}/v1/jobs/{job_id}/results"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 401:
        sys.exit("Error: Unauthorized. Check FASTFOLD_API_KEY or --api-key.")
    if r.status_code == 404:
        sys.exit("Error: Job not found.")
    r.raise_for_status()
    return r.json()


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="Print FastFold viewer URL for a job.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--api-key", default=os.environ.get("FASTFOLD_API_KEY"), help="API key (for --check)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL (for --check)")
    ap.add_argument("--check", action="store_true", help="Verify job exists via API before printing URL")
    args = ap.parse_args()

    if args.check and not args.api_key:
        sys.exit("Error: --check requires FASTFOLD_API_KEY or --api-key.")

    if args.check:
        get_results(args.base_url, args.api_key, args.job_id)

    link = VIEWER_URL_TEMPLATE.format(job_id=args.job_id)
    print(link)


if __name__ == "__main__":
    main()
