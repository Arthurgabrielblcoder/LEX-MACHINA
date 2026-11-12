"""QA-02 first independent legal-audit wave; curated conclusions, deterministic rendering."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "derived/qa02_independent_legal_audit"
CORPUS = HERE / "derived/candidate_cc_001_2046/CC2002_CC13.entenda.jsonl"
INVENTORY = OUT / "QA02_RISK_INVENTORY.json"
AS_OF = "2026-11-12"
CAMARA = "https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html"

# One independent rule statement per examined record: requirements, exceptions and consequence actually checked.
RULES = {
  "CC2002:ART.63": "Insufficient foundation assets go to a foundation with equal/similar purpose unless the founder validly directed otherwise.",
  "CC2002:ART.66": "Foundation oversight belongs to the territorially competent state/DF public prosecutor, cumulatively in each state of activity.",
  "CC2002:ART.138": "A substantial, objectively recognizable error makes the transaction voidable, not automatically void.",
  "CC2002:ART.143": "A merely arithmetical error permits correction of the declaration rather than avoidance of the transaction.",
  "CC2002:ART.157": "Lesion requires manifest contemporaneous imbalance plus urgent need or inexperience; supplementation/reduction can preserve the deal.",
  "CC2002:ART.202": "Prescription is interrupted once by a listed cause and restarts under the sole paragraph; procedural citation effects follow CPC art. 240.",
  "CC2002:ART.235": "Fortuitous deterioration of a certain thing lets the creditor resolve or accept it with proportional price reduction; fault invokes art. 236.",
  "CC2002:ART.241": "A costless improvement to a thing to be returned benefits the creditor without indemnity; debtor-funded improvement follows art. 242.",
  "CC2002:ART.286": "Credit assignment is allowed unless nature, law or agreement bars it; a non-assignment clause affects a good-faith assignee only if in the instrument.",
  "CC2002:ART.302": "The assuming debtor cannot invoke defenses personal to the original debtor, while objective defenses of the debt may remain.",
  "CC2002:ART.406": "The statutory rate is Selic minus the art. 389 index, floored at zero and applied by the CMN/Bacen methodology.",
  "CC2002:ART.421-A": "Civil/business contracts are rebuttably presumed symmetric, subject to special regimes, negotiated interpretation/risk allocation and exceptional review.",
  "CC2002:ART.424": "An adhesion clause prospectively waiving a right inherent to the transaction is void; the rest of the contract is not automatically void.",
  "CC2002:ART.468": "Nomination is communicated within five days unless otherwise set, and the nominee's acceptance must use the original contract's form.",
  "CC2002:ART.585": "Simultaneous borrowers are jointly liable to the lender for obligations from the shared gratuitous loan.",
  "CC2002:ART.698": "A total or partial del credere clause creates joint liability and presumptively higher remuneration unless otherwise agreed.",
  "CC2002:ART.807": "A contract constituting an annuity requires a public deed as a validity formality.",
  "CC2002:ART.869": "Useful management binds the owner and requires reimbursement, statutory interest and loss compensation, judged by circumstances at expenditure time.",
  "CC2002:ART.883": "A transfer made for an unlawful/immoral/prohibited purpose is not recoverable and is judicially directed to local charity.",
  "CC2002:ART.887": "A credit instrument is literal and autonomous and has effect only if statutory formal requirements are met.",
  "CC2002:ART.982": "Business/simple classification follows entrepreneurial activity, with mandatory exceptions for corporations and cooperatives.",
  "CC2002:ART.990": "Partners in an unregistered partnership have unlimited joint liability; the contracting partner lacks benefit of prior execution.",
  "CC2002:ART.1069": "Fiscal council duties include quarterly examination, minutes, annual opinion, reporting wrongdoing, exact assembly triggers and continuation in liquidation.",
  "CC2002:ART.1097": "Affiliation covers controlled, affiliated or simple-participation capital relationships; reciprocal ownership is not required by the text.",
  "CC2002:ART.1108": "After liabilities are paid and remainder divided, the liquidator must convene the partners for final accounts.",
  "CC2002:ART.1146": "The buyer answers for properly booked pre-transfer debts; seller remains jointly liable for one year from publication or maturity.",
  "CC2002:ART.1217": "A good-faith possessor is not liable for loss/deterioration not caused by that possessor.",
  "CC2002:ART.1234": "The finder who returns property receives at least 5% plus conservation/transport costs unless the owner abandons it; judicial factors set the reward.",
  "CC2002:ART.1293": "A compensated aqueduct requires a lawful water purpose/no considerable agricultural-industrial harm and carries future-damage, undergrounding and conservation safeguards.",
  "CC2002:ART.1343": "A new floor/building creating units on common land requires unanimous condominium approval.",
  "CC2002:ART.1440": "A prior mortgage does not bar rural pledge but retains its priority and scope on enforcement.",
  "CC2002:ART.1470": "Legal-pledge creditors may take possession before court only on danger in delay and must provide a receipt; art. 1.471 requires prompt homologation.",
  "CC2002:ART.1496": "Registration doubt does not prevent prenotation; favorable decision within 90 days preserves priority, otherwise a renewed filing gets a new number.",
  "CC2002:ART.1503": "Railway mortgage creditors cannot obstruct operation or administration-approved changes to track, dependencies or equipment.",
  "CC2002:ART.1561": "Putative marriage effects depend separately on each spouse's good faith and always protect children through annulment judgment.",
  "CC2002:ART.1673": "Under final participation, each spouse's own assets include pre- and post-marriage acquisitions, with exclusive management and free disposal of movables.",
  "CC2002:ART.1686": "One spouse's debts beyond that spouse's moiety do not bind the other spouse or heirs, subject to distinct legal bases for joint/common-benefit debt.",
  "CC2002:ART.1710": "All maintenance payments are updated by a regularly established official index; adjustment differs from substantive revision.",
  "CC2002:ART.1726": "Stable union can be converted to marriage; current registry law also provides an optional extrajudicial route.",
  "CC2002:ART.1743": "Technical, complex or distant management may be partially delegated to a person/entity only with judicial approval.",
  "CC2002:ART.1752": "Tutor liability, reimbursement/remuneration, protutor gratification and joint liability of supervisors/contributors are separate consequences.",
  "CC2002:ART.1765": "Tutor serves two years and may continue only if willing and the judge finds continuation convenient for the minor.",
  "CC2002:ART.1787": "Law at death governs succession and capacity to inherit, notwithstanding later inventory/partition.",
  "CC2002:ART.1790": "The formally printed special regime is unconstitutional; Tema 809 applies art. 1.829 without treating art. 1.790 as legislatively repealed.",
  "CC2002:ART.1816": "Exclusion is personal; descendants step in, and the excluded person cannot administer, enjoy or later inherit those assets.",
  "CC2002:ART.1829": "Legitimate succession follows four classes; spousal/partner competition with descendants depends on the statutory marital-property exceptions.",
  "CC2002:ART.1874": "The closed will returns to the testator and the notary records place and full date of approval/delivery.",
  "CC2002:ART.1985": "Executorship is personal, non-heritable and nondelegable, but special-power representation is allowed.",
  "CC2002:ART.2036": "Urban leases within special legislation remain governed by that legislation.",
  "CC2002:ART.2038": "New civil emphyteusis is barred; old grants remain transitional with restrictions, while federal foreshore land follows special law.",
  "CC2002:ART.2044": "The Code entered into force one year after publication, subject to intertemporal rules.",
  "CC2002:ART.2045": "The 1916 Civil Code and Part One of the Commercial Code were expressly repealed without erasing accrued effects or unrepealed commercial law.",
}

SPECIAL_SOURCES = {
  "CC2002:ART.157": ["https://scon.stj.jus.br/SCON/GetInteiroTeorDoAcordao?dt_publicacao=18%2F04%2F2024&num_registro=202101760559"],
  "CC2002:ART.202": ["https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/09112021-Para-Terceira-Turma--seja-qual-for-o-fundamento--prescricao-so-e-interrompida-uma-vez-sob-o-CC2002.aspx"],
  "CC2002:ART.406": ["https://www.bcb.gov.br/content/estabilidadefinanceira/especialnor/Resolu%C3%A7%C3%A3o5171.pdf"],
  "CC2002:ART.1726": ["https://atos.cnj.jus.br/atos/detalhar/4996"],
  "CC2002:ART.1790": ["https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=809", "https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/17082021-Inconstitucionalidade-da-distincao-de-regimes-sucessorios-alcanca-decisao-anterior-que-prejudicou-companheira.aspx"],
  "CC2002:ART.1829": ["https://portal.stf.jus.br/jurisprudenciaRepercussao/tema.asp?num=809", "https://scon.stj.jus.br/SCON/GetInteiroTeorDoAcordao?dt_publicacao=23%2F05%2F2025&num_registro=202403854742"],
}

FINDINGS = {
  "CC2002:ART.1069": dict(field="o_que_diz", severity="ALTO", nature="OMISSAO_DE_CONDICOES_E_DEVER",
    excerpt="convocam assembleia nas hipóteses legais",
    basis="CC art. 1.069, V-VI: atraso superior a 30 dias ou motivo grave/urgente; manutenção dos deveres durante liquidação.",
    consequence="The reader cannot identify the exact trigger or that all listed duties continue during liquidation.",
    correction="State the 30-day trigger, grave/urgent alternative and liquidation continuation explicitly.", confidence="ALTA", human_review=True),
  "CC2002:ART.1097": dict(field="o_que_diz", severity="MÉDIO", nature="GENERALIZACAO_INEXATA",
    excerpt="quando sua participação recíproca se enquadra",
    basis="CC art. 1.097 refers to capital relationships of control, affiliation or simple participation, not necessarily reciprocal participation.",
    consequence="May teach mutual ownership as a necessary element of affiliation.",
    correction="Replace reciprocal participation with capital relationship and defer categories to arts. 1.098-1.100.", confidence="ALTA", human_review=False),
  "CC2002:ART.1234": dict(field="atencao", severity="MÉDIO", nature="CONSEQUENCIA_VAGA_NAO_ANCORADA",
    excerpt="Má conduta do descobridor pode reduzir efeitos",
    basis="CC arts. 1.234-1.235 provide reward criteria and liability for fraudulent conduct; they do not express a generic reduction of effects.",
    consequence="Obscures the actual statutory consequence and may suggest discretionary reduction without a legal basis.",
    correction="Identify art. 1.235 liability precisely or omit the vague sentence.", confidence="MÉDIA", human_review=True),
  "CC2002:ART.1293": dict(field="o_que_diz", severity="ALTO", nature="OMISSAO_DE_DIREITOS_E_ENCARGOS",
    excerpt="Canais podem atravessar imóveis alheios, com indenização prévia",
    basis="CC art. 1.293 §§1-3 additionally grants future-damage compensation, undergrounding in protected areas, least-harm construction, owner cost and conservation duty.",
    consequence="An overview covering the subtree omits material protections and continuing burdens on the aqueduct owner.",
    correction="Add all three paragraph safeguards and distinguish initial from future compensation.", confidence="ALTA", human_review=True),
  "CC2002:ART.1752": dict(field="o_que_diz", severity="ALTO", nature="OMISSAO_E_RESTRICAO_INDEVIDA_DE_SUJEITOS",
    excerpt="com responsabilidade solidária de quem colaborar no prejuízo",
    basis="CC art. 1.752 §§1-2 also grants modest protutor compensation and makes persons charged with supervision jointly liable, besides contributors to damage.",
    consequence="Wrongly narrows joint liability to active contributors and hides the protutor consequence.",
    correction="Name both supervisor and contributor categories and the protutor's modest gratification.", confidence="ALTA", human_review=True),
  "CC2002:ART.1765": dict(field="o_que_diz", severity="ALTO", nature="OMISSAO_DE_CONDICAO_CUMULATIVA",
    excerpt="podendo continuar se o juiz considerar conveniente ao menor",
    basis="CC art. 1.765 sole paragraph requires both the tutor's willingness and the judge's convenience finding.",
    consequence="Suggests judicial convenience alone can compel continuation beyond the two-year term.",
    correction="Express the tutor's willingness and judicial assessment as cumulative conditions.", confidence="ALTA", human_review=False),
  "CC2002:ART.1829": dict(field="o_que_diz", severity="ALTO", nature="OMISSAO_DE_EXCECOES_CENTRAIS",
    excerpt="com regras próprias de concorrência conjugal",
    basis="CC art. 1.829 I states concrete exceptions for universal community, mandatory separation and partial community without separate property; Tema 809 extends the regime to partners.",
    consequence="The central operative rule for descendant competition is not actually explained, risking a wrong inheritance allocation.",
    correction="State the statutory regimes and separate-property condition, plus partner extension and distinction from moiety.", confidence="ALTA", human_review=True),
}


def sha_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main():
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = [json.loads(s) for s in CORPUS.read_text(encoding="utf-8").splitlines()]
    active = {r["target_id"]: r for r in rows if r["status"] == "ACTIVE"}
    b_ids = set(inv["first_b_audit_wave"]["target_ids"])
    a_ids = {r["target_id"] for r in inv["stratified_a_sample"]["records"]}
    ids = b_ids | a_ids | set(inv["mandatory_sentinels"])
    if ids != set(RULES):
        raise RuntimeError(f"CURATION_COVERAGE mismatch: missing={sorted(ids-set(RULES))} extra={sorted(set(RULES)-ids)}")
    audited = []
    for target in sorted(ids, key=lambda t: (int(t.split("ART.")[1].split(":")[0].split("-")[0]), t)):
        r = active[target]
        content = json.dumps(r["content"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        group = (["B_OR_CORRECTION_WAVE"] if target in b_ids else []) + (["A_STRATIFIED_SAMPLE"] if target in a_ids else []) + (["MANDATORY_SENTINEL"] if target in inv["mandatory_sentinels"] else [])
        finding = FINDINGS.get(target)
        audited.append(dict(
            target_id=target, explanation_id=r["explanation_id"], origin_mission=next(x["mission"] for x in inv["priority_b_or_substantive_correction"]["records"] if x["target_id"] == target) if target in b_ids else next((x["mission"] for x in inv["stratified_a_sample"]["records"] if x["target_id"] == target), "SENTINEL"),
            audit_groups=group, norm="Lei 10.406/2002 (Código Civil)", as_of=AS_OF,
            sources=[dict(url=CAMARA, role="CURRENT_CONSOLIDATED_STATUTE", accessed_on=AS_OF)] +
                    [dict(url=u, role="SPECIAL_STATUTE_OR_PRECEDENT", accessed_on=AS_OF) for u in SPECIAL_SOURCES.get(target, [])],
            current_law_snapshot=r["source"]["source_text_snapshot"], source_snapshot_sha256=r["source"]["source_text_sha256"],
            independent_rule_summary=RULES[target], checks=dict(requirements=True, exceptions=True, consequences=True,
                fields=["o_que_diz", "o_que_significa", "exemplo_pratico", "atencao", "palavras_dificeis"]),
            entenda_content_sha256=sha_text(content), result="ACHADO" if finding else "SEM_ACHADO_NO_ESCOPO_VERIFICADO",
            comparison=(finding["basis"] if finding else "The five ENTENDA fields preserve the independently stated rule, its material limitation and legal consequence without an identified contradiction in this review scope."),
            finding=(dict(target_id=target, mission=r.get("batch_id"), problematic_field=finding["field"], problematic_excerpt=finding["excerpt"],
                          legal_basis=finding["basis"], nature=finding["nature"], severity=finding["severity"],
                          legal_or_pedagogical_consequence=finding["consequence"], correction_direction=finding["correction"],
                          confidence=finding["confidence"], human_review_required=finding["human_review"]) if finding else None)))
    findings = [r["finding"] for r in audited if r["finding"]]
    doc = dict(schema_version=1, mission="QA-02", checkpoint="WAVE_01", as_of=AS_OF,
               policy="Independent legal audit artifact; no editorial content or approval status changed. SEM_ACHADO is not an absolute guarantee.",
               universe=dict(active=inv["corpus"]["active"], priority_total=inv["priority_b_or_substantive_correction"]["total"],
                             priority_audited=len(b_ids), priority_pending=inv["priority_b_or_substantive_correction"]["total"]-len(b_ids),
                             a_universe=inv["stratified_a_sample"]["universe"], a_sample_audited=len(a_ids), sentinels=len(inv["mandatory_sentinels"])),
               audited_total=len(audited), findings_total=len(findings), finding_counts=dict(sorted(Counter(f["severity"] for f in findings).items())),
               records=audited)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "QA02_AUDIT_WAVE_01.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    queue = dict(schema_version=1, mission="QA-02", source="QA02_AUDIT_WAVE_01.json", total=len(findings),
                 order="CRÍTICO, ALTO, MÉDIO, BAIXO; then target_id",
                 findings=sorted(findings, key=lambda f: ({"CRÍTICO": 0, "ALTO": 1, "MÉDIO": 2, "BAIXO": 3}[f["severity"]], f["target_id"])))
    (OUT / "QA02_CORRECTION_QUEUE.json").write_text(json.dumps(queue, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    protected = {
      "corpus": hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
      "lookup": hashlib.sha256((HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_LOOKUP.IDX").read_bytes()).hexdigest(),
      "payload": hashlib.sha256((HERE / "derived/candidate_cc_001_2046/candidate_index/ENTENDA_PAYLOAD.DAT").read_bytes()).hexdigest(),
    }
    by_target = {r["target_id"]: r for r in audited}
    cp02 = [t for t in b_ids if 233 <= int(t.split("ART.")[1].split(":")[0].split("-")[0]) <= 965]
    cp03 = [t for t in b_ids if 966 <= int(t.split("ART.")[1].split(":")[0].split("-")[0]) <= 1510]
    cp04 = [t for t in b_ids if 1511 <= int(t.split("ART.")[1].split(":")[0].split("-")[0]) <= 2027]
    cp05 = sorted((b_ids - set(cp02) - set(cp03) - set(cp04)) | (set(inv["mandatory_sentinels"]) - b_ids))
    checkpoint_sets = (
      (2, "B_OBRIGACOES_E_CONTRATOS", cp02),
      (3, "B_EMPRESA_E_DIREITOS_REAIS", cp03),
      (4, "B_FAMILIA_E_SUCESSOES", cp04),
      (5, "DEMAIS_B_E_SENTINELAS", cp05),
      (6, "AMOSTRA_A_ESTRATIFICADA", sorted(a_ids)),
    )
    for number, title, target_ids in checkpoint_sets:
        cp_records = [by_target[t] for t in sorted(target_ids, key=lambda x: (int(x.split("ART.")[1].split(":")[0].split("-")[0]), x))]
        cp_findings = [r["finding"] for r in cp_records if r["finding"]]
        cp = dict(schema_version=1, mission="QA-02", checkpoint=number, title=title, as_of=AS_OF,
                  examined=len(cp_records), target_ids=[r["target_id"] for r in cp_records], pending_priority_after_wave=doc["universe"]["priority_pending"],
                  findings=len(cp_findings), finding_counts=dict(sorted(Counter(f["severity"] for f in cp_findings).items())),
                  protected_sha256=protected, records=cp_records)
        (OUT / f"QA02_CHECKPOINT_{number:02d}.json").write_text(json.dumps(cp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(dict(audited=len(audited), findings=dict(Counter(f["severity"] for f in findings)), pending=doc["universe"]["priority_pending"]), ensure_ascii=False))


if __name__ == "__main__":
    main()
