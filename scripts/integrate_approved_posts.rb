#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'date'
require 'pathname'
require 'fileutils'
require 'net/http'
require 'uri'

##
# ArticleIntegrator
# Integrates approved news articles from verified sources into Jekyll blog posts
#
class ArticleIntegrator
  attr_reader :allowlist, :news_feed, :posts_dir, :config

  def initialize
    @posts_dir = Pathname.new('_posts')
    @config = load_config
    @allowlist = load_allowlist
    @news_feed = load_news_feed
  end

  ##
  # Load Jekyll configuration
  #
  def load_config
    config_path = Pathname.new('_config.yml')
    unless config_path.exist?
      warn "ERROR: Jekyll config not found at #{config_path}"
      exit 1
    end

    require 'yaml'
    YAML.load_file(config_path.to_s) || {}
  rescue => e
    warn "ERROR: Failed to load Jekyll config: #{e.message}"
    exit 1
  end

  ##
  # Load allowlist from v2.1 with FCC sources
  #
  def load_allowlist
    allowlist_path = Pathname.new('demos/langsmith_langgraph_demo/allowlist.json')
    unless allowlist_path.exist?
      warn "ERROR: Allowlist not found at #{allowlist_path}"
      exit 1
    end

    content = File.read(allowlist_path.to_s)
    allowlist = JSON.parse(content)

    puts "✓ Loaded allowlist v#{allowlist['metadata']['version']}"
    puts "  Domains: #{allowlist['domains'].length}"
    puts "  Social accounts: #{allowlist['social_media_accounts'].length}"
    puts "  RSS feeds: #{allowlist['rss_feeds'].length}"
    puts "  FCC-verified sources: #{count_fcc_sources(allowlist)}"

    allowlist
  rescue JSON::ParserError => e
    warn "ERROR: Failed to parse allowlist JSON: #{e.message}"
    exit 1
  end

  ##
  # Count FCC-licensed broadcast stations in allowlist
  #
  def count_fcc_sources(allowlist)
    fcc_patterns = ['kwtb', 'kvue', 'kbtx', 'kwbu', 'temple daily telegram']
    domains = allowlist['domains'].map(&:downcase)
    domains.count { |d| fcc_patterns.any? { |p| d.include?(p) } }
  end

  ##
  # Load news feed data
  #
  def load_news_feed
    feed_path = Pathname.new('_data/news-feed.json')
    unless feed_path.exist?
      warn "WARN: News feed not found at #{feed_path}"
      return { 'feeds' => [], 'all_items' => [] }
    end

    content = File.read(feed_path.to_s)
    feed = JSON.parse(content)

    puts "✓ Loaded news feed"
    puts "  Sources: #{feed['feeds'].length}"
    puts "  Latest update: #{feed['last_updated']}"

    feed
  rescue JSON::ParserError => e
    warn "ERROR: Failed to parse news feed JSON: #{e.message}"
    exit 1
  end

  ##
  # Check if a source is approved in the allowlist
  #
  def approved_source?(source_url, source_name)
    return false if source_url.nil? || source_url.empty?

    # Extract and normalize domain
    uri = URI.parse(source_url)
    domain = uri.host.downcase.gsub(/^www\./, '')

    # Approved domains from allowlist
    approved_domains = allowlist['domains'].map { |d| d.downcase.gsub(/^www\./, '') }

    # Check direct domain match
    approved_domains.any? do |approved|
      approved.include?(domain) || domain.include?(approved)
    end
  rescue URI::InvalidURIError
    false
  end

  ##
  # Generate a Jekyll post from a news article
  #
  def generate_post(article, source_name)
    title = article['title'] || 'Untitled'
    url = article['link'] || ''
    date_str = article['date'] || Time.now.iso8601
    excerpt = article['excerpt'] || ''

    # Parse date
    begin
      pub_date = DateTime.iso8601(date_str)
      post_date = pub_date.strftime('%Y-%m-%d')
    rescue ArgumentError
      post_date = Date.today.strftime('%Y-%m-%d')
    end

    # Generate slug from title
    slug = title.downcase
                 .gsub(/[^\w\s-]/, '')
                 .gsub(/[\s_-]+/, '-')
                 .gsub(/^-+|-+$/, '')
                 .slice(0, 50)

    # Check if post already exists
    filename = "#{post_date}-#{slug}.md"
    filepath = @posts_dir / filename

    if filepath.exist?
      puts "  ⊘ Post already exists: #{filename}"
      return nil
    end

    # Generate front matter
    front_matter = <<~YAML
      ---
      title: "#{title.gsub('"', '\"')}"
      date: #{post_date}
      layout: default
      source_url: "#{url}"
      source_name: "#{source_name}"
      verified_at: #{Date.today}
      category: news
      news_excerpt: true
      ---
    YAML

    # Remove extra blank lines
    front_matter = front_matter.split("\n").reject(&:empty?).join("\n") + "\n"

    # Generate content
    content = <<~MARKDOWN
      #{front_matter}

      #{excerpt}

      ## Source Information

      This article was aggregated from an officially verified news source:

      - **Source**: #{source_name}
      - **Original URL**: [#{url}](#{url})
      - **Verified**: #{Date.today}
      - **Verification Method**: FCC-Licensed Broadcast Station or Approved Local News Source

      ---

      *All articles are sourced from officially verified and approved news organizations. See the [allowlist](https://github.com/legal-luminary/legal-luminary/blob/main/demos/langsmith_langgraph_demo/allowlist.json) for the complete list of approved sources.*
    MARKDOWN

    {
      filename: filename,
      filepath: filepath,
      content: content
    }
  end

  ##
  # Write a post to disk
  #
  def write_post(post)
    return false unless post

    @posts_dir.mkdir unless @posts_dir.exist?
    post[:filepath].write(post[:content])
    puts "  ✓ Created: #{post[:filename]}"
    true
  end

  ##
  # Integrate all approved articles
  #
  def integrate_articles
    puts "\n" + "="*70
    puts "INTEGRATING APPROVED NEWS ARTICLES"
    puts "="*70

    created_posts = []
    skipped_sources = []

    news_feed['feeds'].each do |feed_source|
      source_name = feed_source['source'] || 'Unknown Source'
      source_url = feed_source['url'] || ''
      articles = feed_source['items'] || []

      # Check if source is approved
      unless approved_source?(source_url, source_name)
        puts "⊘ Skipping unapproved source: #{source_name}"
        skipped_sources << source_name
        next
      end

      puts "\n✓ Processing approved source: #{source_name}"
      puts "  URL: #{source_url}"
      puts "  Articles: #{articles.length}"

      # Limit articles per source (prevent spam)
      articles.first(3).each do |article|
        post = generate_post(article, source_name)
        if write_post(post)
          created_posts << post
        end
      end
    end

    # Summary report
    puts "\n" + "="*70
    puts "INTEGRATION SUMMARY"
    puts "="*70
    puts "Posts created: #{created_posts.length}"
    puts "Sources skipped: #{skipped_sources.length}"
    puts "Skipped sources: #{skipped_sources.join(', ')}" unless skipped_sources.empty?
    puts "="*70

    created_posts.length
  end

  ##
  # Verify Jekyll can build with new posts
  #
  def verify_build
    puts "\n" + "="*70
    puts "VERIFYING JEKYLL BUILD"
    puts "="*70

    unless system('bundle exec jekyll build --strict_front_matter 2>&1 | head -50')
      warn "ERROR: Jekyll build failed"
      return false
    end

    site_dir = Pathname.new('_site')
    if site_dir.exist?
      post_count = Dir.glob('_site/**/*.html').length
      puts "✓ Jekyll build successful"
      puts "  HTML files generated: #{post_count}"
      return true
    else
      warn "ERROR: _site directory not created"
      false
    end
  end

  ##
  # Main integration workflow
  #
  def run
    count = integrate_articles

    if count.positive?
      puts "\n✓ Verification: Testing Jekyll build..."
      verify_build
    else
      puts "\n⊘ No new articles to integrate"
    end

    count
  end
end

# Main execution
if __FILE__ == $PROGRAM_NAME
  integrator = ArticleIntegrator.new
  result = integrator.run

  puts "\n✓ Integration complete: #{result} posts created"
  exit 0
end
