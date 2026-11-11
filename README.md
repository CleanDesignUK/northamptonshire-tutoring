# Northamptonshire Tutoring

Complete, static Bootstrap website for **northamptonshiretutoring.com**, part of North Wales Tutoring Group.

**Purpose:** Generate real tutoring enquiries from families in North and West Northamptonshire through clear service pages, practical content, local town pages and a simple Web3Forms enquiry flow.

## Publish / preview

The site is already built. Upload the contents of this directory to the root of your hosting / GitHub Pages repository. The `CNAME` file is configured for `northamptonshiretutoring.com`; connect the domain in your host and configure DNS and HTTPS. The site does not require a runtime backend.

Local preview (from the project directory):

```bash
python3 -m http.server 8000
# Open http://localhost:8000/
```

## Directory structure

```text
index.html                             Home + lead form
about.html                             About page
contact.html                           Contact form
areas.html                             Northamptonshire areas index
blog.html                              Blog homepage
blog/*.html                            3 standalone SEO article pages
locations/*.html                       8 individual town pages
*-tutoring-northamptonshire.html       6 service landing pages
privacy.html, cookie-policy.html       Privacy pages
assets/css/global.css                  Shared brand, navbar, footer, cookie, buttons
assets/css/pages.css                   Home, services, local, blog and contact styles
assets/js/main.js                      Navigation state, auto-year, cookie choices
assets/js/forms.js                     Web3Forms AJAX, validation and status handling
assets/vendor/bootstrap/              Locally bundled Bootstrap 5.3.6 CSS + JS
assets/images/                         NWT-provided logos, tutoring and tutor assets
components/navbar.html                 Shared nav component source
components/footer.html                 Shared footer component source
components/cookie-banner.html          Shared cookie component source
data/site.json                         Brand, contact, prices, exam boards, Web3Forms key
data/locations.json                    Local landing page details
data/subjects.json                   Service page content
data/blog.json                       Blog listing metadata
source/blog/*.html                     Editable article text
scripts/build.py                       Rebuild static HTML (Python 3, no packages)
scripts/check_site.py                  Validate internal links / essentials
robots.txt, sitemap.xml                Crawl discovery
CNAME, .nojekyll                       GitHub Pages compatibility
```

**Shared components are compiled at build time**, not fetched at runtime. This keeps the actual HTML pages complete for crawlers, accessibility and no-JavaScript navigation. To change the navbar, footer, banner, or site-wide contact details, edit their component or data source and then run:

```bash
python3 scripts/build.py
python3 scripts/check_site.py
```

Do **not** edit the generated header/footer in all HTML pages individually. They will be overwritten on the next build.

## Web3Forms

- Access key installed from the request: `7cfb8b83-2221-4866-8be3-087c5dfedd46`.
- Required enquiry fields: name, email, phone and message. Optional level and subject fields help qualification.
- Hidden `botcheck` honeypot (not a visible checkbox), bot speed check, client-side phone validation, duplicate-attempt cooldown and provider-side spam filtering.
- The form uses JSON AJAX so visitors stay on the same page. A successful submission shows a SweetAlert2 confirmation. If JavaScript is disabled, it does not submit or redirect; users can use WhatsApp/email instead.
- **Before launch:** verify the Web3Forms key is active, points to the intended inbox and accepts submissions from your domain. Send *one real test enquiry* from the live domain. No live enquiries were sent during development.
- **For stronger protection:** enable Web3Forms-supported invisible captcha / Turnstile on an eligible account, if desired. This needs separate setup and cannot be secured with a public static key alone. The hidden honeypot is basic spam prevention, not an unbreakable bot defence.

## SEO / AEO / geographic targeting

- One unique title, description, canonical and H1 per page.
- Organization, WebSite, Service, FAQPage, BreadcrumbList and BlogPosting JSON-LD where appropriate.
- Search-relevant, fact-based text on local tutoring, exam boards, year groups, subjects and prices.
- Individual pages for Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and Brackley, plus coverage of surrounding towns.
- No fabricated local business address, physical offices, school partnerships, reviews, grades or tutor availability.
- Sitemap and robots.txt included; submit sitemap in Google Search Console / Bing Webmaster Tools after launch.
- The articles in `source/blog` are separate editable files; use `data/blog.json` and the build script when adding posts.

## Consent / tracking

The supplied site deliberately ships **without GA4 or Meta Pixel**. The cookie banner stores the person's choice; non-essential tracking must only be added behind an actual consent check. Update `cookie-policy.html` and the build source if additional services are installed.

## Brand and usage

The site uses NWT's existing navy `#09096A`, pink `#FF28A8`, real tutor photos and parent-group artwork from the supplied project sources. The Northamptonshire layout, hero, service architecture and conversion blocks are distinct from the parent site.

Bootstrap code is distributed under the MIT License. Other artwork and tutor photos are reused from the user-provided NWT files, assuming you retain the rights to use them across group brands.

## Launch checklist

1. Upload the project to the website's document root.
2. Configure DNS, HTTPS and the `CNAME` mapping.
3. Open the homepage and test navigation on desktop and a real phone.
4. Submit one real enquiry to verify the Web3Forms key, delivery inbox and any domain restrictions.
5. Check links, current tutor availability and whether the pricing still applies.
6. Verify the privacy notice and consent wording against the final hosting/tracking setup.
7. Submit `https://northamptonshiretutoring.com/sitemap.xml` to your search-engine webmaster tools.
8. If enabled later, connect GA4 / Meta Pixel with appropriate consent controls and analytics conversion tracking.
