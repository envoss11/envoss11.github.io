source "https://rubygems.org"

# Jekyll directly, not the `github-pages` shim. The shim pins Jekyll 3.10 and
# restricts plugins to GitHub's allowlist; the site builds in Actions now
# (.github/workflows/deploy.yml), so neither limit applies.
gem "jekyll", "~> 4.4"

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-sitemap"
end

group :development do
  # `make check`, and the same gate CI runs before it deploys.
  gem "html-proofer", "~> 5.0"
end
