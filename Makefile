VAULT ?= $(HOME)/obsidian-vault

.PHONY: sync serve publish clean

sync:
	python3 sync_obsidian.py "$(VAULT)"

serve: sync
	hugo server

publish: sync
	hugo --gc --minify --baseURL "https://envoss11.github.io/"

clean:
	rm -rf public resources .sync_state.json
