#!/usr/bin/env python3
"""
Download CIF file(s) for a completed FastFold job. Single CIF for complex jobs;
one file per sequence for non-complex (e.g. output_0.cif, output_1.cif).

Usage:
    download_cif.py JOB_ID [--out FILE] [--dir DIR] [--api-key KEY] [--base-url URL]

- Complex job: --out single.cif or --dir ./out (writes job_id.cif in dir).
- Non-complex: --dir ./out (writes output_0.cif, output_1.cif, ...).

Requires: requests (pip install requests)
Environment: FASTFOLD_API_KEY (or --api-key)
"""

import argparse
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


def download(url: str, path: str) -> None:
    import requests
    r = requests.get(url, timeout=60, stream=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    ap = argparse.ArgumentParser(description="Download CIF file(s) for a completed FastFold job.")
    ap.add_argument("job_id", help="FastFold job ID (UUID)")
    ap.add_argument("--out", help="Output CIF path (single file; use for complex or single-sequence)")
    ap.add_argument("--dir", default=".", help="Output directory for multiple CIFs (default .)")
    ap.add_argument("--api-key", default=os.environ.get("FASTFOLD_API_KEY"), help="API key")
    ap.add_argument("--base-url", default="https://api.fastfold.ai", help="API base URL")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("Error: Set FASTFOLD_API_KEY or pass --api-key.")

    data = get_results(args.base_url, args.api_key, args.job_id)
    job = data.get("job", {})
    status = job.get("status")
    if status != "COMPLETED":
        sys.exit(f"Error: Job status is {status}, not COMPLETED. Wait for completion first.")

    is_complex = job.get("isComplex", False)
    sequences = data.get("sequences", [])
    pred = data.get("predictionPayload")

    if is_complex and pred and pred.get("cif_url"):
        url = pred["cif_url"]
        if args.out:
            path = args.out
        else:
            path = os.path.join(args.dir, f"{args.job_id}.cif")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        download(url, path)
        print(path)
        return

    # Non-complex: one CIF per sequence
    urls = []
    for s in sequences:
        pp = (s or {}).get("predictionPayload") or {}
        if pp.get("cif_url"):
            urls.append(pp["cif_url"])
    if not urls:
        sys.exit("Error: No CIF URLs in results.")
    if args.out and len(urls) == 1:
        download(urls[0], args.out)
        print(args.out)
        return
    if args.out and len(urls) > 1:
        sys.exit("Error: Job has multiple sequences; use --dir instead of --out.")
    os.makedirs(args.dir, exist_ok=True)
    for i, url in enumerate(urls):
        path = os.path.join(args.dir, f"output_{i}.cif")
        download(url, path)
        print(path)


if __name__ == "__main__":
    main()
