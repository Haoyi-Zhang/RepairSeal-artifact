"""Compare a delivered project against the original user-supplied ZIP.

Only members present in the original ZIP belong to the preservation check.
New experiments, checks and reports are therefore permitted without being
mistaken for modifications to historical evidence. The original archive is an
external audit input and is never copied into the deliverable.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


PROJECT = Path(__file__).resolve().parents[2]
ARCHIVE_ROOT = "RepairSeal_TOSEM"
HISTORICAL_GROUPS = (
    "artifact/data", "artifact/proof-data", "artifact/experiments",
    "artifact/results", "artifact/evaluation-record",
)


def stream_hash(stream):
    sha = hashlib.sha256()
    for block in iter(lambda: stream.read(1048576), b""):
        sha.update(block)
    return sha.hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return stream_hash(stream)


def canonical_line(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()


def existing_leaf_changes(original, current, prefix=""):
    """Added expectation fields are allowed; existing leaves must be identical."""
    changes = []
    if isinstance(original, dict):
        if not isinstance(current, dict):
            return [{"field": prefix, "reason": "container-type-changed"}]
        for key, value in original.items():
            path = prefix + "/" + key
            if key not in current:
                changes.append({"field": path, "reason": "removed", "original": value})
            else:
                changes.extend(existing_leaf_changes(value, current[key], path))
    elif type(original) is not type(current) or original != current:
        changes.append({"field": prefix, "reason": "changed", "original": original, "current": current})
    return changes


def run(original_zip: Path, project: Path, diff_output: Path | None = None):
    original_zip = original_zip.resolve(); project = project.resolve()
    original_inventory = hashlib.sha256(); current_inventory = hashlib.sha256()
    group_counts = defaultdict(Counter)
    paper_rows = []; protected_failures = []; all_differences = []; diffs = []
    protected_rows = []
    old_expectations = None
    total = 0; original_bytes = 0; artifact_files = 0; artifact_equal = 0
    deleted_original_files = []
    with zipfile.ZipFile(original_zip) as archive:
        members = sorted((m for m in archive.infolist() if not m.is_dir()), key=lambda m: m.filename)
        seen = set()
        for member in members:
            parts = PurePosixPath(member.filename).parts
            if not parts or parts[0] != ARCHIVE_ROOT or ".." in parts or member.filename.startswith("/"):
                raise ValueError("unexpected or unsafe archive path")
            relative = PurePosixPath(*parts[1:]).as_posix()
            if relative in seen:
                raise ValueError("duplicate original archive member")
            seen.add(relative)
            total += 1; original_bytes += member.file_size
            destination = project / relative
            with archive.open(member) as stream:
                before_sha = stream_hash(stream)
            exists = destination.is_file() and not destination.is_symlink()
            after_sha = file_hash(destination) if exists else None
            equal = exists and before_sha == after_sha
            status = "MATCH" if equal else "MODIFIED" if exists else "MISSING_OR_NONREGULAR"
            row = {"path": relative, "bytes": member.file_size,
                   "original_sha256": before_sha, "current_sha256": after_sha, "status": status}
            original_inventory.update(canonical_line({"path": relative, "bytes": member.file_size, "sha256": before_sha}))
            current_inventory.update(canonical_line({"path": relative, "bytes": destination.stat().st_size if exists else None, "sha256": after_sha}))
            if relative.startswith("artifact/"):
                artifact_files += 1; artifact_equal += equal
            if not exists:
                deleted_original_files.append(relative)
            if relative.startswith("paper/"):
                paper_rows.append(row)
                protected_rows.append([relative, before_sha, member.file_size])
                if not equal:
                    protected_failures.append(row)
            for group in HISTORICAL_GROUPS:
                if relative.startswith(group + "/"):
                    protected_rows.append([relative, before_sha, member.file_size])
                    group_counts[group]["original_files"] += 1
                    group_counts[group]["original_bytes"] += member.file_size
                    group_counts[group]["matching_files"] += equal
                    group_counts[group]["modified_files"] += status == "MODIFIED"
                    group_counts[group]["missing_or_nonregular_files"] += status == "MISSING_OR_NONREGULAR"
                    if not equal:
                        protected_failures.append(row)
                    break
            if relative == "artifact/expected-results.json":
                old_expectations = json.loads(archive.read(member))
            if not equal:
                all_differences.append(row)
                if exists and member.file_size <= 2**20 and destination.stat().st_size <= 2**20:
                    try:
                        before = archive.read(member).decode("utf-8").splitlines(keepends=True)
                        after = destination.read_text(encoding="utf-8").splitlines(keepends=True)
                    except UnicodeError:
                        continue
                    patch = list(difflib.unified_diff(before, after, fromfile="original/" + relative,
                                                     tofile="updated/" + relative, n=3))
                    row["removed_text_lines"] = sum(line.startswith("-") and not line.startswith("---") for line in patch)
                    row["added_text_lines"] = sum(line.startswith("+") and not line.startswith("+++") for line in patch)
                    diffs.extend(patch)
    current_expectations = json.loads((project / "artifact/expected-results.json").read_text())
    expectation_changes = existing_leaf_changes(old_expectations, current_expectations)
    historical_count = sum(v["original_files"] for v in group_counts.values())
    historical_equal = sum(v["matching_files"] for v in group_counts.values())
    primary_groups = ["artifact/data", "artifact/proof-data", "artifact/experiments"]
    primary_count = sum(group_counts[g]["original_files"] for g in primary_groups)
    primary_equal = sum(group_counts[g]["matching_files"] for g in primary_groups)
    if diff_output is not None:
        diff_output.parent.mkdir(parents=True, exist_ok=True)
        diff_output.write_text("".join(diffs), encoding="utf-8")
    failures = []
    if protected_failures:
        failures.append("original paper or historical scientific evidence modified/deleted")
    if deleted_original_files:
        failures.append("one or more original files missing or nonregular")
    if expectation_changes:
        failures.append("one or more pre-existing expected-result fields changed/removed")
    archive_identity = {"filename": original_zip.name, "bytes": original_zip.stat().st_size,
                        "sha256": file_hash(original_zip), "files": total, "uncompressed_bytes": original_bytes}
    protected_manifest = {
        "schema": "repairseal-original-evidence-hash-manifest-v1",
        "original_archive": archive_identity,
        "entry_fields": ["path_relative_to_project", "original_sha256", "original_bytes"],
        "files": protected_rows,
        "original_expected_results": old_expectations,
    }
    manifest_path = None
    if diff_output is not None:
        manifest_path = diff_output.with_name("original-evidence-manifest.json")
        manifest_path.write_text(json.dumps(protected_manifest, ensure_ascii=True, separators=(",", ":")) + "\n")
    return {
        "schema": "repairseal-original-evidence-integrity-v1",
        "status": "PASS" if not failures else "FAIL",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "original_archive": archive_identity,
        "original_archive_member_inventory_sha256": original_inventory.hexdigest(),
        "current_original_member_inventory_sha256": current_inventory.hexdigest(),
        "paper": {"original_files": len(paper_rows), "matching_files": sum(r["status"] == "MATCH" for r in paper_rows),
                  "modified_files": sum(r["status"] == "MODIFIED" for r in paper_rows),
                  "missing_or_nonregular_files": sum(r["status"] == "MISSING_OR_NONREGULAR" for r in paper_rows),
                  "files": paper_rows},
        "historical_data_proof_data_experiments": {"original_files": primary_count, "matching_files": primary_equal},
        "historical_evidence_including_results_and_evaluation_record": {
            "original_files": historical_count, "matching_files": historical_equal,
            "groups": {name: dict(counts) for name, counts in sorted(group_counts.items())}},
        "all_original_artifact_files": {"original_files": artifact_files, "matching_files": artifact_equal,
                                        "changed_files": artifact_files - artifact_equal},
        "preexisting_expected_result_fields": {"status": "UNCHANGED" if not expectation_changes else "CHANGED",
                                               "changes": expectation_changes,
                                               "added_fields_allowed": True},
        "original_file_differences": all_differences,
        "deleted_original_files": deleted_original_files,
        "protected_failures": protected_failures,
        "errors": failures,
        "code_diff_file": None if diff_output is None else diff_output.name,
        "code_diff_sha256": None if diff_output is None else file_hash(diff_output),
        "audit_script_sha256": file_hash(Path(__file__)),
        "protected_manifest": None if manifest_path is None else {
            "filename": manifest_path.name, "sha256": file_hash(manifest_path),
            "bytes": manifest_path.stat().st_size, "entries": len(protected_rows)},
        "scope": [
            "Every original archive member is hashed; all 71 paper files have individual before/after hashes.",
            "Historical scientific evidence under data, proof-data, experiments, results, and evaluation-record must remain byte identical.",
            "New files are excluded from the historical-preservation comparison because they did not exist in the original archive.",
            "Changes to original code/documentation are enumerated for review, not silently accepted as evidence changes.",
            "The audit checks that every existing expected-results.json leaf is unchanged; added expectation fields are allowed.",
            "Hash comparison alone cannot prove that arbitrary changed executable checks were not weakened. Their complete text diff is supplied for independent review and the existing test gates must still run.",
            "The original ZIP is an external verification input and is not copied or redistributed by this script.",
        ],
    }


def verify(root: Path | None = None, record: Path | None = None):
    """Recheck frozen original hashes offline; root denotes artifact/.

    This intentionally does not require or reopen the original ZIP. The first
    run established the protected hashes from that ZIP, and the receipt binds
    the manifest bytes. The global expected-results integration can additionally
    anchor the manifest hash. New project files are outside this preservation
    comparison; all original scientific evidence and paper files are checked.
    """
    root = PROJECT / "artifact" if root is None else Path(root)
    project = root.parent
    record = root / "results/review-update/original-evidence-integrity.json" if record is None else Path(record)
    errors = []; groups = defaultdict(Counter); files_checked = 0; paper_revised = []
    try:
        receipt = json.loads(record.read_text())
        binding = receipt["protected_manifest"]
        name = binding["filename"]
        if PurePosixPath(name).name != name:
            raise ValueError("manifest filename is not local to receipt")
        manifest_path = record.parent / name
        if file_hash(manifest_path) != binding["sha256"]:
            raise ValueError("original protected manifest hash mismatch")
        manifest = json.loads(manifest_path.read_text())
        if manifest["original_archive"] != receipt["original_archive"]:
            raise ValueError("original archive identity binding mismatch")
        if len(manifest["files"]) != binding["entries"]:
            raise ValueError("protected manifest entry count")
        seen = set()
        for relative, sha, size in manifest["files"]:
            parts = PurePosixPath(relative).parts
            if relative.startswith("/") or ".." in parts or relative in seen:
                raise ValueError("unsafe or duplicate protected path")
            seen.add(relative)
            group = "paper" if relative.startswith("paper/") else next(
                (g for g in HISTORICAL_GROUPS if relative.startswith(g + "/")), None)
            if group is None:
                raise ValueError("manifest contains an unprotected location")
            path = project / relative
            exists = path.is_file() and not path.is_symlink()
            matches = exists and path.stat().st_size == size and file_hash(path) == sha
            groups[group]["files"] += 1; groups[group]["matching_files"] += matches
            files_checked += 1
            if not matches:
                if group == "paper":
                    # The manuscript is registered as a historical record of the
                    # uploaded version; later author revisions are reported, not failed.
                    paper_revised.append(relative)
                else:
                    errors.append("protected file changed or missing: " + relative)
        expected_original = manifest["original_expected_results"]
        expected_now = json.loads((root / "expected-results.json").read_text())
        leaf_changes = existing_leaf_changes(expected_original, expected_now)
        errors.extend("existing expected-result field changed/removed: " + r["field"] for r in leaf_changes)
        if groups["paper"]["files"] != receipt["paper"]["original_files"]:
            errors.append("paper inventory cardinality mismatch")
        historic = sum(c["files"] for g, c in groups.items() if g != "paper")
        if historic != receipt["historical_evidence_including_results_and_evaluation_record"]["original_files"]:
            errors.append("historical evidence inventory cardinality mismatch")
        if receipt["status"] != "PASS" or receipt["errors"] or receipt["protected_failures"]:
            errors.append("original collection receipt did not pass")
    except (ValueError, TypeError, KeyError, OSError, StopIteration) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    return {"status": "PASS" if not errors else "FAIL", "errors": errors,
            "files_checked": files_checked, "groups": {g: dict(c) for g, c in sorted(groups.items())},
            "paper_files_revised_since_upload": sorted(paper_revised),
            "scope": ("Offline preservation check: historical scientific evidence (data, proof-data, experiments, "
                      "results, evaluation-record) must match byte for byte, and old expected-result leaves must be "
                      "unchanged. The originally uploaded manuscript is registered as a historical record; files the "
                      "authors revised later are listed, not failed. External ZIP not required.")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-zip", type=Path)
    parser.add_argument("--project", type=Path, default=PROJECT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--diff-output", type=Path)
    parser.add_argument("--verify-record", action="store_true")
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    if args.verify_record:
        result = verify(args.project / "artifact", args.record)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if args.original_zip is None or args.output is None:
        parser.error("initial comparison requires --original-zip and --output")
    diff_output = args.diff_output or args.output.with_name("original-code-differences.diff")
    result = run(args.original_zip, args.project, diff_output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"status": result["status"], "original_files": result["original_archive"]["files"],
                      "paper_matching": result["paper"]["matching_files"],
                      "historical_evidence_matching": result["historical_evidence_including_results_and_evaluation_record"]["matching_files"],
                      "original_artifact_differences": result["all_original_artifact_files"]["changed_files"],
                      "errors": result["errors"]}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
