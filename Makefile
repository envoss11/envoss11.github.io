# The whole interface to this site. Run `make` on its own for the list.
#
# Everything goes through `bundle exec`, so what runs locally is what
# Gemfile.lock pins, which is what .github/workflows/deploy.yml runs too.

BUNDLE := bundle exec
DATE   := $(shell date +%Y-%m-%d)

# Title -> filename slug: lowercase, non-alphanumerics collapse to one dash,
# no leading or trailing dash. Matches the shape of the URLs already published.
SLUG := $(shell printf '%s' '$(TITLE)' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//')

.DEFAULT_GOAL := help
.PHONY: help serve build check draft publish

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /  \1|/' \
	  | awk -F'|' '{ printf "  %-10s %s\n", $$1, $$2 }'
	@echo
	@echo '  make draft TITLE="Some post title"'
	@echo '  make publish DRAFT=some-post-title'

serve: ## Preview at localhost:4000, drafts included, reloading on save
	$(BUNDLE) jekyll serve --drafts --livereload --incremental

build: ## Production build into _site/
	JEKYLL_ENV=production $(BUNDLE) jekyll build

check: build ## Build, then run the same link check CI runs
	$(BUNDLE) htmlproofer ./_site --disable-external

draft: ## Scaffold _drafts/<slug>.md from a title
	@test -n '$(TITLE)' || { echo 'usage: make draft TITLE="Some post title"'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@test ! -f '_drafts/$(SLUG).md' || { echo '_drafts/$(SLUG).md already exists'; exit 1; }
	@mkdir -p _drafts
	@printf '%s\n' \
	  '---' \
	  'title: "$(TITLE)"' \
	  'excerpt: ""' \
	  '# An image is optional. Drop the file in /assets/images/ and point at it here.' \
	  '# image_fit: contain letterboxes charts and screenshots instead of cropping them.' \
	  '# image: /assets/images/example-header.png' \
	  '# image_fit: contain' \
	  'tags_list:' \
	  '  - ""' \
	  '---' \
	  '' \
	  > '_drafts/$(SLUG).md'
	@echo 'wrote _drafts/$(SLUG).md — `make serve` shows it, publishing does not'

publish: ## Move a draft into _posts/, stamped with today's date
	@test -n '$(DRAFT)' || { echo 'usage: make publish DRAFT=<slug>'; exit 1; }
	@test -f '_drafts/$(DRAFT).md' || { echo 'no such draft: _drafts/$(DRAFT).md'; exit 1; }
	@test ! -f '_posts/$(DATE)-$(DRAFT).md' || { echo '_posts/$(DATE)-$(DRAFT).md already exists'; exit 1; }
	@git mv '_drafts/$(DRAFT).md' '_posts/$(DATE)-$(DRAFT).md' 2>/dev/null \
	  || mv '_drafts/$(DRAFT).md' '_posts/$(DATE)-$(DRAFT).md'
	@echo 'published _posts/$(DATE)-$(DRAFT).md  ->  /blog/$(DRAFT)/'
