"""Build the isolated CC-09 candidate incrementally."""
from __future__ import annotations
import argparse, hashlib, importlib, json, tempfile
from collections import Counter
from pathlib import Path
import entenda_engine as E

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_700"
CONFIG = BATCH / "CC09_ENTENDA_CONFIG.json"
BASELINE = ROOT / "ENTENDA_ENGINE" / "derived" / "candidate_cc_001_550" / "CC2002_CC08.entenda.jsonl"
CORPUS, DRAFTS, MANIFEST, COVERAGE = BATCH / "CC2002_CC09.entenda.jsonl", BATCH / "CC09_DRAFTS.json", BATCH / "CC09_MANIFEST.json", BATCH / "CC09_COVERAGE.json"
INDEX_DIR, CHECKPOINTS = BATCH / "candidate_index", BATCH / "checkpoints"
EXPECTED_BASELINE_SHA256 = "c1951fe3af7f514c17376864fa8b3692564c6621249804afc6dc177f37dcb8bc"
BLOCKS = {"551_580": [str(n) for n in range(551,581)], "581_610": [str(n) for n in range(581,611)], "611_640": [str(n) for n in range(611,641)], "641_670": [str(n) for n in range(641,671)], "671_700": [str(n) for n in range(671,701)]}
MODULES = ("cc09_editorial_551_610", "cc09_editorial_611_670", "cc09_editorial_671_700")
def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2)+"\n").encode("utf-8"))
def all_rows():
    rows={}
    for name in MODULES:
        mod=importlib.import_module(name)
        if set(rows)&set(mod.ROWS): raise SystemExit("CC09_DUPLICATE_EDITORIAL_ROWS")
        rows.update(mod.ROWS)
    expected={str(n) for n in range(551,701)}
    if set(rows)!=expected: raise SystemExit("CC09_EDITORIAL_ROWS_MISMATCH")
    return rows
def render(rows, selected):
    return {"schema_version":1,"norma_id":"CC2002","template_version":"ENTENDA-T1","prompt_version":"CC09-DELEGATED-PRODUCTION-V1","review_status":"PENDING_HUMAN_REVIEW","authoring":{"method":"ARTICLE_SPECIFIC_AI_DRAFT_WITH_DELEGATED_LEGAL_REVIEW","mission":"CC-09","generated_on":"2026-11-08","human_approval_claimed":False},"explanations":[{"target_id":f"CC2002:ART.{n}","role":"OVERVIEW","semantic_autonomy":"AUTONOMOUS","editorial_reason":"Explicação específica do dispositivo vigente, auditada quanto a requisitos, sujeitos, exceções e consequências.","content":{k:rows[n][k] for k in ("o_que_diz","o_que_significa","exemplo_pratico","atencao","palavras_dificeis")},"external_layer_notes":[],"review_status":"PENDING_HUMAN_REVIEW","editorial_version":1} for n in selected]}
def build(through_block=5,out_dir=None):
    if sha(BASELINE.read_bytes())!=EXPECTED_BASELINE_SHA256: raise SystemExit("CC09_CC08_BASELINE_HASH_MISMATCH")
    names=list(BLOCKS)[:through_block]; selected=[n for name in names for n in BLOCKS[name]]
    ctx=E.NormContext("CC2002",config_path=CONFIG); existing=E.load_corpus(BASELINE); drafts=render(all_rows(),selected)
    records=E.stamp(drafts,ctx,existing=existing); E.validate_corpus(records,ctx)
    root=BATCH if out_dir is None else out_dir; corpus_path=root/CORPUS.name
    E.write_corpus(records,corpus_path,ctx); write_json(root/DRAFTS.name,drafts); im=E.build_entenda_index(ctx,records,root/"candidate_index")
    active=[r for r in records if r["status"]=="ACTIVE"]; new=[r for r in active if 551<=int(r["target_id"].split("ART.",1)[1].split(":",1)[0].split("-")[0])<=700]
    manifest={"schema_version":1,"mission":"CC-09","candidate_only":True,"deployed":False,"through_block":through_block,"completed_blocks":names,"cc08_records_preserved":len(existing),"active_total":len(active),"cc09_active":len(new),"cc09_review_status_counts":dict(sorted(Counter(r["review_status"] for r in new).items())),"corpus_sha256":sha(corpus_path.read_bytes()),"candidate_index":im,"production_index_modified":False}
    coverage={"schema_version":1,"scope":"CC2002 arts. 551 a 700","numbered_positions_examined":150,"article_targets_examined":150,"expected_current_explanations":150,"produced_explanations":len(new),"remaining_explanations":150-len(new),"intercalated_current_articles":[],"fully_revoked_without_active_explanation":[],"completed_blocks":names}
    write_json(root/MANIFEST.name,manifest); write_json(root/COVERAGE.name,coverage)
    if out_dir is None:
        name=names[-1]; members=BLOCKS[name]; br=[r for r in new if r["target_id"].split("ART.",1)[1].split(":",1)[0] in members]
        write_json(CHECKPOINTS/f"CC09_{name}.json",{"schema_version":1,"block":name,"expected":len(members),"produced":len(br),"complete":len(br)==len(members),"target_ids":[r["target_id"] for r in br],"records_sha256":sha(json.dumps(br,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()),"corpus_checkpoint_sha256":manifest["corpus_sha256"]})
    return manifest
def check():
    with tempfile.TemporaryDirectory(prefix=".cc09-check-",dir=BATCH) as td:
        tmp=Path(td); result=build(5,tmp); pairs=[(tmp/CORPUS.name,CORPUS),(tmp/DRAFTS.name,DRAFTS),(tmp/MANIFEST.name,MANIFEST),(tmp/COVERAGE.name,COVERAGE)]+[(tmp/"candidate_index"/n,INDEX_DIR/n) for n in ("ENTENDA_LOOKUP.IDX","ENTENDA_PAYLOAD.DAT","ENTENDA_BUILD_MANIFEST.json")]
        changed=[str(dst.relative_to(ROOT)) for src,dst in pairs if not dst.is_file() or src.read_bytes()!=dst.read_bytes()]
        if changed: raise SystemExit("CC09_NOT_REPRODUCIBLE: "+", ".join(changed))
        return result
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--through-block",type=int,default=5); p.add_argument("--check",action="store_true"); a=p.parse_args(); print(json.dumps(check() if a.check else build(a.through_block),ensure_ascii=False,indent=2))
