"""CLI do deploy massivo CC 653; nenhum destino é inferido automaticamente."""
from pathlib import Path
import sys
from cc_transactional_deploy import cli

if __name__ == "__main__":
    raise SystemExit(cli(Path(__file__).parent / "CC_MASS_DEPLOY_653/DEPLOY_PROFILE.json", sys.argv[1:]))
