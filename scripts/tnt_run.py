"""Local run initialization and structural validation; no network or model calls."""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "VN": "vietnam_source_inbox.md",
    "US": "us_source_inbox.md",
    "MACRO": "global_macro_source_inbox.md",
}
SECTIONS = ("Stream A — Data / Reports", "Stream B — News / Events", "Leads / Unverified")
MAIN_LABELS = {"Primary checked", "Secondary checked"}
LEAD_LABELS = {"Discovery only", "Unverified claim"}
REQUIRED_FIELDS = (
    "ID", "Event key", "Owner", "Source", "URL", "Published",
    "Event date / reporting period", "Geography", "Category", "Tickers",
    "Source tier", "Verification", "Evidence checked", "Vietnam relevance",
    "Relevance", "Related / supporting", "Description",
)


class RunError(ValueError):
    pass


def configure(root: Path, folder_url: str, folder_name="TNT Newsletter", replace=False) -> dict:
    parsed = urlparse(folder_url)
    match = re.fullmatch(r"/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]+)/*", parsed.path)
    if parsed.scheme != "https" or parsed.netloc != "drive.google.com" or not match:
        raise RunError("Supply a Google Drive folder URL, not a file URL or local path.")
    config = json.loads((root / "storage_config.example.json").read_text(encoding="utf-8"))
    folder_id = match.group(1)
    config["destination"].update({
        "folder_id": folder_id, "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "folder_name": folder_name,
    })
    target = root / "storage_config.json"
    if target.exists() and not replace:
        old = json.loads(target.read_text(encoding="utf-8"))
        if old["destination"]["folder_id"] == folder_id:
            return {"configured": True, "configuration": "storage_config.json", "access_verified": False}
        raise RunError("A different destination is configured. Use --replace only after confirming the change.")
    write_json(target, config)
    return {"configured": True, "configuration": "storage_config.json", "access_verified": False}


def run_path(root: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run_id):
        raise RunError("Run ID must be 1–80 letters, digits, underscores, or hyphens.")
    base = root.resolve() / "runs"
    path = base / run_id
    if base.is_symlink() or path.is_symlink():
        raise RunError("Run directories must not be symlinks.")
    return path


def timestamp(value: str) -> datetime:
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RunError(f"Invalid timestamp: {value}") from exc
    if result.utcoffset() is None:
        raise RunError("Start and end must include timezone offsets.")
    return result


