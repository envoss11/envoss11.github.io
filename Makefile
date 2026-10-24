# The whole interface to this site. Run `make` on its own for the list.
#
# Everything goes through `bundle exec`, so what runs locally is what
# Gemfile.lock pins, which is what .github/workflows/deploy.yml runs too.

BUNDLE := bundle exec
DATE   := $(shell date +%Y-%m-%d)

# Title -> filename slug: lowercase, non-alphanumerics collapse to one dash,
# no leading or trailing dash.
SLUG ?= $(shell printf '%s' '$(TITLE)' | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$$//')

TOPICS      = $(shell sed -n 's/^- key: //p' _data/topics.yml | tr '\n' ' ')
NOTE_TOPICS = $(shell sed -n 's/^- key: //p' _data/note_topics.yml | tr '\n' ' ')

.DEFAULT_GOAL := help
.PHONY: help serve build check post publish note book session next touch

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /\1|/' \
	  | awk -F'|' '{ printf "  %-9s %s\n", $$1, $$2 }'
	@echo
	@echo '  make post TITLE="Some post title" TOPIC=evaluation [FROM_NOTE=<note-slug>]'
	@echo '  make publish SLUG=some-post-title'
	@echo '  make note TITLE="Some note title" TOPIC=evals-statistics [LOCAL=1]'
	@echo '  make book TITLE="Either/Or" AUTHOR="Søren Kierkegaard" TOPIC=philosophy'
	@echo '  make session [NOTE=either-or] [LABEL="Diapsalmata"]'
	@echo '  make next'
	@echo '  make touch SLUG=some-note-title'
	@echo
	@echo "  post topics: $(TOPICS)(or none, for Other)"
	@echo "  note topics: $(NOTE_TOPICS)"

serve: ## Preview at localhost:4000, drafts and private notes included
	$(BUNDLE) jekyll serve --drafts --unpublished --livereload

build: ## Production build into _site/
	JEKYLL_ENV=production $(BUNDLE) jekyll build

check: build ## What CI gates on: the build, then the link and image check
	$(BUNDLE) htmlproofer ./_site --disable-external

# TOPIC is checked against _data/topics.yml because a misspelled key is not an
# error anywhere else: the post would just land in Other. FROM_NOTE, when set,
# must name a file in _notes/; the post then links back to that note.
post: ## Start a draft in _drafts/<slug>.md (TOPIC, FROM_NOTE optional)
	@test -n '$(TITLE)' || { echo 'usage: make post TITLE="Some post title" [TOPIC=evaluation] [FROM_NOTE=<note-slug>]'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@test ! -f '_drafts/$(SLUG).md' || { echo '_drafts/$(SLUG).md already exists'; exit 1; }
	@test -z '$(TOPIC)' || grep -qx -- '- key: $(TOPIC)' _data/topics.yml \
	  || { echo "unknown topic '$(TOPIC)' — one of: $(TOPICS)"; exit 1; }
	@test -z '$(FROM_NOTE)' || test -f '_notes/$(FROM_NOTE).md' || test -f '_notes/local/$(FROM_NOTE).md' \
	  || { echo 'no such note: _notes/$(FROM_NOTE).md'; exit 1; }
	@mkdir -p _drafts
	@printf '%s\n' \
	  '---' \
	  'title: "$(TITLE)"' \
	  'topics: [$(TOPIC)]' \
	  'excerpt: ""' \
	  $(if $(FROM_NOTE),'from_note: $(FROM_NOTE)',) \
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

# Notes, books, and sessions go through bin/study, which reads the same
# variables. A note starts private; it goes live when its front matter says
# `published: true`. LOCAL=1 puts it in _notes/local/ instead: gitignored, so
# never committed or deployed, but still shown by `make serve`.
note: ## Start a private note in _notes/<slug>.md (TOPIC required, LOCAL=1 optional)
	@ruby bin/study note

book: ## Start a book note with its first session open (TOPIC required)
	@ruby bin/study book

session: ## Add today's session to a note and open it (NOTE optional: defaults to the last one)
	@ruby bin/study session

next: ## What is in progress, linked-but-unwritten, and queued
	@ruby bin/study next

touch: ## Set a note's updated: date to today (a session does this for you)
	@test -n '$(SLUG)' || { echo 'usage: make touch SLUG=<note-slug>'; exit 1; }
	@f=$$(ls _notes/$(SLUG).md _notes/local/$(SLUG).md 2>/dev/null | head -1); \
	  test -n "$$f" || { echo 'no such note: _notes/$(SLUG).md'; exit 1; }; \
	  grep -q '^updated:' "$$f" || { echo "$$f has no updated: line"; exit 1; }; \
	  perl -pi -e 's/^updated:.*/updated: $(DATE)/' "$$f" && echo "$$f updated: $(DATE)"
