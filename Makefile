# The whole interface to this site. Run `make` on its own for the list.
#
# Everything goes through `bundle exec`, so what runs locally is what
# Gemfile.lock pins, which is what .github/workflows/deploy.yml runs too.

BUNDLE := bundle exec
DATE   := $(shell date +%Y-%m-%d)

# Title -> filename slug: lowercase, non-alphanumerics collapse to one dash,
# no leading or trailing dash.
SLUG ?= $(shell printf '%s' '$(TITLE)' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//')

.DEFAULT_GOAL := help
.PHONY: help serve build check entry sync-books

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /\1|/' \
	  | awk -F'|' '{ printf "  %-9s %s\n", $$1, $$2 }'
	@echo
	@echo '  make entry SECTION=writing TITLE="Some title"   (reading|writing|projects)'

serve: ## Preview at localhost:4000, unpublished entries included, reloading on save
	$(BUNDLE) jekyll serve --unpublished --livereload

build: ## Production build into _site/
	JEKYLL_ENV=production $(BUNDLE) jekyll build

check: build ## What CI gates on: the build, then the link and image check
	$(BUNDLE) htmlproofer ./_site --disable-external

# Sections are the collections in _config.yml. A new entry starts unpublished;
# flip `published` to true (or delete the line) when it is ready.
SECTIONS := reading writing projects
DIR_reading  := _books
DIR_writing  := _writing
DIR_projects := _projects

entry: ## Start an entry: make entry SECTION=writing TITLE="..."
	@case ' $(SECTIONS) ' in *' $(SECTION) '*) ;; *) echo 'usage: make entry SECTION=<$(SECTIONS)> TITLE="..."'; exit 1;; esac
	@test -n '$(TITLE)' || { echo 'a TITLE is required'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@f='$(DIR_$(SECTION))/$(if $(filter writing,$(SECTION)),$(DATE)-)$(SLUG).md'; \
	  test ! -f "$$f" || { echo "$$f already exists"; exit 1; }; \
	  mkdir -p '$(DIR_$(SECTION))'; \
	  printf '%s\n' '---' 'title: "$(TITLE)"' 'published: false' 'excerpt: ""' '---' '' > "$$f"; \
	  echo "wrote $$f — unpublished; \`make serve\` shows it, the live site does not"

sync-books: ## Pull the public Goodreads shelf into _books/ (DRY=1 to preview)
	python3 tools/goodreads_sync.py $(if $(DRY),--dry-run)
