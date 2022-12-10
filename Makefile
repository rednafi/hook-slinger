path := .

define Comment
	- Run `make help` to see all the available options.
	- Run `make lint` to run the linter.
	- Run `make lint-check` to check linter conformity.
	- Run `dep-lock` to lock the deps in 'requirements.txt' and 'requirements-dev.txt'.
	- Run `dep-sync` to sync current environment up to date with the locked deps.
endef


.PHONY: lint
lint: black ruff mypy	## Apply all the linters.


.PHONY: lint-check
lint-check:  ## Check whether the codebase satisfies the linter rules.
	@echo
	@echo "Checking linter rules..."
	@echo "========================"
	@echo
	@black --check $(path)
	@ruff $(path)
	@echo 'y' | mypy $(path) --install-types


.PHONY: black
black: ## Apply black.
	@echo
	@echo "Applying black..."
	@echo "================="
	@echo
	@black --fast $(path)
	@echo


.PHONY: ruff
ruff: ## Apply ruff.
	@echo "Applying ruff..."
	@echo "================"
	@echo
	@ruff --fix $(path)


.PHONY: mypy
mypy: ## Apply mypy.
	@echo
	@echo "Applying mypy..."
	@echo "================="
	@echo
	@mypy $(path)


.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: dep-lock
dep-lock: ## Freeze deps in 'requirements.txt' file.
	@pip-compile requirements.in -o requirements.txt --no-emit-options
	@pip-compile requirements-dev.in -o requirements-dev.txt --no-emit-options


.PHONY: dep-sync
dep-sync: ## Sync venv installation with 'requirements.txt' file.
	@pip-sync


.PHONY: test
test: ## Run the tests against the current version of Python.
	export PYTHONWARNINGS="ignore" && pytest -v -s -k 'not integration'


.PHONY: create-topology
create-topology: ## Creates topology diagram from docker compose file.
	@docker run \
	--rm -it \
	--name dcv \
	-v /home/rednafi/workspace/personal/hook-slinger:/input pmsipilot/docker-compose-viz \
	render -m image \
	--force docker-compose.yml \
	--output-file=topology.png \
	--no-volumes \
	--no-networks


.PHONY: start-servers
start-servers: ## Start the app, worker and monitor.
	docker compose up --build -d


.PHONY: stop-servers
stop-servers: ## Stop the app, worker and monitor.
	docker system prune
	docker compose down -t 1


.PHONY: start-tests
start-tests: ## Start the servers and execute the tests.
	docker compose -f docker-compose-ci.yml up --build -d


.PHONY: app-logs
app-logs: ## Explore the application server container logs.
	docker logs wh_app -f


.PHONY: worker-logs
worker-logs: ## Explore the worker instance container logs.
	docker logs hook-slinger_worker_1 -f


.PHONY: worker-scale
worker-scale:
	docker compose up -d --build --scale worker=$(n)
