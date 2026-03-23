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
  <p class="section-intro">Research candidates running for office in Bell County and Central Texas. Data sourced from FEC filings, campaign disclosures, and Ballotpedia. Rows marked <strong>Sample data</strong> are placeholders for layout until verified. <a href="{{ '/candidates/FINANCIALS/' | relative_url }}">View FEC Finance Report</a></p>

  <div class="tab-nav-sentinel"></div>
  {% include candidates/tab-navigation.html %}

  <div id="candidates-content"></div>
  <div class="tab-content active" id="tab-federal" role="tabpanel" aria-labelledby="tab-btn-federal">
    <div class="tab-banner tab-banner--us-flag" aria-hidden="true"></div>
    <h2>Federal offices</h2>

    <div class="general-election-banner">
      <span class="general-election-banner__badge">November 3, 2026</span>
      <strong>General election:</strong> Confirm matchups with the Secretary of State and FEC.
    </div>

    <h3 class="candidates-subsection-title">U.S. Senate</h3>
    {% include candidates/race-card.html race="US Senate TX - Cornyn" %}
    {% include candidates/race-card.html race="US Senate TX - Cruz" %}

    <h3 class="candidates-subsection-title">U.S. House of Representatives</h3>
    {% include candidates/race-card.html race="US House TX-31" election_label="General November 3, 2026" %}

    <section class="candidates-prose-block candidates-prose-block--compact" id="tx-31-primary-context" aria-labelledby="tx-31-primary-heading">
      <h3 id="tx-31-primary-heading" class="candidates-prose-block__title">TX-31: after the March 2026 primaries</h3>
      <p class="candidates-prose-block__sources"><strong>Sources:</strong> <a href="https://www.nbcnews.com/politics/2026-primary-elections/texas-us-house-district-31-results">NBC News 2026 TX-31 results</a>, <a href="https://www.kten.com/john-carter-wins-republican-nomination-for-u-s-house-in-texas-31st-congressional-district/article_a01067b4-85ce-5780-a780-dae34b99a1fe.html">KTEN (Carter, GOP)</a>, <a href="https://www.sos.texas.gov/">Texas Secretary of State</a> (official certification).</p>
      <p>The March 2026 primaries narrowed each party to one nominee for U.S. House District 31. <strong>Republican:</strong> Incumbent <strong>John Carter</strong> won the GOP nomination with a majority in a large field (reported near 60%). <strong>Democratic:</strong> <strong>Justin Early</strong> won the nomination over Stuart Whitlow (reported ~57.6% / ~42.4%). The <strong>November 3, 2026</strong> general is between those two nominees. This page lists only that incumbent and challenger; primary also-rans were removed from the data.</p>
    </section>
  </div>

  <div class="tab-content" id="tab-state" role="tabpanel" aria-labelledby="tab-btn-state">
    <div class="tab-banner tab-banner--tx-flag" aria-hidden="true"></div>
    <h2>State offices</h2>

    <h3 class="candidates-subsection-title">Statewide Executive</h3>
    {% include candidates/race-card.html race="TX Governor" %}
    {% include candidates/race-card.html race="TX Attorney General" election_label="Primary runoff May 26, 2026 · General Nov 3, 2026" %}
    {% include candidates/race-card.html race="TX Comptroller" %}

    <h3 class="candidates-subsection-title">Texas Senate</h3>
    {% include candidates/race-card.html race="State Senate TX-24" %}

    <h3 class="candidates-subsection-title">Texas House of Representatives</h3>
    {% include candidates/race-card.html race="State House TX-54" %}

    <section class="candidates-prose-block" id="comptroller-primary-context" aria-labelledby="comptroller-primary-heading">
      <h3 id="comptroller-primary-heading" class="candidates-prose-block__title">Comptroller primary (what deep-search would have synthesized)</h3>
      <p class="candidates-prose-block__sources"><strong>Sources:</strong> <a href="https://en.wikipedia.org/wiki/2026_Texas_Comptroller_of_Public_Accounts_election">2026 Texas Comptroller election (Wikipedia)</a>, <a href="https://www.texastribune.org/2026/03/03/don-huffines-christi-craddick-kelly-hancock-texas-gop-primary-comptroller/">Texas Tribune — Huffines wins GOP primary</a>, <a href="https://www.statesman.com/politics/election/2026/article/comptroller-primary-results-21329222.php">Austin American-Statesman / general matchup</a>.</p>

      <h4 class="candidates-prose-block__h">Office (why it mattered in 2026)</h4>
      <p>The Comptroller of Public Accounts is Texas’s chief financial officer: tax collection, revenue estimating (drives the Legislature’s budget process), disbursements, and oversight of large state spending. Texas Tribune notes the comptroller helps oversee execution of a very large biennial budget.</p>

      <h4 class="candidates-prose-block__h">Why the seat was open</h4>
      <p>Glenn Hegar was elected comptroller in 2014 and reelected (including 2022). He resigned effective July 1, 2025 to become chancellor of the Texas A&amp;M University System (Wikipedia, Tribune).</p>
      <p>Kelly Hancock (former state senator) became acting comptroller after being positioned as chief clerk and taking office in July 2025; the appointment followed a path around limits on appointing sitting legislators (Wikipedia, Tribune).</p>

      <h4 class="candidates-prose-block__h">Republican primary — candidates and result</h4>
      <p><strong>Candidates:</strong> Don Huffines, Kelly Hancock (acting), Christi Craddick (Railroad Commissioner), Michael Berlanga.</p>
      <p>March 2026 primary vote totals (Wikipedia):</p>
      <div class="candidates-prose-block__table-wrap">
        <table class="candidates-prose-block__table">
          <thead>
            <tr><th scope="col">Candidate</th><th scope="col">Votes</th><th scope="col">%</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">Don Huffines</th><td>1,191,830</td><td>57.4</td></tr>
            <tr><th scope="row">Kelly Hancock</th><td>491,358</td><td>23.7</td></tr>
            <tr><th scope="row">Christi Craddick</th><td>312,626</td><td>15.1</td></tr>
            <tr><th scope="row">Michael Berlanga</th><td>80,985</td><td>3.9</td></tr>
          </tbody>
        </table>
      </div>
      <p><strong>No runoff</strong> — Huffines won outright.</p>

      <h4 class="candidates-prose-block__h">Themes / money / endorsements (high level)</h4>
      <ul class="candidates-prose-block__list">
        <li><strong>Texas Tribune:</strong> Huffines cast himself as “DOGE-ing” state government, self-funded heavily, late Trump endorsement, plus Cruz and other MAGA-aligned figures; Abbott spent heavily for Hancock in the final stretch (~two-thirds of Hancock’s late spend from Abbott’s war chest in one cited report). Total spend among the top three was on the order of $16M vs. much less for Hegar’s 2022 primary at the same point.</li>
        <li>Hancock pitched implementation of school vouchers, ICE collaboration grants, and DEI-related contracting changes; Craddick also emphasized audits/waste and culture-war touchpoints. Tribune also notes legislature has narrowed some comptroller audit authority over time.</li>
      </ul>

      <h4 class="candidates-prose-block__h">Democratic primary</h4>
      <p><strong>Candidates:</strong> Sarah Eckhardt (state senator, SD-14), Savant Moore, Michael Lange.</p>
      <p>Results (Wikipedia):</p>
      <div class="candidates-prose-block__table-wrap">
        <table class="candidates-prose-block__table">
          <thead>
            <tr><th scope="col">Candidate</th><th scope="col">Votes</th><th scope="col">%</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">Sarah Eckhardt</th><td>1,317,024</td><td>64.1</td></tr>
            <tr><th scope="row">Savant Moore</th><td>392,043</td><td>19.1</td></tr>
            <tr><th scope="row">Michael Lange</th><td>346,484</td><td>16.9</td></tr>
          </tbody>
        </table>
      </div>
      <p>Eckhardt switched from a congressional path to comptroller near the filing deadline (Wikipedia).</p>

      <h4 class="candidates-prose-block__h">General election (November 3, 2026)</h4>
      <p>Don Huffines (R) vs. Sarah Eckhardt (D). Texas has not elected a Democratic comptroller since the 1990s (Tribune).</p>

      <h4 class="candidates-prose-block__h">Libertarian line</h4>
      <p>Wikipedia lists Alonzo Echavarria-Garza as a declared Libertarian convention candidate.</p>
    </section>
  </div>

  <div class="tab-content" id="tab-county" role="tabpanel" aria-labelledby="tab-btn-county">
    <h2>County offices</h2>
    {% include candidates/race-card.html race="Bell County DA" %}
    {% include candidates/race-card.html race="Bell County Commissioner P4" %}
    {% include candidates/race-card.html race="Bell JP P4 Place 2" %}
  </div>

  <div class="tab-content" id="tab-municipal" role="tabpanel" aria-labelledby="tab-btn-municipal">
    <h2>Municipal offices</h2>
    {% include candidates/municipal-by-city.html %}
  </div>

  <div class="tab-content" id="tab-education" role="tabpanel" aria-labelledby="tab-btn-education">
    <h2>Education</h2>
    {% include candidates/race-card.html race="SBOE TX-10" %}
    {% include candidates/race-card.html race="CTC Trustee Place 1" %}
    {% include candidates/race-card.html race="CTC Trustee Place 2" %}
    {% include candidates/race-card.html race="CTC Trustee Place 3" %}
    {% include candidates/race-card.html race="CTC Trustee Place 4" %}
  </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const tabs = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const targetId = this.dataset.tab;

      tabs.forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
        t.setAttribute('tabindex', '-1');
      });

      contents.forEach(c => c.classList.remove('active'));

      this.classList.add('active');
      this.setAttribute('aria-selected', 'true');
      this.setAttribute('tabindex', '0');

      const targetContent = document.getElementById('tab-' + targetId);
      if (targetContent) {
        targetContent.classList.add('active');
        targetContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });

    tab.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        const currentIndex = Array.from(tabs).indexOf(this);
        let newIndex;
        if (e.key === 'ArrowRight') {
          newIndex = currentIndex === tabs.length - 1 ? 0 : currentIndex + 1;
        } else {
          newIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1;
        }
        tabs[newIndex].focus();
        tabs[newIndex].click();
      }
    });
  });

  const hash = window.location.hash.replace('#', '');
  if (hash && document.getElementById('tab-' + hash)) {
    const btn = document.querySelector('[data-tab="' + hash + '"]');
    if (btn) btn.click();
  }

  var sentinel = document.querySelector('.tab-nav-sentinel');
  var tabNav = document.querySelector('.tab-nav');
  if (sentinel && tabNav && window.IntersectionObserver) {
    var obs = new IntersectionObserver(function(entries) {
      tabNav.classList.toggle('tab-nav--stuck', !entries[0].isIntersecting);
    }, { threshold: 0 });
    obs.observe(sentinel);
  }
});
</script>
