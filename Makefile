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
.PHONY: help serve build check post publish

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /\1|/' \
	  | awk -F'|' '{ printf "  %-9s %s\n", $$1, $$2 }'
	@echo
	@echo '  make post TITLE="Some post title" TOPIC=ai-ml'
	@echo '  make publish SLUG=some-post-title'
	@echo
	@echo "  topics: $$(sed -n 's/^- key: //p' _data/topics.yml | tr '\n' ' ')(or none, for Other)"

serve: ## Preview at localhost:4000, drafts included, reloading on save
	$(BUNDLE) jekyll serve --drafts --livereload

build: ## Production build into _site/
	JEKYLL_ENV=production $(BUNDLE) jekyll build

check: build ## What CI gates on: the build, then the link and image check
	$(BUNDLE) htmlproofer ./_site --disable-external

# TOPIC is checked against _data/topics.yml because a misspelled key is not an
# error anywhere else: the post would just land in Other.
post: ## Start a draft in _drafts/<slug>.md (TOPIC optional)
	@test -n '$(TITLE)' || { echo 'usage: make post TITLE="Some post title" [TOPIC=ai-ml]'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@test ! -f '_drafts/$(SLUG).md' || { echo '_drafts/$(SLUG).md already exists'; exit 1; }
	@test -z '$(TOPIC)' || grep -qx -- '- key: $(TOPIC)' _data/topics.yml \
	  || { echo "unknown topic '$(TOPIC)' — one of: $$(sed -n 's/^- key: //p' _data/topics.yml | tr '\n' ' ')"; exit 1; }
	@mkdir -p _drafts
	@printf '%s\n' \
	  '---' \
	  'title: "$(TITLE)"' \
	  'topics: [$(TOPIC)]' \
	  'excerpt: ""' \
	  '---' \
	  '' \
	  > '_drafts/$(SLUG).md'
	@echo 'wrote _drafts/$(SLUG).md — `make serve` shows it, the live site does not'

publish: ## Move _drafts/<slug>.md into _posts/, dated today
	@test -n '$(SLUG)' || { echo 'usage: make publish SLUG=<slug>'; exit 1; }
	@test -f '_drafts/$(SLUG).md' || { echo 'no such draft: _drafts/$(SLUG).md'; exit 1; }
	@test ! -f '_posts/$(DATE)-$(SLUG).md' || { echo '_posts/$(DATE)-$(SLUG).md already exists'; exit 1; }
	@mkdir -p _posts
	@git mv '_drafts/$(SLUG).md' '_posts/$(DATE)-$(SLUG).md' 2>/dev/null \
	  || mv '_drafts/$(SLUG).md' '_posts/$(DATE)-$(SLUG).md'
	@echo 'published -> _posts/$(DATE)-$(SLUG).md -> /posts/$(SLUG)/'
