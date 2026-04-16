// Central Texas Legal Resource - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Ensure non-critical images lazy load for better performance
  document.querySelectorAll('img:not([loading])').forEach(img => {
    if (!img.closest('.logo')) {
      img.setAttribute('loading', 'lazy');
    }
  });

  // Mobile navigation toggle
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.getElementById('primary-menu') || document.querySelector('.nav-menu');

  if (navToggle && navMenu) {
    navToggle.setAttribute('aria-expanded', 'false');

    navToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      const expanded = navMenu.classList.contains('active');
      navToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
        navMenu.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.focus();
      }
    });
  }

  // Submenu toggle for mobile devices
  const navItemsWithChildren = document.querySelectorAll('.nav-item-has-children > a');
  navItemsWithChildren.forEach(function(item) {
    item.addEventListener('click', function(e) {
      // Only prevent default and toggle on mobile (when menu is in vertical mode)
      if (window.innerWidth <= 768) {
        const parent = this.parentElement;
        const submenu = parent.querySelector('.nav-submenu');

        if (submenu) {
          e.preventDefault();
          parent.classList.toggle('active');

          // Close other open submenus
          document.querySelectorAll('.nav-item-has-children').forEach(function(otherItem) {
            if (otherItem !== parent && otherItem.classList.contains('active')) {
              otherItem.classList.remove('active');
            }
          });
        }
      }
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      if (this.classList.contains('skip-link')) {
        return;
      }
      const href = this.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // Add external link indicators and security attributes
  document.querySelectorAll('a[target="_blank"]').forEach(link => {
    if (!link.querySelector('.external-icon')) {
      // Preserve existing rel values (like 'sponsored') and add security attributes
      const currentRel = link.getAttribute('rel') || '';
      const relTokens = currentRel.split(/\s+/).filter(token => token.length > 0);
      const requiredTokens = ['noopener', 'noreferrer'];

      // Add required tokens if not already present
      requiredTokens.forEach(token => {
        if (!relTokens.includes(token)) {
          relTokens.push(token);
        }
      });

      // Set the updated rel attribute, preserving any existing values like 'sponsored'
      link.setAttribute('rel', relTokens.join(' '));
    }
  });

  // Track phone number clicks (for analytics integration)
  document.querySelectorAll('a[href^="tel:"]').forEach(phone => {
    phone.addEventListener('click', function() {
      if (typeof gtag !== 'undefined') {
        gtag('event', 'click', {
          'event_category': 'Contact',
          'event_label': 'Phone Call',
          'value': this.href
        });
      }
    });
  });

  // Track email clicks
  document.querySelectorAll('a[href^="mailto:"]').forEach(email => {
    email.addEventListener('click', function() {
      if (typeof gtag !== 'undefined') {
        gtag('event', 'click', {
          'event_category': 'Contact',
          'event_label': 'Email',
          'value': this.href
        });
      }
    });
  });
});
