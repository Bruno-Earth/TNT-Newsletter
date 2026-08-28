"""Synthetic local fixtures only: no live collection and no Google writes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tnt_run", REPO / "scripts" / "tnt_run.py")
tnt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tnt)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "storage_config.example.json").write_bytes((REPO / "storage_config.example.json").read_bytes())
        tnt.configure(self.root, "https://drive.google.com/drive/folders/test-folder-id")
        self.run = tnt.initialize(self.root, "2026-08-21T00:00:00+07:00", "2026-08-28T00:00:00+07:00", "test-run")
        self.folder = self.root / "runs" / "test-run"

    def item(self, owner="VN", label="Primary checked", name=None):
        identifier = name or owner + "-1"
        return {
            "ID": identifier, "Event key": identifier + "/release/2026-08",
            "Owner": owner, "Source": "Synthetic fixture; English",
            "URL": "https://example.test/" + identifier, "Published": "2026-08-27",
            "Event date / reporting period": "2026-08", "Geography": "Test only",
            "Category": "Macro", "Tickers": "N/A", "Source tier": "T1",
            "Verification": label, "Evidence checked": "Synthetic test data, no real source",
            "Vietnam relevance": "Not identified", "Relevance": "8/10",
            "Related / supporting": "None", "Description": "Synthetic fixture, not a collected fact.",
        }

    def write_inbox(self, items, collector=None, status="Complete"):
        header = ["# Test inbox"]
        if collector:
            header.append("Collector ID: " + collector)
            header.append("Instruction version: test-version")
        for key, value in (("Run ID", self.run["run_id"]), ("Start", self.run["start"]),
                           ("End", self.run["end"]), ("Timezone", self.run["timezone"]),
                           ("Collected", "2026-08-28T01:00:00+07:00"),
                           ("Run status" if collector else "Merge status", status)):
            header.append(f"{key}: {value}")
        for section in tnt.SECTIONS:
            header.extend(["", "## " + section])
            selected = [i for i in items if (section == tnt.SECTIONS[2] and i["Verification"] in tnt.LEAD_LABELS)
                        or (section == tnt.SECTIONS[0] and i["Verification"] in tnt.MAIN_LABELS)]
            if not selected:
                header.append("None found in this synthetic test.")
            for item in selected:
                if not collector:
                    group = {"VN": "Vietnam", "US": "U.S. Public Markets", "MACRO": "Global Macro"}[item["Owner"]]
                    header.append("### " + group)
                header.append(("### " if collector else "#### ") + "Synthetic entry")
                header.extend(f"{key}: {value}" for key, value in item.items())
        header.extend(["", "## Handoffs", "None", "", "## Coverage and gaps", "Synthetic fixtures; no sources checked."])
        path = self.folder / (tnt.FILES[collector] if collector else "source_inbox.md")
        path.write_text("\n".join(header) + "\n", encoding="utf-8")
        return path

    def complete_run(self):
        items = [self.item(owner) for owner in tnt.FILES]
        for item in items:
            self.write_inbox([ item ], item["Owner"])
        merged = copy.deepcopy(items)
        for item in merged:
            item["Contributors / original IDs"] = item["ID"]
        self.write_inbox(merged)
        return items, merged


    def test_init_preserves_destination_and_scope(self):
        self.assertEqual(self.run["destination"]["folder_id"], "test-folder-id")
        self.assertEqual(self.run["collectors"], ["VN", "US", "MACRO"])
        self.assertEqual(self.run["drive_week"], {
            "start": "2026-08-24",
            "end": "2026-08-30",
            "name": "Week 2026-08-24 to 2026-08-30",
        })
        self.assertTrue((self.folder / "run.json").is_file())

    def test_runs_in_same_week_reuse_the_same_drive_week_name(self):
        monday = tnt.initialize(
            self.root, "2026-08-23T12:00:00+07:00", "2026-08-24T09:00:00+07:00", "monday-run"
        )
        tuesday = tnt.initialize(
            self.root, "2026-08-24T09:00:00+07:00", "2026-08-25T09:00:00+07:00", "tuesday-run"
        )
        next_monday = tnt.initialize(
            self.root, "2026-08-30T09:00:00+07:00", "2026-08-31T09:00:00+07:00", "next-monday-run"
        )
        self.assertEqual(monday["drive_week"], tuesday["drive_week"])
        self.assertEqual(monday["drive_week"]["name"], "Week 2026-08-24 to 2026-08-30")
        self.assertEqual(next_monday["drive_week"]["name"], "Week 2026-08-31 to 2026-09-06")

    def test_configure_is_local_and_does_not_claim_access(self):
        result = tnt.configure(self.root, "https://drive.google.com/drive/folders/test-folder-id?usp=sharing")
        self.assertFalse(result["access_verified"])
        config = json.loads((self.root / "storage_config.json").read_text())
        self.assertEqual(config["destination"]["folder_id"], "test-folder-id")
        self.assertNotIn("require_sharing_check", config["destination"])
        self.assertNotIn("sharing_decision", config["destination"])

    def test_configure_requires_explicit_destination_replacement(self):
        other = "https://drive.google.com/drive/folders/other-test-folder"
        with self.assertRaises(tnt.RunError):
            tnt.configure(self.root, other)
        tnt.configure(self.root, other, replace=True)
        config = json.loads((self.root / "storage_config.json").read_text())
        self.assertEqual(config["destination"]["folder_id"], "other-test-folder")

    def test_configure_rejects_non_folder_urls(self):
        for url in ("https://drive.google.com/file/d/test/view", "http://drive.google.com/drive/folders/test", "https://other.test/drive/folders/test"):
            with self.subTest(url=url), self.assertRaises(tnt.RunError):
                tnt.configure(self.root, url)

    def test_init_does_not_overwrite(self):
        before = (self.folder / "run.json").read_bytes()
        with self.assertRaises(tnt.RunError):
            tnt.initialize(self.root, run_id="test-run")
        self.assertEqual((self.folder / "run.json").read_bytes(), before)

    def test_invalid_period_and_path_rejected(self):
        for kwargs in [{"start": "2026-08-21T00:00:00+07:00"},
                       {"start": "2026-08-28T00:00:00", "end": "2026-08-29T00:00:00"},
                       {"start": "2026-08-29T00:00:00Z", "end": "2026-08-28T00:00:00Z"},
                       {"run_id": "../outside"}, {"max_items": 0}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(tnt.RunError):
                tnt.initialize(self.root, **kwargs)

    def test_complete_three_collector_run(self):
        self.complete_run()
        result = tnt.validate(self.root, "test-run")
        self.assertEqual((result["merge_status"], result["retained_items"]), ("Complete", 3))
        self.assertEqual(len((self.folder / "notebooklm_sources.txt").read_text().splitlines()), 3)

    def test_duplicate_aliases_preserve_all_inputs(self):
        items, merged = self.complete_run()
        merged[0]["Contributors / original IDs"] += ", " + items[1]["ID"]
        self.write_inbox([merged[0], merged[2]])
        result = tnt.validate(self.root, "test-run")
        self.assertEqual(result["duplicates_removed"], 1)

    def test_dropped_item_rejected(self):
        _, merged = self.complete_run()
        self.write_inbox(merged[:-1])
        with self.assertRaisesRegex(tnt.RunError, "disappeared"):
            tnt.validate(self.root, "test-run")

    def test_unknown_alias_rejected(self):
        _, merged = self.complete_run()
        merged[0]["Contributors / original IDs"] += ", unknown"
        self.write_inbox(merged)
        with self.assertRaisesRegex(tnt.RunError, "unknown original"):
            tnt.validate(self.root, "test-run")

    def test_reused_alias_rejected(self):
        _, merged = self.complete_run()
        merged[1]["Contributors / original IDs"] += ", " + merged[0]["ID"]
        self.write_inbox(merged)
        with self.assertRaisesRegex(tnt.RunError, "more than one"):
            tnt.validate(self.root, "test-run")

    def test_missing_input_requires_partial(self):
        _, merged = self.complete_run()
        (self.folder / tnt.FILES["MACRO"]).unlink()
        self.write_inbox(merged[:-1])
        with self.assertRaisesRegex(tnt.RunError, "must be Partial"):
            tnt.validate(self.root, "test-run")
        self.write_inbox(merged[:-1], status="Partial")
        self.assertEqual(tnt.validate(self.root, "test-run")["inputs"]["MACRO"]["status"], "Missing")

    def test_all_missing_is_blocked_not_empty_success(self):
        self.write_inbox([], status="Blocked")
        result = tnt.validate(self.root, "test-run")
        self.assertEqual(result["merge_status"], "Blocked")
        self.assertEqual((self.folder / "notebooklm_sources.txt").read_text(), "")

    def test_period_mismatch_rejected(self):
        self.complete_run()
        path = self.folder / tnt.FILES["US"]
        path.write_text(path.read_text(encoding="utf-8").replace(self.run["start"], "2026-08-20T00:00:00+07:00"), encoding="utf-8")
        with self.assertRaisesRegex(tnt.RunError, "Start must match"):
            tnt.validate(self.root, "test-run")

    def test_leads_excluded_from_notebook_urls(self):
        _, merged = self.complete_run()
        lead = self.item("VN", "Discovery only", "VN-lead")
        self.write_inbox([self.item(), lead], "VN")
        lead["Contributors / original IDs"] = lead["ID"]
        self.write_inbox(merged + [lead])
        result = tnt.validate(self.root, "test-run")
        self.assertEqual((result["retained_items"], result["notebook_urls"]), (4, 3))

    def test_verification_upgrade_rejected(self):
        _, merged = self.complete_run()
        self.write_inbox([self.item("VN", "Discovery only")], "VN")
        with self.assertRaisesRegex(tnt.RunError, "upgrade verification"):
            tnt.validate(self.root, "test-run")

    def test_new_url_cannot_be_invented_at_merge(self):
        _, merged = self.complete_run()
        merged[0]["URL"] = "https://example.test/not-in-input"
        self.write_inbox(merged)
        with self.assertRaisesRegex(tnt.RunError, "source URL"):
            tnt.validate(self.root, "test-run")

    def test_unchecked_record_in_main_stream_rejected(self):
        self.complete_run()
        path = self.folder / tnt.FILES["VN"]
        path.write_text(path.read_text(encoding="utf-8").replace("Verification: Primary checked", "Verification: Discovery only"), encoding="utf-8")
        with self.assertRaisesRegex(tnt.RunError, "wrong section"):
            tnt.validate(self.root, "test-run")

    def test_credentials_in_url_rejected(self):
        self.complete_run()
        item = self.item()
        item["URL"] = "https://name:secret@example.test/item"
        self.write_inbox([item], "VN")
        with self.assertRaisesRegex(tnt.RunError, "without credentials"):
            tnt.validate(self.root, "test-run")

    def test_missing_required_field_rejected(self):
        self.complete_run()
        item = self.item()
        del item["Evidence checked"]
        self.write_inbox([item], "VN")
        with self.assertRaisesRegex(tnt.RunError, "missing Evidence checked"):
            tnt.validate(self.root, "test-run")

    def test_missing_instruction_version_rejected(self):
        self.complete_run()
        path = self.folder / tnt.FILES["VN"]
        text = path.read_text(encoding="utf-8").replace("Instruction version: test-version\n", "")
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(tnt.RunError, "Instruction version"):
            tnt.validate(self.root, "test-run")

    def test_item_limit_is_enforced(self):
        self.complete_run()
        self.write_inbox([self.item(name=f"VN-{i}") for i in range(21)], "VN")
        with self.assertRaisesRegex(tnt.RunError, "exceeds max"):
            tnt.validate(self.root, "test-run")


if __name__ == "__main__":
    unittest.main()
