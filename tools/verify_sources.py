"""Compare previously read source documents without executing source-project code."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "OpenAgentScaler"

baseline = json.loads((ROOT / "sources/source_sha256.json").read_text())
changed, missing = [], []
for relative, digest in baseline.items():
    path = SOURCE / relative
    if not path.is_file():
        missing.append(relative)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        changed.append(relative)
report = {"checked_files": len(baseline), "changed": changed, "missing": missing,
          "scope": "Read-only comparison of the source documents recorded at the start of paper preparation; does not snapshot active experiment runs."}
(ROOT / "build/source_integrity.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report))
