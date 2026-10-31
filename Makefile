# The whole interface to this site. Run `make` on its own for the list.
#
# Everything goes through `bundle exec`, so what runs locally is what
# Gemfile.lock pins, which is what .github/workflows/deploy.yml runs too.

BUNDLE := bundle exec
DATE   := $(shell date +%Y-%m-%d)

# Title -> filename slug: lowercase, non-alphanumerics collapse to one dash.
SLUG ?= $(shell printf '%s' '$(TITLE)' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//')

.DEFAULT_GOAL := help
.PHONY: help serve build check post topo

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /\1|/' \
	  | awk -F'|' '{ printf "  %-7s %s\n", $$1, $$2 }'

serve: ## Preview at localhost:4000, unpublished posts included, reloading on save
	$(BUNDLE) jekyll serve --unpublished --livereload

build: ## Production build into _site/
	JEKYLL_ENV=production $(BUNDLE) jekyll build

check: build ## What CI gates on: the build, then the link and image check
	$(BUNDLE) htmlproofer ./_site --disable-external

post: ## Start an unpublished post: make post TITLE="..."
	@test -n '$(TITLE)' || { echo 'usage: make post TITLE="..."'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing; try another'; exit 1; }
	@f='_writing/$(DATE)-$(SLUG).md'; \
	  test ! -f "$$f" || { echo "$$f already exists"; exit 1; }; \
	  printf '%s\n' '---' 'title: "$(TITLE)"' 'published: false' 'excerpt: ""' '---' '' > "$$f"; \
	  echo "wrote $$f (unpublished; \`make serve\` shows it, the live site does not)"

topo: ## Redraw the contour drawing (a Gaussian mixture) into _includes/topo.svg
	python3 tools/topo.py _includes/topo.svg
