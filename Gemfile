source "https://rubygems.org"

# GitHub Pages builds this site, so pin to the gem that mirrors its
# environment rather than to Jekyll directly.
gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-sitemap"
end

# Windows and JRuby don't ship zoneinfo files.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
