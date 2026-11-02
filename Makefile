# Convenience targets for the K1 repository.
#
# CI is the authority: .github/workflows/ci.yml runs the claim-map lint, the
# path guard, the wording lint, and the full pytest suite. These targets mirror
# those commands so a contributor can run the same checks locally on a machine
# that is allowed to execute the project (see AGENTS.md: K-project execution is
# Kaggle/CI only on the 2011 laptop).

PYTHON ?= python3

.PHONY: check claim-map paths wording test paper

check: claim-map paths wording

claim-map:
	$(PYTHON) tools/check_claim_map.py

paths:
	$(PYTHON) tools/check_repo_paths.py

wording:
	$(PYTHON) tools/check_report_wording.py

test:
	$(PYTHON) -m pytest -q --tb=short

paper:
	xelatex -interaction=nonstopmode -halt-on-error -file-line-error paper0_two_clocks.tex
	xelatex -interaction=nonstopmode -halt-on-error -file-line-error paper0_two_clocks.tex
