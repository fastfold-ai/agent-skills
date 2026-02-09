#!/usr/bin/env python3
"""
Wait for a FastFold job to complete by polling GET /v1/jobs/{jobId}/results.

Usage:
    wait_for_completion.py JOB_ID [--poll-interval SEC] [--timeout SEC] [--api-key KEY] [--base-url URL]
    wait_for_completion.py JOB_ID --json   # print final results JSON to stdout

Requires: requests (pip install requests)
Environment: FASTFOLD_API_KEY (or --api-key)
"""

import argparse
import json
import os
import sys
import time


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
    ap = argparse.ArgumentParser(description="Wait for FastFold job completion.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between polls (default 5)")
    ap.add_argument("--timeout", type=float, default=900.0, help="Max seconds to wait (default 900)")
    ap.add_argument("--api-key", default=os.environ.get("FASTFOLD_API_KEY"), help="API key (default: FASTFOLD_API_KEY)")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--json", action="store_true", help="Print final results JSON to stdout")
    ap.add_argument("--quiet", action="store_true", help="Do not print status lines")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY or pass --api-key.")

    start = time.time()
    last_status = None
    while True:
        data = get_results(args.base_url, args.api_key, args.job_id)
        job = data.get("job", {})
        status = job.get("status", "UNKNOWN")
        if not args.quiet:
            print(f"[FastFold] job {args.job_id} status: {status}", file=sys.stderr)
        if status == "COMPLETED":
            if args.json:
                print(json.dumps(data, indent=2))
            sys.exit(0)
        if status in ("FAILED", "STOPPED"):
            if args.json:
                print(json.dumps(data, indent=2))
            sys.exit(1)
        if (time.time() - start) > args.timeout:
            sys.exit(2)  # timeout
        time.sleep(max(0.1, args.poll_interval))


if __name__ == "__main__":
    main()
