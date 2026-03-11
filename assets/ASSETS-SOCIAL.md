# Social & SEO image assets

Images in this folder are used in `<meta>` tags and `<link>` tags in `_layouts/default.html` for social sharing and SEO.

## Platform requirements (summary)

| Use | Recommended size | Asset used |
|-----|------------------|------------|
| **Open Graph** (Facebook, LinkedIn, etc.) | 1200×630 px (1.91:1) | `legal-luminary-of-central-texas-hero-banner.png` |
| **Twitter/X card** | 1200×675 or 1200×630 | Same as OG (hero-banner) |
| **Favicon (PNG fallback)** | 32×32 or multi-size | `legal-luminary-of-central-texas-favicon-(seo).png` |
| **Apple touch icon** | 180×180 (1:1) | `legal-luminary-of-central-texas-square.png` |
| **Organization logo (JSON-LD)** | Square preferred | `legal-luminary-of-central-texas-square.png` |

## Naming conventions

- **Profile** — `*-facebook-profile.png`, `*-instagram-profile.png`, `*-linkedin-profile.png`, `*-x-(twitter)-profile.png`: platform-specific variants (often square); used when you want platform-specific images; default layout uses one shared OG image.
- **Hero / header** — `*-hero-banner.png`, `*-website-header-(h).png`, `*-website-header-(v).png`: horizontal/vertical; hero-banner is the default for link previews.
- **Favicon / SEO** — `*-favicon-(seo).png`: small icon for browser tab and SEO.
- **Square** — `*-square.png`: 1:1, for profile and apple-touch-icon.

## Best practices applied

- **Absolute URLs** for `og:image` and `twitter:image` (via Jekyll `absolute_url`).
- **Dimensions** set via `og:image:width` and `og:image:height` (1200×630) for faster layout and crawling.
- **Alt text** via `og:image:alt` and `twitter:image:alt` for accessibility and SEO.
- **Twitter card type** `summary_large_image` for large previews.
- **PNG** used for meta images; favicon has SVG primary and PNG fallback.

## Layout usage

- Default page and most pages: `default_social_image` = hero-banner; posts can override with `page.image`.
- Favicon: SVG (primary) + PNG fallback; apple-touch-icon uses square asset.
