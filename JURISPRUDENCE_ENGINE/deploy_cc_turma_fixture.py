"""CLI do fixture físico Turma B; nenhum destino é inferido automaticamente."""
from pathlib import Path
import sys
from cc_transactional_deploy import cli

if __name__ == "__main__":
    raise SystemExit(cli(Path(__file__).parent / "CC_TURMA_PHYSICAL_FIXTURE/DEPLOY_PROFILE.json", sys.argv[1:]))
