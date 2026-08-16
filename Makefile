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
.PHONY: help serve build check draft wip publish

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /  \1|/' \
	  | awk -F'|' '{ printf "  %-10s %s\n", $$1, $$2 }'
	@echo
	@echo '  make draft TITLE="Some post title"'
	@echo '  make wip   TITLE="Something to think about in public"'
	@echo '  make publish SLUG=some-post-title'

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

# The tier between a draft and a post: live at /posts/wip/<slug>/, but noindex,
# out of the sitemap and out of RSS. The date goes in the front matter here
# rather than the filename — the drawer on /posts/ sorts on it, and a note
# without one falls back to sorting by filename.
wip: ## Scaffold _wip/<slug>.md + _research/<slug>/ from a title
	@test -n '$(TITLE)' || { echo 'usage: make wip TITLE="Some note title"'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@test ! -f '_wip/$(SLUG).md' || { echo '_wip/$(SLUG).md already exists'; exit 1; }
	@mkdir -p _wip '_research/$(SLUG)'
	@printf '%s\n' \
	  '---' \
	  'title: "$(TITLE)"' \
	  'date: $(DATE)' \
	  'excerpt: ""' \
	  'tags_list:' \
	  '  - ""' \
	  '---' \
	  '' \
	  '## The dump' \
	  '' \
	  '## What I found' \
	  '' \
	  '## Where this goes' \
	  '' \
	  > '_wip/$(SLUG).md'
	@printf '%s\n' \
	  '# Working notes for _wip/$(SLUG).md' \
	  '' \
	  'Raw pulls, scripts, and sources. Never built — Jekyll skips _-prefixed dirs.' \
	  > '_research/$(SLUG)/notes.md'
	@echo 'wrote _wip/$(SLUG).md and _research/$(SLUG)/  ->  /posts/wip/$(SLUG)/'

# One target for both sources. _wip/ is checked first: a slug that exists in
# both is ambiguous and is an error rather than a guess.
publish: ## Move a note out of _wip/ or _drafts/ into _posts/, stamped today
	@test -n '$(SLUG)' || { echo 'usage: make publish SLUG=<slug>'; exit 1; }
	@test ! \( -f '_wip/$(SLUG).md' -a -f '_drafts/$(SLUG).md' \) \
	  || { echo '$(SLUG) exists in both _wip/ and _drafts/ — remove one first'; exit 1; }
	@test -f '_wip/$(SLUG).md' -o -f '_drafts/$(SLUG).md' \
	  || { echo 'no such note: _wip/$(SLUG).md or _drafts/$(SLUG).md'; exit 1; }
	@test ! -f '_posts/$(DATE)-$(SLUG).md' || { echo '_posts/$(DATE)-$(SLUG).md already exists'; exit 1; }
	@src=$$(test -f '_wip/$(SLUG).md' && echo '_wip/$(SLUG).md' || echo '_drafts/$(SLUG).md'); \
	  git mv "$$src" '_posts/$(DATE)-$(SLUG).md' 2>/dev/null \
	    || mv "$$src" '_posts/$(DATE)-$(SLUG).md'; \
	  echo "published $$src  ->  _posts/$(DATE)-$(SLUG).md  ->  /posts/$(SLUG)/"
	@grep -q '^date:' '_posts/$(DATE)-$(SLUG).md' \
	  && echo 'drop the `date:` line from the front matter — the filename carries it now' \
	  || true
