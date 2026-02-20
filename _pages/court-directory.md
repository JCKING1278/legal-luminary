---
layout: default
title: Court Directory
permalink: /court-directory/
hero: true
hero_title: "Bell County Court Directory"
hero_subtitle: "Phone numbers, addresses, judges, and officials for every court in Bell County"
description: "Complete Bell County court directory. District Courts, County Courts at Law, Justice of the Peace, Municipal Courts, and county officials with phone numbers and addresses."
verified_at: 2026-02-19
source_url: "https://www.bellcountytx.com/"
---

{% assign dir = site.data.bell_county_directory %}

<p class="intro-text">
This directory provides contact information for every court and key government office in Bell County, Texas. Information is verified against official county sources. If you are an attorney, defendant, plaintiff, or citizen needing to reach a court or official, use the phone numbers and addresses below.
</p>

<div class="info-box">
<h4>{{ dir.courthouse.name }}</h4>
<p>{{ dir.courthouse.address }}<br>
Main Phone: <a href="tel:+12549335100">{{ dir.courthouse.phone }}</a><br>
<a href="{{ dir.courthouse.website }}" target="_blank" rel="noopener noreferrer">{{ dir.courthouse.website }}</a></p>
</div>

## County Officials

| Office | Name | Phone | Role |
|--------|------|-------|------|
{% for official in dir.county_officials %}{% assign o = official[1] %}| **{{ o.title }}** | {{ o.name }} | [{{ o.phone }}](tel:{{ o.phone | replace: ' ', '' | replace: '(', '' | replace: ')', '' | replace: '-', '' | prepend: '+1' }}) | {{ o.role }} |
{% endfor %}

## District Courts

District Courts handle felony criminal cases, civil cases over $200,000, family law, and juvenile matters. All are located at the Bell County Justice Center, 1201 Huey Drive, Belton, TX 76513.

<div class="cards-grid two-columns">
{% for court in dir.district_courts %}
<div class="card">
<h3>{{ court.name }}</h3>
<p><strong>{{ court.judge }}</strong></p>
<p>Phone: <a href="tel:{{ court.phone | replace: ' ', '' | replace: '(', '' | replace: ')', '' | replace: '-', '' | prepend: '+1' }}">{{ court.phone }}</a></p>
<p class="card-meta">{{ court.location }}</p>
</div>
{% endfor %}
</div>

## County Courts at Law

County Courts at Law handle Class A and B misdemeanors, civil cases between $500 and $200,000, probate matters, and appeals from Justice of the Peace courts. All are located at the Bell County Justice Center.

<div class="cards-grid">
{% for court in dir.county_courts_at_law %}
<div class="card">
<h3>{{ court.name }}</h3>
<p><strong>{{ court.judge }}</strong></p>
<p>Phone: <a href="tel:{{ court.phone | replace: ' ', '' | replace: '(', '' | replace: ')', '' | replace: '-', '' | prepend: '+1' }}">{{ court.phone }}</a></p>
</div>
{% endfor %}
</div>

## Justice of the Peace Courts

Justice of the Peace courts handle Class C misdemeanors (fine-only offenses), small claims civil cases up to $20,000, evictions, and truancy cases.

<div class="cards-grid two-columns">
{% for jp in dir.justice_of_the_peace %}
<div class="card">
<h3>{{ jp.name }}</h3>
<p><strong>{{ jp.judge }}</strong></p>
<p>Phone: <a href="tel:{{ jp.phone | replace: ' ', '' | replace: '(', '' | replace: ')', '' | replace: '-', '' | prepend: '+1' }}">{{ jp.phone }}</a></p>
{% if jp.email %}<p>Email: <a href="mailto:{{ jp.email }}">{{ jp.email }}</a></p>{% endif %}
<p class="card-meta">{{ jp.location }}</p>
</div>
{% endfor %}
</div>

## Municipal Courts

Municipal courts handle city ordinance violations and Class C misdemeanors that occur within city limits.

<div class="cards-grid two-columns">
{% for court in dir.municipal_courts %}
<div class="card">
<h3>{{ court.name }}</h3>
<p>{{ court.address }}</p>
<p>Phone: <a href="tel:{{ court.phone | replace: ' ', '' | replace: '(', '' | replace: ')', '' | replace: '-', '' | prepend: '+1' }}">{{ court.phone }}</a></p>
{% if court.website %}<p><a href="{{ court.website }}" target="_blank" rel="noopener noreferrer">Website</a></p>{% endif %}
</div>
{% endfor %}
</div>

## Online Resources

<div class="info-box">
<h4>{{ dir.key_resources.odyssey_portal.name }}</h4>
<p>{{ dir.key_resources.odyssey_portal.description }}<br>
<a href="{{ dir.key_resources.odyssey_portal.url }}" target="_blank" rel="noopener noreferrer">{{ dir.key_resources.odyssey_portal.url }}</a></p>
</div>

<div class="info-box">
<h4>{{ dir.key_resources.online_payments.name }}</h4>
<p>{{ dir.key_resources.online_payments.description }}<br>
<a href="{{ dir.key_resources.online_payments.url }}" target="_blank" rel="noopener noreferrer">{{ dir.key_resources.online_payments.url }}</a></p>
</div>

## Service Areas

{% for area in dir.service_areas %}
### {{ area.name }} — {{ area.type }}

{{ area.description }}

{% if area.key_facilities.size > 0 %}**Key Facilities:** {{ area.key_facilities | join: ", " }}{% endif %}

{% endfor %}

<div class="legal-notice">
<strong>Note:</strong> Court contact information is verified against official Bell County sources. Phone numbers and personnel may change. For the most current information, visit <a href="https://www.bellcountytx.com" target="_blank" rel="noopener noreferrer">bellcountytx.com</a> or call the main courthouse line at (254) 933-5100.
</div>
