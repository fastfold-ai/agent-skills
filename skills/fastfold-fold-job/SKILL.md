---
name: fastfold-fold-job
description: Submits and manages FastFold protein folding jobs via the Jobs API. Covers authentication, creating jobs, polling for completion, and fetching CIF/PDB URLs, metrics, and viewer links. Use when folding protein sequences with FastFold, calling the FastFold API, or scripting fold-and-wait workflows.
---

# FastFold Fold Job

## Overview

This skill guides correct use of the [FastFold Jobs API](https://docs.fastfold.ai/docs/api): create fold jobs, wait for completion with polling, then fetch results (CIF/PDB URLs, metrics, viewer link). Use the bundled OpenAPI schema and scripts in this skill for consistent behavior (skill is self-contained).

## Authentication

**Get an API key:** Create a key in the [FastFold dashboard](https://cloud.fastfold.ai/api-keys). Keep it secret; anyone with the key can make requests on your behalf.

**Use the key:** Send it in the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

- **Environment (recommended):** `export FASTFOLD_API_KEY="sk-..."`
- **Scripts in this skill** read `FASTFOLD_API_KEY` by default; override with `--api-key` when needed.

**Required before any authenticated action:** If `FASTFOLD_API_KEY` is not set and the user has not provided an API key (e.g. via `--api-key`), **do not continue**. Ask the user to create a key at [FastFold API Keys](https://cloud.fastfold.ai/api-keys) and set it (e.g. `export FASTFOLD_API_KEY="sk-..."`) or to provide it. Wait for the user to confirm the key is set before creating jobs, running wait/fetch/download scripts, or calling authenticated endpoints.

Public jobs (`isPublic: true`) can be read without auth via Get Job Results; private jobs require the owner’s API key. See [references/auth_and_api.md](references/auth_and_api.md) for details and quota limits.

## When to Use This Skill

- User wants to fold a protein sequence with FastFold (API or scripts).
- User mentions FastFold API, fold job, CIF/PDB results, or viewer link.
- User needs to script: create job → wait for completion → download results / metrics / viewer URL.

## Workflow: Create → Wait → Results

0. **Ensure API key is set** – If `FASTFOLD_API_KEY` is not set (and no `--api-key` given), ask the user to create and set the key; do not proceed until they confirm.
1. **Create job** – POST `/v1/jobs` with `name`, `sequences`, `params` (required). Optional: `isPublic`, `constraints`, `from` (library ID). See schema in this skill: [references/jobs.yaml](references/jobs.yaml).
2. **Wait for completion** – Poll GET `/v1/jobs/{jobId}/results` until `job.status` is `COMPLETED`, `FAILED`, or `STOPPED`. Use a 5–10 s interval and a timeout (e.g. 900 s).
3. **Fetch results** – For `COMPLETED` jobs: read `cif_url`, `pdb_url`, metrics (e.g. `meanPLLDT`, `ptm_score`, `iptm_score`), and build viewer link. Complex vs non-complex jobs differ (see below).

**Scripts:** Prefer the bundled scripts so behavior matches the SDK:

- **Wait for completion:** `python scripts/wait_for_completion.py <job_id> [--poll-interval 5] [--timeout 900]`
- **Fetch results (JSON):** `python scripts/fetch_results.py <job_id>`
- **Download CIF:** `python scripts/download_cif.py <job_id> [--out output.cif]`
- **Viewer link:** `python scripts/get_viewer_link.py <job_id>`

All scripts accept `--api-key` and `--base-url`; they use `FASTFOLD_API_KEY` and `https://api.fastfold.ai` by default.

## Complex vs Non-Complex Jobs

- **Complex** (e.g. boltz-2 single complex): Results have a single top-level `predictionPayload`; use `results.cif_url()`, `results.metrics()` once.
- **Non-complex** (e.g. multi-chain monomer/simplefold): Each sequence has its own `predictionPayload`; use `results[0].cif_url()`, `results[1].cif_url()`, etc., and `results[i].metrics()` per chain.

The scripts handle both: `fetch_results.py` and `download_cif.py` output or download the right CIF(s); `get_viewer_link.py` prints the job viewer URL (one URL per job on FastFold cloud).

## Job Status Values

- `PENDING` – Queued, not yet initialized  
- `INITIALIZED` – Ready to run  
- `RUNNING` – Processing  
- `COMPLETED` – Success; artifacts and metrics available  
- `FAILED` – Error  
- `STOPPED` – Stopped before completion  

Only use `cif_url`, `pdb_url`, metrics, and viewer link when status is `COMPLETED`.

## Viewer Link (3D structure)

For a completed job, the 3D structure viewer URL is:

`https://cloud.fastfold.ai/mol/new?from=jobs&job_id=<job_id>`

Use `scripts/get_viewer_link.py <job_id>` to print this URL. If the job is private, the user must be logged in to the same FastFold account to view it.

## Resources

- **Auth and API overview:** [references/auth_and_api.md](references/auth_and_api.md)  
- **Schema summary:** [references/schema_summary.md](references/schema_summary.md)  
- **Full request/response schema (in this skill):** [references/jobs.yaml](references/jobs.yaml)
