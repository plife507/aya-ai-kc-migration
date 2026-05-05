.PHONY: validate install-dry-run

validate:
	./scripts/validate.sh

install-dry-run:
	./scripts/install-bundle.sh --dry-run
