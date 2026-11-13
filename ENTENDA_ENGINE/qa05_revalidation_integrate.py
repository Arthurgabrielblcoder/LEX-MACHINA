"""Integrate independent cross-reviews for all 50 QA-05 corrections."""
import json
from collections import Counter

import qa05_prepare as prep


EDITORIAL = prep.OUT / "QA05_EDITORIAL_CORRECTIONS_50.json"
REVIEWS = (
    prep.OUT / "QA05_REVALIDATION_A_12.json",
    prep.OUT / "QA05_REVALIDATION_B_17.json",
    prep.OUT / "QA05_REVALIDATION_C_21.json",
)
OUTPUT = prep.OUT / "QA05_REVALIDATION_50.json"


def main():
    if prep.current_hashes() != prep.PROTECTED:
        raise RuntimeError("protected baseline hash mismatch")
    editorial = json.loads(EDITORIAL.read_text(encoding="utf-8"))["records"]
    proposals = {row["target_id"]: row for row in editorial}
    reviews = []
    sources = []
    for path in REVIEWS:
        document = json.loads(path.read_text(encoding="utf-8"))
        reviews.extend(document["records"])
        sources.append({"name": path.name, "sha256": prep.sha256(path),
                        "decision_counts": document["decision_counts"]})
    by_target = {row["target_id"]: row for row in reviews}
    if len(reviews) != 50 or len(by_target) != 50 or set(by_target) != set(proposals):
        raise RuntimeError("independent reviews do not cover exactly 50 unique targets")
    ordered = []
    for proposal in editorial:
        target = proposal["target_id"]
        review = by_target[target]
        if review["severity"] != proposal["severity"]:
            raise RuntimeError(f"severity mismatch: {target}")
        expected_hash = prep.json_sha(proposal["proposed_content"])
        if review.get("proposed_content_sha256") not in (None, expected_hash):
            raise RuntimeError(f"reviewed proposal hash mismatch: {target}")
        if review["decision"] != "CONFIRMED_CORRECTED":
            raise RuntimeError(f"unresolved independent review: {target} ({review['decision']})")
        editor = proposal["editor_identifier"]
        reviewer = review.get("reviewer", "")
        if editor and editor in reviewer:
            raise RuntimeError(f"reviewer is not independent: {target}")
        review["proposed_content_sha256"] = expected_hash
        review["editor_identifier"] = editor
        review["independence_confirmed"] = True
        ordered.append(review)
    counts = Counter(row["decision"] for row in ordered)
    document = {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP11", "as_of": prep.AS_OF,
        "status": "INDEPENDENT_REVALIDATION_COMPLETE", "total": 50,
        "decision_counts": dict(sorted(counts.items())), "source_modules": sources,
        "records": ordered,
    }
    prep.write_json(OUTPUT, document)
    prep.write_json(prep.OUT / "QA05_CHECKPOINT_11.json", {
        "schema_version": 1, "mission": "QA-05", "checkpoint": "CP11", "as_of": prep.AS_OF,
        "status": "COMPLETE", "total": 50, "confirmed_corrected": counts["CONFIRMED_CORRECTED"],
        "pending": 0, "source": OUTPUT.name, "source_sha256": prep.sha256(OUTPUT),
    })
    print(json.dumps({"revalidated": 50, "decisions": dict(counts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
