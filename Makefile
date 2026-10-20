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
.PHONY: help serve build check post publish note touch

help: ## Show this list
	@echo "usage: make <target>"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | sed -E 's/^([a-z-]+):.*## /\1|/' \
	  | awk -F'|' '{ printf "  %-9s %s\n", $$1, $$2 }'
	@echo
	@echo '  make post TITLE="Some post title" TOPIC=evaluation [FROM_NOTE=<note-slug>]'
	@echo '  make publish SLUG=some-post-title'
	@echo '  make note TITLE="Some note title" TOPIC=evals-statistics'
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
	@test -z '$(FROM_NOTE)' || test -f '_notes/$(FROM_NOTE).md' \
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

# A note starts private. It goes live when its front matter says
# `published: true`; there is no separate publish step.
note: ## Start a private note in _notes/<slug>.md (TOPIC required)
	@test -n '$(TITLE)' || { echo 'usage: make note TITLE="Some note title" TOPIC=<topic>'; exit 1; }
	@test -n '$(SLUG)'  || { echo 'that title slugifies to nothing — try another'; exit 1; }
	@test '$(SLUG)' != index || { echo 'a note cannot be slugged "index" — it would replace /notes/'; exit 1; }
	@test ! -f '_notes/$(SLUG).md' || { echo '_notes/$(SLUG).md already exists'; exit 1; }
	@test -n '$(TOPIC)' && grep -qx -- '- key: $(TOPIC)' _data/note_topics.yml \
	  || { echo "TOPIC must be one of: $(NOTE_TOPICS)"; exit 1; }
	@mkdir -p _notes
	@printf '%s\n' \
	  '---' \
	  'title: "$(TITLE)"' \
	  'topic: $(TOPIC)' \
	  'status: idea          # idea | wip | complete' \
	  'updated: $(DATE)' \
	  'published: false      # true puts it on the live site' \
	  '# writing: evaluation # optional: also list it on /writing/ under this category' \
	  'excerpt: ""' \
	  '---' \
	  '' \
	  > '_notes/$(SLUG).md'
	@echo 'wrote _notes/$(SLUG).md — private until `published: true`'

touch: ## Set a note's updated: date to today
	@test -n '$(SLUG)' || { echo 'usage: make touch SLUG=<note-slug>'; exit 1; }
	@test -f '_notes/$(SLUG).md' || { echo 'no such note: _notes/$(SLUG).md'; exit 1; }
	@grep -q '^updated:' '_notes/$(SLUG).md' || { echo '_notes/$(SLUG).md has no updated: line'; exit 1; }
	@perl -pi -e 's/^updated:.*/updated: $(DATE)/' '_notes/$(SLUG).md'
	@echo '_notes/$(SLUG).md updated: $(DATE)'
