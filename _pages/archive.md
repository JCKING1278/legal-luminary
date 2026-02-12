---
permalink: /archive/
layout: page
title: Blog archive
verified_at: 2026-02-11
---


{% assign now_ts = 'now' | date: '%s' | plus: 0 %}
{% assign cutoff_ts = now_ts | minus: 31536000 %}

<ul>
  {% for post in site.posts %}
    {% assign post_ts = post.date | date: '%s' | plus: 0 %}
    {% if post_ts >= cutoff_ts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>({{ post.date | date: "%b %-d, %Y" }})</small>
    </li>
    {% endif %}
  {% endfor %}
</ul>
