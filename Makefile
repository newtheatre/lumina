vcs_rev=$(shell git describe)

test:
	PYTHONPATH=src/.:tests/. pytest tests/unit

build:
	mkdir -p dependencies
	poetry export -o dependencies/requirements.txt
	sam build

strip_botocore:
	poetry run bin/strip-botocore.py

env:
	@echo "AWS_VAULT: $(AWS_VAULT)"
	@echo "VCS_REV: $(vcs_rev)"
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

deploy: env build strip_botocore
	sam deploy --parameter-overrides "ParameterKey=Environment,ParameterValue=prod ParameterKey=VcsRev,ParameterValue=$(vcs_rev)"

.PHONY: test build strip_botocore deploy-sandbox deploy-prod
