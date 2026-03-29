---
layout: default
title: "Candidates - Elected Officials & Races"
permalink: /candidates/
description: "Browse candidates for Federal, State, County, Municipal, and Education offices in Central Texas"
body_class: page-candidates
---

<link rel="stylesheet" href="{{ '/assets/css/candidates-new.css' | relative_url }}">

<section class="candidates-hub candidates-section" aria-label="Candidates and elected offices">
  <a href="#candidates-content" class="skip-link">Skip to candidates</a>
  <h1>Candidates & Elected Officials</h1>
  <p class="section-intro">Bell County and Central Texas races. <strong>Sample data</strong> rows are placeholders. <a href="{{ '/candidates/FINANCIALS/' | relative_url }}">FEC finance report</a></p>

  <div class="candidates-tab-stack">
    <div class="tab-nav-sentinel"></div>
    {% include candidates/tab-navigation.html %}

    <div id="candidates-content"></div>

    <div class="tab-content active" id="tab-federal" role="tabpanel" aria-labelledby="tab-btn-federal">
      {% include candidates/tabs/federal.html %}
    </div>

    <div class="tab-content" id="tab-state" role="tabpanel" aria-labelledby="tab-btn-state">
      {% include candidates/tabs/state.html %}
    </div>

    <div class="tab-content" id="tab-county" role="tabpanel" aria-labelledby="tab-btn-county">
      {% include candidates/tabs/county.html %}
    </div>

    <div class="tab-content" id="tab-municipal" role="tabpanel" aria-labelledby="tab-btn-municipal">
      {% include candidates/tabs/municipal.html %}
    </div>

    <div class="tab-content" id="tab-education" role="tabpanel" aria-labelledby="tab-btn-education">
      {% include candidates/tabs/education.html %}
    </div>
  </div>
</section>

{% include candidates/candidates-tabs-script.html %}
