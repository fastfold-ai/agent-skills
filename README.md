# Fastfold Agent Skills

A collection of skills for AI coding agents. Skills are packaged instructions and scripts that extend agent capabilities.

Skills follow the [Agent Skills](https://agentskills.io/) format.

## Install

```bash
npx skills add fastfold-ai/agent-skills
```

## Available Skills

Skills in this repo live in the **`skills/`** folder.

### fastfold-fold-job

Submits and manages FastFold protein folding jobs via the Jobs API. Covers authentication, creating jobs, polling for completion, and fetching CIF/PDB URLs, metrics, and 3D viewer links.

**Use when:**
- Folding a protein sequence with FastFold (API or scripts)
- Mentioning FastFold API, fold job, CIF/PDB results, or viewer link
- Scripting: create job → wait for completion → download results / metrics / viewer URL

**Features:**
- Create Job (POST `/v1/jobs`) with sequences and params; optional constraints, library `from` ID
- Wait for completion with configurable polling and timeout
- Fetch results (JSON or summary), download CIF(s), get 3D viewer link
- Self-contained OpenAPI schema in `references/jobs.yaml`

**Scripts:**
- `wait_for_completion.py` – poll until COMPLETED/FAILED/STOPPED
- `fetch_results.py` – get job results (full JSON or `--summary`)
- `download_cif.py` – download CIF file(s) for completed jobs
- `get_viewer_link.py` – print Mol* viewer URL: `https://cloud.fastfold.ai/mol/new?from=jobs&job_id=<id>`

**Requires:** `FASTFOLD_API_KEY` (or `--api-key`). Agent will ask the user to set the key before continuing if missing.

## Usage

Once installed, the agent uses a skill when the task matches its description and “Use when” triggers.

**Example:**
- *“Fold this sequence with FastFold”* → fastfold-fold-job

For **fastfold-fold-job**, set your API key before creating jobs or running scripts:
```bash
export FASTFOLD_API_KEY="sk-..."
```

## Skill Structure

Each skill in `skills/` contains:

| Item | Purpose |
|------|---------|
| `SKILL.md` | Required. YAML frontmatter (name, description) + markdown instructions for the agent. |
| `scripts/` | Optional. Executable helpers (e.g. Python, shell) for automation. |
| `references/` | Optional. Supporting docs (API refs, schemas, guides). |
| `assets/` | Optional. Templates, images, or other files used in outputs. |

Example layout:
```
skills/
└── skill-name/
    ├── SKILL.md
    ├── references/
    │   ├── api_ref.md
    │   └── schema.yaml
    └── scripts/
        ├── run_thing.py
        └── validate.sh
```

## License

MIT
