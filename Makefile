vcs_rev=$(shell git describe)

test:
	PYTHONPATH=app/. pytest tests/unit

build:
	mkdir -p dependencies
	poetry export -o dependencies/requirements.txt
	sam build


env:
	@echo "AWS_VAULT: $(AWS_VAULT)"
	@echo "VCS_REV: $(vcs_rev)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

deploy: env build
	sam deploy --parameter-overrides "ParameterKey=Environment,ParameterValue=prod ParameterKey=VcsRev,ParameterValue=$(vcs_rev)" --no-confirm-changeset

.PHONY: test build deploy-sandbox deploy-prod
