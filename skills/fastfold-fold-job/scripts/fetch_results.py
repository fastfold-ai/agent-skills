#!/usr/bin/env python3
"""
Fetch FastFold job results (GET /v1/jobs/{jobId}/results) and print JSON or a short summary.

Usage:
    fetch_results.py JOB_ID [--api-key KEY] [--base-url URL]
    fetch_results.py JOB_ID --summary   # print status, cif_url(s), and metrics summary

Requires: requests (pip install requests)
Environment: FASTFOLD_API_KEY (or --api-key)
"""

import argparse
import json
import os
import sys


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


def summary(data: dict) -> str:
    job = data.get("job", {})
    status = job.get("status", "UNKNOWN")
    is_complex = job.get("isComplex", False)
    lines = [f"Status: {status}", f"Complex: {is_complex}"]
    if status != "COMPLETED":
        return "\n".join(lines)
    params = data.get("parameters", {})
    sequences = data.get("sequences", [])
    pred = data.get("predictionPayload")
    if is_complex and pred:
        lines.append(f"cif_url: {pred.get('cif_url') or '(none)'}")
        lines.append(f"meanPLLDT: {pred.get('meanPLLDT')}")
        lines.append(f"ptm_score: {pred.get('ptm_score')}")
        lines.append(f"iptm_score: {pred.get('iptm_score')}")
    else:
        for i, seq in enumerate(sequences):
            pp = (seq or {}).get("predictionPayload") or {}
            lines.append(f"[{i}] cif_url: {pp.get('cif_url') or '(none)'}")
            lines.append(f"[{i}] meanPLLDT: {pp.get('meanPLLDT')}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Fetch FastFold job results.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--api-key", default=os.environ.get("FASTFOLD_API_KEY"), help="API key")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    ap.add_argument("--summary", action="store_true", help="Print status and artifact summary")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY or pass --api-key.")

    data = get_results(args.base_url, args.api_key, args.job_id)
    if args.summary:
        print(summary(data))
    else:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
