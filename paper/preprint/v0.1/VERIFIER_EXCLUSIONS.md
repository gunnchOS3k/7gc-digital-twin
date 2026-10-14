# Repaired verifier: explicit scientific comparison and provenance validation

The preserved Git verifier is unchanged at repaired source6523d11066d963d922433607462e5f5cd066b9f8. Its saved successful record is evidence/reproduction/current_verification.json; original output paths and provenance are retained. Focused regression record verification/VERIFIER_REGRESSION.txt reruns its four tests without modifying the historical evidence. Portable scripts/reproduce.py adapts source-byte validation to the archive manifest and explicitly retains unknown producer identity for a clean non-Git run. This adaptation is not an alteration of frozen experiment code.

| Excluded from equality | Separate check | Retained in successful record |
|---|---|---|
| Root result_sha256 | Recompute canonical full-result content hash excluding itself and root output-location fields | Historical and fresh hash values |
| Root wrote and statistical_artifacts paths | Nonempty string locations; a historical location need not still exist | Historical and fresh location values when present |
| Typed provenance/producer/commit | Git verifier: 40hex and object resolves. Portable: known recorded producer revision or explicitly unknown in non-Git extraction; no fabricated identity | Full historical and fresh producer objects |
| Typed provenance/producer/generated_at | Valid ISO timestamp with timezone | Both original and fresh timestamps |
| Typed provenance/content_sha256 | Canonical provenance object checksum recomputed | Both full provenance objects |

No blanket recursive hash/key exclusion is applied. All scientific values, seed lists, method labels, bundle content identifier, stable semantic provenance and non-claim flags remain compared exactly. A scientific change with a freshly recomputed valid result checksum must fail. A malformed timestamp or provenance checksum must fail. A benign correctly hashed timestamp/producer/path change must pass while remaining visible in the record. Path checks validate syntax, not historical file existence; archive manifests independently validate retained files.

The engine's digest_match flag compares two stored semantic identifiers, not a rederived semantic bundle digest. The independent byte checksum and frozen snapshot checks establish retained file identity only. They do not prove physical truth, ownership or upstream generation. Whole-payload byte equality, prospective registration and human replication are not claimed.
