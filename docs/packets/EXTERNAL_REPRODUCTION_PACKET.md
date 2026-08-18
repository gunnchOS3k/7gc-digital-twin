# External / independent reproduction packet — 7gc-digital-twin

**Status:** `INDEPENDENT_REPRODUCTION_PENDING` for a second-person sign-off. The **digital command path** is ready.

Cursor cannot sign this on another person’s behalf.

## Scope

RQ1 profiles/benchmarks on a frozen commit. Synthetic fixtures only.

## Command

```bash
git clone https://github.com/gunnchOS3k/7gc-digital-twin.git
cd 7gc-digital-twin
git checkout <frozen-sha>
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
make test
make reproduce
```

## Expected evidence form

Store as `artifacts/independent_reproduction/<person-or-lab-id>.md` (no extra PII).

```text
system:
commit:
command: make reproduce
start:
end:
result:
output_hashes:
deviations:
PASS_FAIL:
notes: synthetic_fixture only; not RF; not community deployment; not Oulu affiliation
```

## What success means

`make reproduce` writes `results/reproduce/REPRODUCE_RECORD.json` with `result: PASS` and hashes for `results/experiments/rq1_gary_flagship_profiles.json`.

## What success does not mean

Independent digital PASS is not `FIELD_VALIDATED` and is not a community-network result.
