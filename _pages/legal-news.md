---
layout: default
title: Legal News
permalink: /legal-news/
sidebar_ads: general
description: Latest legal news from Bell County Texas and Texas state government sources
source_type: news
sources:
  - url: "https://www.bellcountytx.com/"
    label: "Bell County, Texas (official site)"
  - url: "https://capitol.texas.gov/"
    label: "Texas Legislature Online"
  - url: "https://www.texasattorneygeneral.gov/"
    label: "Texas Attorney General (press releases)"
verified_at: 2026-02-11
---

# Legal News

Stay informed with the latest legal news, government updates, and legislative developments from Bell County Texas and Texas state sources.

{%- assign news_data = site.data.news-feed -%}

{%- if news_data and news_data.feeds -%}
  {%- assign has_items = false -%}
  {%- for feed in news_data.feeds -%}
    {%- if feed.items and feed.items.size > 0 -%}
      {%- assign has_items = true -%}
      {%- break -%}
    {%- endif -%}
  {%- endfor -%}
  
  {%- if has_items -%}
    <div class="news-feed-header">
      <p class="intro-text">
        This page aggregates legal news and government updates from official sources in Bell County and Texas. 
        Content is automatically updated daily from RSS feeds.
      </p>
      
      {%- if news_data.last_updated -%}
        <p class="news-update-info">
          <strong>Last updated:</strong> {{ news_data.last_updated | date: "%B %-d, %Y at %-I:%M %p" }}
        </p>
      {%- endif -%}
    </div>
    
    <div class="news-feed-sources">
      {%- for feed in news_data.feeds -%}
        {%- if feed.items and feed.items.size > 0 -%}
          <section class="news-source-section" aria-labelledby="source-{{ forloop.index }}">
            <h3 id="source-{{ forloop.index }}">{{ feed.source }}</h3>
            
            {%- if feed.url -%}
              <p class="news-source-link">
                <a href="{{ feed.url }}" target="_blank" rel="noopener noreferrer">
                  View source feed →
                </a>
              </p>
            {%- endif -%}
            
            <ul class="news-items-list">
              {%- for item in feed.items -%}
                <li class="news-item">
                  <a href="{{ item.link }}" target="_blank" rel="noopener noreferrer" class="news-item-title">
                    {{ item.title }}
                  </a>
                  <div class="news-item-meta">
                    <span class="news-item-date">{{ item.date | date: "%B %-d, %Y" }}</span>
                  </div>
                  {%- if item.excerpt and item.excerpt != "" -%}
                    <p class="news-item-excerpt">{{ item.excerpt }}</p>
                  {%- endif -%}
                </li>
              {%- endfor -%}
            </ul>
          </section>
        {%- endif -%}
      {%- endfor -%}
    </div>
    
    {%- if news_data.total_items -%}
      <div class="news-feed-summary">
        <p><strong>Total items:</strong> {{ news_data.total_items }} news articles from {{ news_data.feeds.size }} sources</p>
      </div>
    {%- endif -%}
    
  {%- else -%}
    <div class="news-feed-empty">
      <p>No news items available at this time.</p>
      <p>News feeds are updated daily. Please check back later.</p>
    </div>
  {%- endif -%}
  
{%- else -%}
  <div class="news-feed-empty">
    <p>News feed data is not yet available.</p>
    <p>The news feed system is being set up and will be populated automatically once the GitHub Actions workflow runs.</p>
  </div>
{%- endif -%}

## About This Feed

This legal news feed aggregates content from the following sources:

### Local Bell County Sources
- **City of Killeen** - Legal notices, public notices, and city news
- **Killeen Daily Herald** - Local news covering Bell County

### Texas State Sources
- **Texas Legislature Online** - Bills, committee meetings, and legislative updates
- **Texas Attorney General** - Press releases and legal updates (when available)

All content is automatically fetched from official RSS feeds and updated daily. Items are filtered to show only the most recent 30 days of news.