def write_json(path: Path, data: dict) -> None:
    if path.is_symlink():
        raise RunError(f"Refusing to write through symlink: {path.name}")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def initialize(root: Path, start=None, end=None, run_id=None, collectors=None, max_items=None, tz_name=None) -> dict:
    if not (root / "storage_config.json").exists():
        raise RunError("Set the destination first: python scripts/tnt_run.py configure --folder-url YOUR_DRIVE_FOLDER_URL")
    config = json.loads((root / "storage_config.json").read_text(encoding="utf-8"))
    if not config["destination"].get("folder_id"):
        raise RunError("No destination folder is configured.")
    defaults = config["defaults"]
    if bool(start) != bool(end):
        raise RunError("Supply both start and end, or neither.")
    selected_timezone = tz_name or defaults["timezone"]
    try:
        zone = ZoneInfo(selected_timezone)
    except ZoneInfoNotFoundError as exc:
        raise RunError("Unknown timezone or missing timezone data. Check the name; on Windows, install: python -m pip install tzdata") from exc
    stop = timestamp(end) if end else datetime.now(zone)
    begin = timestamp(start) if start else stop - timedelta(days=defaults["lookback_days"])
    if begin >= stop:
        raise RunError("Start must be earlier than end.")
    selected = collectors if collectors is not None else defaults["collectors"]
    if not selected or len(set(selected)) != len(selected) or any(c not in FILES for c in selected):
        raise RunError("Select unique collector IDs from VN, US, MACRO.")
    limit = max_items if max_items is not None else defaults["max_items_per_collector"]
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise RunError("Max items must be a positive integer.")
    rid = run_id or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ-") + uuid.uuid4().hex[:6]
    folder = run_path(root, rid)
    if folder.exists():
        raise RunError("This run already exists. Resume it or choose a new ID; initialization never overwrites.")
    folder.mkdir(parents=True)
    data = {
        "run_id": rid, "start": begin.isoformat(), "end": stop.isoformat(),
        "timezone": selected_timezone, "collectors": selected,
        "max_items_per_collector": limit,
        "destination": config["destination"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(folder / "run.json", data)
    return data


def fields(lines: list[str]) -> dict[str, str]:
    values = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        match = re.match(r"^([^:]+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            if key in values:
                raise RunError(f"Repeated field: {key}")
            values[key] = value.strip()
    return values


def parse_inbox(path: Path, run: dict, collector: str | None) -> dict:
    if path.is_symlink():
        raise RunError(f"Refusing symlink inbox: {path.name}")
    text = path.read_text(encoding="utf-8")
    if "```" in text:
        raise RunError(f"{path.name}: use filled records, not fenced templates.")
    lines = text.splitlines()
    first_section = next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))
    header = fields(lines[:first_section])
    for key, expected in (("Run ID", run["run_id"]), ("Start", run["start"]),
                          ("End", run["end"]), ("Timezone", run["timezone"])):
        if header.get(key) != expected:
            raise RunError(f"{path.name}: {key} must match run.json exactly.")
    if collector and header.get("Collector ID") != collector:
        raise RunError(f"{path.name}: incorrect Collector ID.")
    if collector and not header.get("Instruction version"):
        raise RunError(f"{path.name}: Instruction version is required.")
    if not header.get("Collected"):
        raise RunError(f"{path.name}: Collected timestamp is required.")
    timestamp(header["Collected"])
    status_key = "Run status" if collector else "Merge status"
    status = header.get(status_key)
    if status not in {"Complete", "Partial", "Blocked"}:
        raise RunError(f"{path.name}: invalid {status_key}.")
    titles = {line[3:].strip() for line in lines if line.startswith("## ")}
    required_sections = set(SECTIONS) | {"Handoffs", "Coverage and gaps"}
    if not required_sections.issubset(titles):
        raise RunError(f"{path.name}: missing section headings must include {sorted(required_sections)}.")
    records = []
    section, title, body = None, None, []

    def finish():
        nonlocal title, body
        if title is not None:
            item = fields(body)
            for key in REQUIRED_FIELDS:
                if not item.get(key):
                    raise RunError(f"{path.name}: {title}: missing {key}.")
            if item["Owner"] not in FILES or (collector and item["Owner"] != collector):
                raise RunError(f"{path.name}: invalid item owner; use Handoffs for other scopes.")
            label = item["Verification"]
            allowed = LEAD_LABELS if section == SECTIONS[2] else MAIN_LABELS
            if label not in allowed:
                raise RunError(f"{path.name}: evidence label is in the wrong section.")
            if item["Source tier"] not in {"T1", "T2", "T3", "T4", "T5"}:
                raise RunError(f"{path.name}: invalid source tier.")
            if not re.fullmatch(r"(?:[1-9]|10)/10", item["Relevance"]):
                raise RunError(f"{path.name}: relevance must be 1/10 through 10/10.")
            if not any(item["Vietnam relevance"].startswith(v) for v in ("Direct", "Potential", "Not identified")):
                raise RunError(f"{path.name}: invalid Vietnam relevance label.")
            if item["Vietnam relevance"].startswith("Potential") and "Inference:" not in item["Vietnam relevance"]:
                raise RunError(f"{path.name}: Potential relevance requires an Inference: basis.")
            url = urlparse(item["URL"])
            if url.scheme not in {"http", "https"} or not url.netloc or url.username or url.password:
                raise RunError(f"{path.name}: expected a public HTTP(S) source URL without credentials.")
            item["title"], item["section"] = title, section
            records.append(item)
        title, body = None, []

    for line in lines[first_section:]:
        if line.startswith("## "):
            finish()
            section = line[3:].strip()
        elif section in SECTIONS and re.match(r"^#{3,4} ", line):
            # Combined inboxes use ### owner groups and #### records.
            if collector and line.startswith("#### "):
                raise RunError(f"{path.name}: collector record headings must use ###.")
            if not collector and line.startswith("### ") and line[4:].strip() not in {"Vietnam", "U.S. Public Markets", "Global Macro"}:
                raise RunError(f"{path.name}: use ### for owner groups and #### for merged records.")
            is_record = line.startswith("### ") if collector else line.startswith("#### ")
            finish()
            if is_record:
                title = line.lstrip("# ").strip()
        elif title is not None:
            body.append(line)
    finish()
    if status == "Blocked" and records:
        raise RunError(f"{path.name}: a blocked inbox cannot contain collected records; use Partial.")
    if collector and len(records) > run["max_items_per_collector"]:
        raise RunError(f"{path.name}: exceeds max_items_per_collector.")
    ids = [item["ID"] for item in records]
    if len(set(ids)) != len(ids):
        raise RunError(f"{path.name}: repeated item IDs.")
    return {"status": status, "items": records}


def validate(root: Path, run_id: str) -> dict:
    folder = run_path(root, run_id)
    manifest_file = folder / "run.json"
    if manifest_file.is_symlink():
        raise RunError("run.json must not be a symlink.")
    run = json.loads(manifest_file.read_text(encoding="utf-8"))
    if run.get("run_id") != run_id:
        raise RunError("Run manifest ID does not match the directory.")
    if timestamp(run["start"]) >= timestamp(run["end"]):
        raise RunError("Invalid time interval in run.json.")
    selected = run["collectors"]
    if not selected or len(set(selected)) != len(selected) or any(c not in FILES for c in selected):
        raise RunError("Invalid collector IDs in run.json.")
    inputs, originals = {}, {}
    for collector in selected:
        path = folder / FILES[collector]
        if not path.exists():
            inputs[collector] = {"status": "Missing", "count": 0}
            continue
        parsed = parse_inbox(path, run, collector)
        inputs[collector] = {"status": parsed["status"], "count": len(parsed["items"])}
        for item in parsed["items"]:
            if item["ID"] in originals:
                raise RunError("Item IDs must be unique across collectors.")
            originals[item["ID"]] = item
    merged = parse_inbox(folder / "source_inbox.md", run, None)
    statuses = [info["status"] for info in inputs.values()]
    expected = "Complete" if all(s == "Complete" for s in statuses) else "Partial"
    if all(s in {"Missing", "Blocked"} for s in statuses):
        expected = "Blocked"
    if merged["status"] != expected:
        raise RunError(f"Merge status must be {expected} based on requested collector statuses.")
    accounted = set()
    verified_urls = []
    rank = {"Unverified claim": 0, "Discovery only": 1, "Secondary checked": 2, "Primary checked": 3}
    for item in merged["items"]:
        aliases = {x.strip() for x in item.get("Contributors / original IDs", "").split(",") if x.strip()}
        if not aliases or item["ID"] not in aliases:
            raise RunError("Each merged item must list its canonical ID and all originals in Contributors / original IDs.")
        if not aliases.issubset(originals):
            raise RunError("Merged item references an unknown original ID.")
        if accounted & aliases:
            raise RunError("An original item appears in more than one merged record.")
        best_evidence = max(rank[originals[x]["Verification"]] for x in aliases)
        if rank[item["Verification"]] > best_evidence:
            raise RunError("Merging must not upgrade verification beyond the input evidence.")
        if not any(originals[x]["URL"] == item["URL"] and rank[originals[x]["Verification"]] >= rank[item["Verification"]] for x in aliases):
            raise RunError("Merged source URL and verification must be supported by an original record.")
        accounted.update(aliases)
        if item["Verification"] in MAIN_LABELS and item["URL"] not in verified_urls:
            verified_urls.append(item["URL"])
    if accounted != set(originals):
        raise RunError("Some collected items disappeared from the merge without an original-ID alias.")
    result = {
        "run_id": run_id, "merge_status": merged["status"], "inputs": inputs,
        "retained_items": len(merged["items"]),
        "duplicates_removed": len(originals) - len(merged["items"]),
        "notebook_urls": len(verified_urls),
        "validation": "structural_only_not_fact_verification",
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    output = folder / "notebooklm_sources.txt"
    if output.is_symlink():
        raise RunError("NotebookLM URL output must not be a symlink.")
    output.write_text("\n".join(verified_urls) + ("\n" if verified_urls else ""), encoding="utf-8")
    write_json(folder / "validation.json", result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("configure", help="save the Drive destination locally; does not grant access")
    setup.add_argument("--folder-url", required=True)
    setup.add_argument("--folder-name", default="TNT Newsletter")
    setup.add_argument("--replace", action="store_true")
    init = sub.add_parser("init", help="create a unique local run and shared parameters")
    init.add_argument("--start")
    init.add_argument("--end")
    init.add_argument("--run-id")
    init.add_argument("--collectors", nargs="+", choices=list(FILES))
    init.add_argument("--max-items", type=int)
    init.add_argument("--timezone")
    check = sub.add_parser("validate", help="check inboxes and create a NotebookLM URL list; no upload")
    check.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "configure":
            result = configure(ROOT, args.folder_url, args.folder_name, args.replace)
        elif args.command == "init":
            result = initialize(ROOT, args.start, args.end, args.run_id, args.collectors, args.max_items, args.timezone)
        else:
            result = validate(ROOT, args.run_id)
    except (RunError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
