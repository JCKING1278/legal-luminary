source "https://rubygems.org"

# GitHub Pages compatibility
gem "github-pages", "~> 228", group: :jekyll_plugins

# Required for local development server
gem "webrick", "~> 1.8"

# Required for Ruby 3.4+ compatibility with Jekyll 3.9.3
gem "csv"
gem "logger"
gem "base64"
gem "bigdecimal"

# RSS feed parsing for legal news feeds
gem "feedjira", "~> 3.2"
gem "faraday", "~> 2.0"

# Windows and JRuby do not include zoneinfo files
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data", "~> 1.2024"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock http_parser.rb to v0.6.x (0.8.x can lack arm64-darwin-25 on RubyGems)
gem "http_parser.rb", "~> 0.6.0"
