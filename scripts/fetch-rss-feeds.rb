#!/usr/bin/env ruby
# frozen_string_literal: true

# RSS Feed Fetcher for Legal News
# Fetches RSS feeds from configured sources and generates JSON for Jekyll

require 'yaml'
require 'json'
require 'feedjira'
require 'net/http'
require 'uri'
require 'time'
require 'logger'

# Set up logging
logger = Logger.new(STDERR)
logger.level = Logger::INFO

# Configuration
DATA_DIR = File.join(__dir__, '..', '_data')
FEEDS_CONFIG = File.join(DATA_DIR, 'rss-feeds.yml')
OUTPUT_FILE = File.join(DATA_DIR, 'news-feed.json')

# Load configuration
def load_config
  log = Logger.new(STDERR)
  log.level = Logger::INFO
  
  unless File.exist?(FEEDS_CONFIG)
    log.error "Configuration file not found: #{FEEDS_CONFIG}"
    exit 1
  end
  
  config = YAML.load_file(FEEDS_CONFIG)
  log.info "Loaded configuration with #{config['feeds'].size} feeds"
  config
end

# Fetch RSS feed with error handling
def fetch_feed(url, timeout: 10, retries: 2)
  log = Logger.new(STDERR)
  log.level = Logger::INFO
  
  retries.times do |attempt|
    begin
      log.info "Fetching feed: #{url} (attempt #{attempt + 1}/#{retries})"

      uri = URI(url)
      http = Net::HTTP.new(uri.host, uri.port)
      http.use_ssl = (uri.scheme == 'https')
      http.open_timeout = timeout
      http.read_timeout = timeout
      req = Net::HTTP::Get.new(uri)
      req['User-Agent'] = 'Legal Luminary RSS Fetcher/1.0'
      response = http.request(req)

      unless response.is_a?(Net::HTTPSuccess)
        log.warn "HTTP error #{response.code} for #{url}"
        next
      end

      feed = Feedjira.parse(response.body)
      log.info "Successfully parsed feed: #{feed.title || 'Untitled'}"
      return feed

    rescue Net::OpenTimeout, Net::ReadTimeout => e
      log.warn "Timeout fetching #{url}: #{e.message}"
      next if attempt < retries - 1

    rescue SocketError, SystemCallError => e
      log.warn "Network error fetching #{url}: #{e.message}"
      next if attempt < retries - 1
      
    rescue Feedjira::NoParserAvailable => e
      log.error "No parser available for #{url}: #{e.message}"
      return nil
      
    rescue StandardError => e
      log.error "Error parsing feed #{url}: #{e.message}"
      log.error e.backtrace.first(3).join("\n")
      return nil
    end
  end
  
  nil
end

# Convert feed item to hash
def item_to_hash(item, source_name)
  {
    'title' => item.title || 'No title',
    'link' => item.url || item.link || '#',
    'date' => parse_date(item.published || item.updated),
    'excerpt' => extract_excerpt(item.summary || item.content || ''),
    'source' => source_name
  }
rescue StandardError => e
  log = Logger.new(STDERR)
  log.warn "Error converting item: #{e.message}"
  {
    'title' => 'Error parsing item',
    'link' => '#',
    'date' => Time.now.iso8601,
    'excerpt' => '',
    'source' => source_name
  }
end

# Parse date from various formats
def parse_date(date_string)
  return Time.now.iso8601 if date_string.nil? || date_string.empty?
  
  Time.parse(date_string.to_s).iso8601
rescue StandardError
  Time.now.iso8601
end

# Extract excerpt from content
def extract_excerpt(content, max_length: 200)
  return '' if content.nil? || content.empty?
  
  # Remove HTML tags
  text = content.gsub(/<[^>]+>/, ' ').gsub(/\s+/, ' ').strip
  
  if text.length > max_length
    text[0, max_length] + '...'
  else
    text
  end
end

# Filter items by date
def filter_by_date(items, max_age_days: 30)
  cutoff_date = Time.now - (max_age_days * 24 * 60 * 60)
  
  items.select do |item|
    begin
      item_date = Time.parse(item['date'])
      item_date >= cutoff_date
    rescue StandardError
      false
    end
  end
end

# Main execution
def main
  log = Logger.new(STDERR)
  log.level = Logger::INFO
  log.info "Starting RSS feed fetch at #{Time.now}"
  
  config = load_config
  feeds_config = config['feeds'] || []
  global_config = config['config'] || {}
  
  max_age_days = global_config['max_age_days'] || 30
  timeout = global_config['timeout_seconds'] || 10
  retries = global_config['retry_attempts'] || 2
  delay = global_config['delay_between_feeds'] || 1
  
  all_items = []
  feed_results = []
  
  feeds_config.each do |feed_config|
    next unless feed_config['enabled']
    
    source_name = feed_config['name']
    url = feed_config['url']
    max_items = feed_config['max_items'] || 10
    
    log.info "Processing feed: #{source_name}"
    
    feed = fetch_feed(url, timeout: timeout, retries: retries)
    
    if feed.nil?
      log.warn "Failed to fetch feed: #{source_name}"
      feed_results << {
        'source' => source_name,
        'url' => url,
        'items' => [],
        'error' => 'Failed to fetch or parse feed'
      }
      sleep delay
      next
    end
    
    # Convert feed items
    items = feed.entries.map { |entry| item_to_hash(entry, source_name) }
    
    # Filter by date
    items = filter_by_date(items, max_age_days: max_age_days)
    
    # Limit items
    items = items.first(max_items)
    
    # Add to results
    feed_results << {
      'source' => source_name,
      'url' => url,
      'items' => items,
      'item_count' => items.size
    }
    
    # Add to all items
    all_items.concat(items)
    
    log.info "Fetched #{items.size} items from #{source_name}"
    
    # Delay between feeds to be respectful
    sleep delay
  end
  
  # Sort all items by date (newest first)
  all_items.sort_by! { |item| Time.parse(item['date']) }.reverse!
  
  # Generate output
  output = {
    'last_updated' => Time.now.iso8601,
    'feeds' => feed_results,
    'all_items' => all_items,
    'total_items' => all_items.size
  }
  
  # Write JSON file
  File.write(OUTPUT_FILE, JSON.pretty_generate(output))
  log.info "Wrote #{all_items.size} total items to #{OUTPUT_FILE}"
  
  # Summary
  successful_feeds = feed_results.count { |f| f['items'].any? }
  log.info "Summary: #{successful_feeds}/#{feed_results.size} feeds successful, #{all_items.size} total items"
  
  exit 0
rescue StandardError => e
  log.error "Fatal error: #{e.message}"
  log.error e.backtrace.join("\n")
  exit 1
end

# Run if executed directly
main if __FILE__ == $PROGRAM_NAME
