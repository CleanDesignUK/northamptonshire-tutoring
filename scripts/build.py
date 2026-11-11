#!/usr/bin/env python3
"""Build accessible, SEO-ready standalone HTML from shared components + JSON.

Run: python3 scripts/build.py
This produces deployable HTML, with headers/footer/cookie HTML inlined so
search engines and visitors see navigation even without client-side JS.
"""
from pathlib import Path
from html import escape as E
from datetime import date
import json
import re

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: (ROOT / p).read_text(encoding='utf-8')
load = lambda p: json.loads(read(p))
SITE = load('data/site.json')
LOCATIONS = load('data/locations.json')
SUBJECTS = load('data/subjects.json')
POSTS = load('data/blog.json')
NAV = read('components/navbar.html')
FOOT = read('components/footer.html')
COOKIE = read('components/cookie-banner.html')
DOMAIN = SITE['domain']
TEL = SITE['phone_display']
EMAIL = SITE['email']
WHATSAPP = SITE['whatsapp']
BOARDS = SITE['exam_boards']
AREA_NAMES = [p['name'] for p in LOCATIONS]
LOC_LOOKUP = {p['slug']:p for p in LOCATIONS}
SUB_LOOKUP = {p['slug']:p for p in SUBJECTS}
POST_LOOKUP = {p['slug']:p for p in POSTS}


def breadcrumbs(crumbs):
    out=['<nav class="breadcrumb-custom" aria-label="Breadcrumb"><a href="/">Home</a>']
    for name,url in crumbs:
        if url:out.append(f'<span aria-hidden="true">/</span><a href="{E(url)}">{E(name)}</a>')
        else:out.append(f'<span aria-hidden="true">/</span><span aria-current="page">{E(name)}</span>')
    return ''.join(out)+'</nav>'


def jsonld(data):
    safe=json.dumps(data,ensure_ascii=False,separators=(',', ':')).replace('<','\\u003c')
    return f'<script type="application/ld+json">{safe}</script>'


def organization_schema():
    return {'@context':'https://schema.org','@type':'EducationalOrganization','@id':DOMAIN+'/#organisation',
        'name':SITE['brand'],'url':DOMAIN+'/','logo':DOMAIN+'/assets/images/nwt-group-logo.png',
        'description':'Online one-to-one Maths, Physics, Biology, Chemistry, English, GCSE and A-Level tutoring for pupils throughout Northamptonshire, including Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and Brackley.',
        'slogan':SITE['motto'],'email':EMAIL,'telephone':SITE['phone_international'],
        'parentOrganization':{'@type':'Organization','name':SITE['parent'],'url':SITE['parent_url']},
        'areaServed':[{'@type':'AdministrativeArea','name':'Northamptonshire, England'}]+[{'@type':'City','name':n} for n in AREA_NAMES],
        'sameAs':[SITE['facebook'],SITE['instagram']],
        'knowsAbout':['GCSE Maths tuition','GCSE Physics tuition','A-Level Physics tuition','A-Level Maths tuition','GCSE Chemistry','GCSE Biology','AQA','Pearson Edexcel','OCR','WJEC','Eduqas','Cambridge International','KS3','Primary Maths']}


def site_schema():
    return {'@context':'https://schema.org','@type':'WebSite','@id':DOMAIN+'/#website',
            'name':SITE['brand'],'url':DOMAIN+'/','inLanguage':'en-GB',
            'publisher':{'@id':DOMAIN+'/#organisation'}}


def faq_schema(items):
    return {'@context':'https://schema.org','@type':'FAQPage',
            'mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in items]}


def service_schema(name,desc,service_url,area=None):
    served=area or 'Northamptonshire, England'
    return {'@context':'https://schema.org','@type':'Service','@id':DOMAIN+service_url+'#service',
            'name':name,'serviceType':'Online one-to-one tutoring','description':desc,
            'provider':{'@id':DOMAIN+'/#organisation'},
            'areaServed':{'@type':'Place','name':served},'availableChannel':{'@type':'ServiceChannel','serviceUrl':DOMAIN+'/contact.html'}}


def crumb_schema(parts):
    items=[{'@type':'ListItem','position':1,'name':'Home','item':DOMAIN+'/'}]
    for i,(label,path) in enumerate(parts,start=2):
        items.append({'@type':'ListItem','position':i,'name':label,'item':DOMAIN+path})
    return {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':items}


def base(title,desc,path,body,extra_schema=None,ogtype='website'):
    extra_schema=extra_schema or []
    if not path.startswith('/'):path='/'+path
    canonical=DOMAIN+path
    head=f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc,quote=True)}">
<link rel="canonical" href="{E(canonical,quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large"><meta name="theme-color" content="#09096A">
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="Northamptonshire Tutoring">
<meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:url" content="{E(canonical,quote=True)}">
<meta property="og:image" content="{DOMAIN}/assets/images/study-session.webp"><meta property="og:image:alt" content="Student studying with books and notes">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title,quote=True)}"><meta name="twitter:description" content="{E(desc,quote=True)}">
<link rel="icon" href="/assets/images/nwt-group-mark.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="/assets/vendor/bootstrap/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/global.css"><link rel="stylesheet" href="/assets/css/pages.css">
{jsonld(organization_schema())}{jsonld(site_schema())}{''.join(jsonld(x) for x in extra_schema)}
</head><body>{NAV}
<main id="main-content">{body}</main>
{FOOT}{COOKIE}
<script defer src="/assets/vendor/bootstrap/bootstrap.bundle.min.js"></script>
<script defer src="/assets/js/main.js"></script><script defer src="/assets/js/forms.js"></script>
</body></html>'''
    # SRI must match official JS CDN. We avoid a potentially wrong SRI hash by removing it.
    head=head.replace(' integrity="sha384-ENjdO4Dr2bkBIFxQpeo9MfN07P45sQ+eJA9l+ItC6Vzu6F8V+/TJcDiY/7ZmTT"','')
    return head


def write(path, html):
    # Relative internal links work at both the production domain root and
    # GitHub Pages project previews (e.g. /northamptonshire-tutoring/).
    # Canonical and structured-data URLs stay absolute to the production domain.
    dest = ROOT / path.lstrip('/')
    if dest.suffix == '.html':
        prefix = '../' * (len(dest.relative_to(ROOT).parts) - 1)
        def fix_link(match):
            target = match.group('target')
            if not target or target.startswith('#') or target.startswith('?'):
                target = 'index.html' + target
            return match.group('attr') + match.group('quote') + prefix + target + match.group('quote')
        html = re.sub(
            r'(?P<attr>\b(?:href|src|action|poster)=)(?P<quote>[\"\'])/(?P<target>[^\"\']*)(?P=quote)',
            fix_link, html
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding='utf-8')
    print('built', dest.relative_to(ROOT))


def button(text='Find a tutor',href='/contact.html',style='pink'):
    return f'<a href="{E(href)}" class="btn btn-{style}">{E(text)} <i class="bi bi-arrow-up-right" aria-hidden="true"></i></a>'


def hero_page(title,lead,crumbs,eyebrow='Northamptonshire online tutoring'):
    return f'''<section class="page-hero"><div class="container">{breadcrumbs(crumbs)}<span class="eyebrow">{E(eyebrow)}</span><h1>{E(title)}</h1><p>{E(lead)}</p><div class="hero-actions d-flex flex-wrap gap-2">{button('Enquire about lessons')}{button('WhatsApp our team',WHATSAPP,'outline-navy')}</div></div></section>'''


def form(id='enquiry-form',subject='New Northamptonshire Tutoring enquiry',intro=False):
    heading = '<div class="enquiry-top"><div><div class="form-tag">Speak to our team</div><h2>Find your ideal tutor</h2><p class="card-sub">Tell us what you need. We’ll help you find a suitable online tutor.</p></div><div class="decor-badge"><i class="bi bi-chat-heart" aria-hidden="true"></i></div></div>' if intro else '''<h2>Enquire about tutoring</h2><p class="text-secondary mb-4">Share a few details and we’ll help you with the next step.</p>'''
    return f'''<form id="{E(id)}" class="{ 'enquiry-card' if intro else 'contact-section-form' }" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
{heading}
<input type="hidden" name="access_key" value="{E(SITE['web3forms_access_key'])}">
<input type="hidden" name="subject" value="{E(subject)}">
<input type="hidden" name="from_name" value="Northamptonshire Tutoring Website">
<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" style="display:none!important" aria-hidden="true">
<div class="row g-3"><div class="col-12"><label class="form-label" for="{id}-name">Your name <span aria-hidden="true">*</span></label><input class="form-control" id="{id}-name" name="name" type="text" autocomplete="name" placeholder="Parent or student name" minlength="2" maxlength="100" required></div>
<div class="col-md-6"><label class="form-label" for="{id}-email">Email address *</label><input class="form-control" id="{id}-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" maxlength="200" required></div>
<div class="col-md-6"><label class="form-label" for="{id}-phone">Phone number *</label><input class="form-control" id="{id}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="07… or +44…" minlength="7" maxlength="25" required></div>
<div class="col-md-6"><label class="form-label" for="{id}-level">Student level</label><select class="form-select" id="{id}-level" name="student_level"><option value="">Choose level</option><option>Primary / SATs</option><option>KS3 / Years 7–9</option><option>GCSE</option><option>A-Level</option><option>Other</option></select></div>
<div class="col-md-6"><label class="form-label" for="{id}-subject">Subject</label><select class="form-select" id="{id}-subject" name="tuition_subject"><option value="">Choose subject</option><option>Maths</option><option>Physics</option><option>Chemistry</option><option>Biology</option><option>English</option><option>Combined Science</option><option>Other</option></select></div>
<div class="col-12"><label class="form-label" for="{id}-message">How can we help? *</label><textarea class="form-control" id="{id}-message" name="message" rows="3" minlength="10" maxlength="4000" placeholder="Year group, exam board, topics or preferred days…" required></textarea></div>
</div><button class="btn btn-pink form-button" type="submit">Send my enquiry <i class="bi bi-arrow-right" aria-hidden="true"></i></button>
<p class="form-status mt-2 mb-0" role="status" aria-live="polite"></p><p class="form-note mb-0 mt-2">No obligation to book. By sending an enquiry, you agree we may contact you about tutoring. <a href="/privacy.html">Privacy notice</a>.</p>
</form>'''


def faqs(items):
    return '<div class="faq-list">'+''.join(f'<details class="faq-item"><summary>{E(q)}</summary><div class="faq-answer">{E(a)}</div></details>' for q,a in items)+'</div>'


def cta(heading='Ready to find the right tutor?',desc='Tell us the subject, year group and exam board. We’ll help you take the next step towards personalised online lessons.'):
    return f'''<section class="section"><div class="container"><div class="cta-band"><span class="eyebrow light">Delivering a better future</span><h2>{E(heading)}</h2><p>{E(desc)}</p><div class="d-flex flex-wrap gap-2 mt-4">{button('Find my tutor')}{button('Message on WhatsApp',WHATSAPP,'outline-light')}</div></div></div></section>'''


def subject_cards():
    contents=[
      ('Maths tutoring','maths-tutoring-northamptonshire','calculator','GCSE, KS3 and A-Level Maths. Build confidence with algebra, fractions, graphs and exam questions.'),
      ('Physics tutoring','physics-tutoring-northamptonshire','lightning-charge','GCSE and A-Level Physics, from forces and electricity to equations and tricky concepts.'),
      ('Science tutoring','science-tutoring-northamptonshire','flask','KS3 and GCSE Combined or Separate Sciences, plus A-Level Biology and Chemistry.'),
      ('GCSE tutoring','gcse-tutoring-northamptonshire','mortarboard','Focused Year 10 and Year 11 revision in Maths, English, Science and more.'),
      ('A-Level tutoring','a-level-tutoring-northamptonshire','book','One-to-one sixth-form support in Maths, Physics, Chemistry, Biology and more.'),
      ('Primary & KS3','primary-tutoring-northamptonshire','pencil-square','Build essential Maths and English foundations, including SATs and Years 7–9.')]
    return '<div class="row g-3">'+''.join(f'<div class="col-sm-6 col-lg-4"><a class="subject-card card-soft" href="/{slug}.html"><span class="subject-icon"><i class="bi bi-{icon}" aria-hidden="true"></i></span><h3>{E(name)}</h3><p>{E(detail)}</p><span class="link-arrow">Explore tutoring <i class="bi bi-arrow-right" aria-hidden="true"></i></span></a></div>' for name,slug,icon,detail in contents)+'</div>'


def locations_grid():
    return '<div class="area-grid">'+''.join(f'<a class="area-link" href="/locations/{p["slug"]}.html">{E(p["name"])} <i class="bi bi-arrow-up-right" aria-hidden="true"></i></a>' for p in LOCATIONS)+'</div>'


def blog_cards(posts):
    return '<div class="row g-4">'+''.join(f'''<div class="col-md-6 col-lg-4"><article class="blog-card card-soft"><a href="/blog/{p['slug']}.html"><img loading="lazy" width="480" height="300" src="/assets/images/{p['image']}" alt="{E(p['category'])} study materials"></a><div class="blog-content"><div class="post-meta">{E(p['category'])} <span class="mx-2">•</span> {p['read_minutes']} min read</div><h3 class="mt-2"><a href="/blog/{p['slug']}.html">{E(p['title'])}</a></h3><p>{E(p['description'])}</p><a class="link-arrow" href="/blog/{p['slug']}.html">Read the guide <i class="bi bi-arrow-right" aria-hidden="true"></i></a></div></article></div>''' for p in posts)+'</div>'


HOME_FAQS=[
 ('Do you offer online GCSE Maths and Physics tutoring in Northamptonshire?','Yes. We offer one-to-one online tutoring in GCSE Maths, GCSE Physics and other subjects for pupils in Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and nearby areas.'),
 ('How much does online tutoring cost?','Lessons up to GCSE level start from £20 per hour. A-Level lessons start from £25 per hour. We will confirm the rate for the suitable tutor and subject before booking.'),
 ('Which exam boards do your tutors cover?','Our tutor network supports AQA, Pearson Edexcel, OCR, WJEC, Eduqas and Cambridge International (CAIE) specifications. Tell us your qualification and exam board when you enquire.'),
 ('Are lessons online or in person?','Northamptonshire Tutoring currently offers online one-to-one lessons. We do not advertise an in-person Northamptonshire tutoring centre.'),
 ('Can we request a tutor for GCSE Combined Science?','Yes. Please tell us whether you need Biology, Chemistry, Physics or a combination, plus your exam board and current year group.'),
 ('Can I choose a regular weekly time?','You can request preferred days and times. We will check a suitable tutor’s availability before confirming a recurring slot.'),
 ('How do we book our first lesson?','Use our enquiry form or WhatsApp us with the subject, year group, exam board and preferred availability. We will discuss a suitable tutor, rate and next steps.'),
]


def home():
    body=f'''<section class="hero"><div class="container"><div class="row g-lg-5 align-items-center"><div class="col-lg-7"><span class="eyebrow hero-eyebrow">One-to-one online tutoring across Northamptonshire</span><h1>GCSE, A-Level &amp; Maths tutors <em>in Northamptonshire.</em></h1><p class="hero-lead">Personalised online tutoring for pupils in <strong>Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry</strong> and beyond. Specialist support in <strong>Maths, Physics, Chemistry, Biology and English</strong>, tailored to your goals and exam board.</p><ul class="hero-bullets"><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> GCSE lessons from £20/hr</li><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> A-Level lessons from £25/hr</li><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> AQA · Edexcel · OCR &amp; more</li></ul><div class="hero-actions">{button('Find my tutor', '#enquiry-form')}{button('Explore subjects','#subjects','outline-navy')}</div><div class="hero-proof"><span class="proof-icon"><i class="bi bi-laptop" aria-hidden="true"></i></span><span><strong>Online lessons that fit around your life</strong>No travel. A tailored one-to-one learning plan.</span></div></div><div class="col-lg-5 hero-right">{form('enquiry-form',intro=True)}</div></div><div class="hero-bottom"><div class="row g-3 align-items-stretch"><div class="col-lg-7"><div class="hero-image-panel"><img src="/assets/images/study-session.webp" width="960" height="600" loading="eager" alt="Student revising with study notes and books for a tutoring lesson"><div class="image-float"><i class="bi bi-heart-fill" aria-hidden="true"></i> Delivering a better future</div></div></div><div class="col-lg-5"><div class="quick-stats"><div class="quick-stat"><strong>1-to-1</strong><span>Personalised online lessons</span></div><div class="quick-stat"><strong>£20<span style="font-size:1rem">/hr</span></strong><span>GCSE tuition from</span></div><div class="quick-stat"><strong>KS1–A-Level</strong><span>Support across school stages</span></div><div class="quick-stat"><strong>6 boards</strong><span>UK &amp; international specifications</span></div></div></div></div></div></div></section>
<section class="trust-strip" aria-label="Supported exam boards"><div class="container trust-inner"><span class="trust-title">Exam board support</span><span class="board">AQA</span><span class="board">Pearson Edexcel</span><span class="board">OCR</span><span class="board">WJEC</span><span class="board">Eduqas</span><span class="board">CAIE</span></div></section>
<section id="subjects" class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Tutoring for every step</span><h2>Online tutoring in Maths, Physics, Science, English and more</h2><p>Choose a subject or stage of learning. Each online lesson can be focused on the skills, topics and exam questions your child needs to practise.</p></div>{subject_cards()}</div></section>
<section class="section section-soft"><div class="container"><div class="row align-items-center g-5"><div class="col-lg-5"><div class="subject-feature-image"><img loading="lazy" width="800" height="800" src="/assets/images/online-tutoring.webp" alt="Student studying online at home with a laptop"></div></div><div class="col-lg-7"><span class="eyebrow">Why Northamptonshire Tutoring?</span><h2 class="display-font fw-bold mb-3" style="font-size:clamp(2rem,3.8vw,3.25rem)">Support that starts with what your child needs.</h2><p class="text-secondary mb-4">Some pupils need the fundamentals explained slowly; others want a challenging past-paper question broken down. We help match families with online tutors who can adapt lessons to the learner.</p><div class="row g-3"><div class="col-sm-6"><div class="value-card card-soft"><span class="value-num">01 / Personal</span><h3>One-to-one support</h3><p>Individual attention, questions and practice, not a generic lecture.</p></div></div><div class="col-sm-6"><div class="value-card card-soft"><span class="value-num">02 / Relevant</span><h3>Exam board focused</h3><p>Share AQA, Edexcel, OCR or another board so lessons suit your course.</p></div></div><div class="col-sm-6"><div class="value-card card-soft"><span class="value-num">03 / Flexible</span><h3>Learn from home</h3><p>Request lesson times that work around school and family commitments.</p></div></div><div class="col-sm-6"><div class="value-card card-soft"><span class="value-num">04 / Clear</span><h3>Simple next steps</h3><p>Tell us what help you need, and we’ll discuss your options.</p></div></div></div></div></div></div></section>
<section class="section"><div class="container"><div class="d-flex justify-content-between align-items-end flex-wrap gap-3 mb-4"><div class="section-heading mb-0"><span class="eyebrow">Meet a few of our group tutors</span><h2>Real tutors. Real subject support.</h2><p>Tutor matching depends on subject and availability. These are examples from the wider NWT tutor network.</p></div>{button('Enquire about availability')}</div><div class="row g-3">'''
    tutors=[('Robert','Maths & Physics','GCSE and A-Level Maths and Physics support.','robert'),('Sihaam','Physics & Science','Physics at GCSE and A-Level, plus GCSE science support.','sihaam'),('Ashley','English','English tutoring from KS3 through to A-Level.','ashley'),('Muskan','Maths & Sciences','GCSE Maths and Science, plus A-Level Biology and Chemistry.','muskan')]
    for name,subject,desc,pic in tutors:
        body+=f'''<div class="col-6 col-lg-3"><article class="tutor-card card-soft"><div class="tutor-photo"><img loading="lazy" width="600" height="600" src="/assets/images/tutor-{pic}.jpg" alt="{E(name)}, an NWT Group {E(subject)} tutor"></div><div class="tutor-info"><h3>{E(name)}</h3><div class="tutor-subject">{E(subject)}</div><p>{E(desc)}</p><a class="link-arrow" href="/contact.html">Ask about lessons <i class="bi bi-arrow-right"></i></a></div></article></div>'''
    body+='''</div><p class="form-note mt-3 mb-0">Tutor biographies are examples from the NWT Group network and do not guarantee availability in every subject or time slot.</p></div></section>'''
    body+='''<section class="section section-pink"><div class="container"><div class="row align-items-center g-5"><div class="col-lg-6"><span class="eyebrow">Straightforward prices</span><h2 style="font-size:clamp(2rem,3.7vw,3.4rem)">Online tutoring, with clear starting rates.</h2><p class="text-secondary">Lesson fees are confirmed before booking. Prices shown are starting rates for 60-minute one-to-one online sessions, subject to tutor and course.</p></div><div class="col-lg-6"><div class="row g-3"><div class="col-sm-6"><div class="price-card"><div class="price-level">Primary • KS3 • GCSE</div><div class="price">£20<small>/hr</small></div><p>From, per 60-minute online lesson.</p>'''+button('Enquire now')+'''</div></div><div class="col-sm-6"><div class="price-card featured"><div class="price-level">A-Level</div><div class="price">£25<small>/hr</small></div><p>From, per 60-minute online lesson.</p>'''+button('Enquire now')+'''</div></div></div></div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading center"><span class="eyebrow">How it works</span><h2>Book your first online tutoring lesson in three steps</h2><p>We make the process simple for families, whatever your pupil's current confidence or target grade.</p></div><div class="row g-3"><div class="col-lg-4"><div class="step-row"><span class="step-number">1</span><div><h3>Tell us what you need</h3><p>Share the year group, subject, exam board and goals.</p></div></div></div><div class="col-lg-4"><div class="step-row"><span class="step-number">2</span><div><h3>Discuss tutor options</h3><p>We check suitable tutors and the lesson times you prefer.</p></div></div></div><div class="col-lg-4"><div class="step-row"><span class="step-number">3</span><div><h3>Start learning online</h3><p>Once confirmed, attend your one-to-one lesson from home.</p></div></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row align-items-end mb-4 g-2"><div class="col-lg-8"><span class="eyebrow">Across Northamptonshire</span><h2 style="font-size:clamp(2rem,3.6vw,3.3rem)">Online tutors for Northampton, Kettering, Corby &amp; more</h2><p class="text-secondary">We support students throughout North and West Northamptonshire. Lessons are online, so you're not limited to a tutor in your town.</p></div><div class="col-lg-4 text-lg-end">'''+button('See all areas','/areas.html','outline-navy')+'''</div></div>'''+locations_grid()+'''<p class="text-secondary mt-3 mb-0 small">Also covering Oundle, Thrapston, Raunds, Rothwell, Desborough, Burton Latimer, Higham Ferrers, Irthlingborough and surrounding villages online.</p></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Helpful revision guidance</span><h2>Study tips for Northamptonshire families</h2><p>Useful, practical guides for choosing tutoring and preparing for Maths, Physics and school exams.</p></div>'''+blog_cards(POSTS[:3])+'''<div class="mt-4 text-center">'''+button('Explore the tutoring blog','/blog.html','outline-navy')+'''</div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">FAQs</span><h2 style="font-size:clamp(2rem,3.5vw,3.1rem)">Questions about online tutoring in Northamptonshire?</h2><p class="text-secondary">Here are answers to common questions about subjects, prices, exam boards and booking.</p>'''+button('Speak to our team')+'''</div><div class="col-lg-7">'''+faqs(HOME_FAQS)+'''</div></div></div></section>'''
    body+=cta('Let’s find the tutoring support your child needs.','GCSE Maths, A-Level Physics, Science, English or KS3 basics: tell us the subject and your preferred availability, and we’ll discuss suitable next steps.')
    extra=[service_schema('Online GCSE and A-Level tutoring in Northamptonshire','Online one-to-one tutoring in Maths, Physics, Chemistry, Biology and English across Northamptonshire.','/'),faq_schema(HOME_FAQS)]
    write('index.html',base('Northamptonshire Tutors | Online GCSE, A-Level, Maths & Physics Tutoring','Find online Maths, Physics, Science and English tutors in Northamptonshire. GCSE from £20/hr, A-Level from £25/hr. Serving Northampton, Kettering, Corby and more.','/',body,extra))


def about():
    body=hero_page('About Northamptonshire Tutoring','A local-facing online tutoring service backed by North Wales Tutoring Group. We help families across Northamptonshire find one-to-one teaching support that fits the learner. ', [('About us',None)],'Part of North Wales Tutoring Group')
    body+='''<section class="section"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-6"><span class="eyebrow">Our vision</span><h2 style="font-size:clamp(2rem,3.8vw,3.3rem)">Delivering a better future, one lesson at a time.</h2><p>Northamptonshire Tutoring is part of <a href="https://nwttutoring.com/" target="_blank" rel="noopener">North Wales Tutoring Group</a>, a UK online tutoring network. Our purpose is to make personalised academic support easier to access for students, parents and learners across Northamptonshire.</p><p>We focus on what helps a student move forward: understanding difficult concepts, asking questions without pressure, practising unfamiliar exam formats and building a routine that feels manageable.</p><p>We provide online tuition, rather than claiming to operate a physical tutoring centre or local school partnership.</p></div><div class="col-lg-6"><div class="subject-feature-image"><img loading="lazy" src="/assets/images/online-tutoring.webp" width="800" height="800" alt="Pupil working independently during an online study session"></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="section-heading center"><span class="eyebrow">What matters to us</span><h2>Our approach to online tutoring</h2></div><div class="row g-3"><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">01 / Confidence</span><h3>Questions are welcome</h3><p>Students should feel comfortable asking why an answer works, not just remembering steps.</p></div></div><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">02 / Structure</span><h3>Relevant learning goals</h3><p>We encourage lessons built around the learner’s year group, course specification and priority topics.</p></div></div><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">03 / Access</span><h3>Learning from anywhere</h3><p>Online delivery helps connect students in towns and villages to a broader tutor network.</p></div></div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-7"><span class="eyebrow">Who we support</span><h2>Maths, Physics and more, from primary school to sixth form</h2><p>Our tutor network supports KS1–KS3, Year 6 SATs, GCSE and A-Level pupils. Popular requests include GCSE Maths, GCSE Combined Science, A-Level Maths, A-Level Physics, Chemistry and English.</p><p>We take account of AQA, Edexcel, OCR, WJEC, Eduqas and Cambridge International syllabuses where relevant. If your subject isn't listed, you can still ask us about options.</p>'''+button('Find a tutor')+'''</div><div class="col-lg-5"><div class="area-panel"><h3>Northamptonshire areas</h3><p>Online support for students across North and West Northamptonshire:</p>'''+locations_grid()+'''</div></div></div></div></section>'''
    body+=cta()
    write('about.html',base('About Northamptonshire Tutoring | NWT Group Online Tutors','Learn how Northamptonshire Tutoring, part of North Wales Tutoring Group, supports GCSE, A-Level, Maths and Physics students through online one-to-one lessons.','/about.html',body,[crumb_schema([('About us','/about.html')])]))


def service_page(s):
    title=s['h1'];slug=s['slug'];path='/'+slug+'.html'
    body=hero_page(title,s['intro'],[(s['label']+' tutoring',None)],'Personalised one-to-one lessons')
    body+=f'''<section class="section"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-7 service-content"><span class="eyebrow">{E(s['label'])} tuition from home</span><h2>Focused {E(s['label'])} lessons for the topics that matter</h2><p>{E(s['who'])}</p><h3 class="fs-5 mt-4 mb-3">Topics we can work on</h3><ul>'''+''.join(f'<li>{E(x)}</li>' for x in s['topics'])+f'''</ul><p><strong>Exam board support:</strong> {E(s['boards'])}</p>{button('Ask about '+s['label']+' tutors')}</div><div class="col-lg-5"><div class="subject-feature-image"><img loading="lazy" src="/assets/images/{E(s['image'])}" width="800" height="800" alt="Study materials used for online {E(s['label'])} tutoring"></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="section-heading"><span class="eyebrow">Where we teach</span><h2>Online lessons throughout Northamptonshire</h2><p>Students can join from home in Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester, Brackley and neighbouring communities.</p></div>'''+locations_grid()+'''</div></section>'''
    fq=[(s['faq'],s['answer']),('Are online lessons one-to-one?','Yes. Tuition is delivered online in personalised one-to-one sessions rather than a physical tutoring centre in Northamptonshire.'),('How much does a lesson cost?','Up to GCSE level, prices start from £20 per hour. A-Level tutoring starts from £25 per hour, subject to the tutor and course.')]
    body+='''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Common questions</span><h2>'''+E(s['label'])+''' tutoring FAQs</h2><p>Contact us with your year group, exam board, topic needs and preferred times.</p>'''+button('Request tutor availability')+'''</div><div class="col-lg-7">'''+faqs(fq)+'''</div></div></div></section>'''
    body+=cta('Get tailored '+s['label']+' support online.','Tell us your level, exam board and the topics you want help with. We will discuss suitable tutor options and lesson times.')
    write(slug+'.html',base(s['title'],s['intro']+' Online lessons for Northampton, Kettering, Corby and surrounding areas.',path,body,[crumb_schema([(s['label']+' tutoring',path)]),service_schema(s['label']+' tutoring in Northamptonshire',s['intro'],path),faq_schema(fq)]))


def areas():
    body=hero_page('Online tutors across Northamptonshire','We help families access GCSE, A-Level and school tutoring from home in North Northamptonshire and West Northamptonshire. Explore location-specific guidance for major towns and neighbouring villages.', [('Areas we cover',None)])
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">North and West Northamptonshire</span><h2>Explore tutoring in your town</h2><p>Our tutoring is delivered online. These pages explain the support available to students living in each area, not a physical tuition centre.</p></div><div class="row g-3">'''
    for p in LOCATIONS:
        body+=f'''<div class="col-md-6 col-lg-4"><article class="value-card card-soft"><span class="value-num">{E(p['zone'])}</span><h3><a href="/locations/{p['slug']}.html">{E(p['name'])} tutors</a></h3><p>{E(p['benefit'])}</p><a class="link-arrow" href="/locations/{p['slug']}.html">See {E(p['name'])} tutoring <i class="bi bi-arrow-right" aria-hidden="true"></i></a></article></div>'''
    body+='''</div><div class="mt-5 area-panel"><h3>More towns and villages covered online</h3><p>In addition to the locations above, families in Oundle, Thrapston, Raunds, Desborough, Rothwell, Burton Latimer, Higham Ferrers, Irthlingborough, Finedon, Earls Barton, Long Buckby, Silverstone, Brixworth, Roade and other Northamptonshire villages can enquire about lessons.</p></div></div></section>'''
    body+=cta('Live in Northamptonshire? Start your tutoring enquiry.','Wherever you are in the county, tell us the subject, year group and preferred times so we can discuss online tutor options.')
    write('areas.html',base('Online Tutors Across Northamptonshire | Towns & Areas We Cover','Find GCSE, Maths, Physics and A-Level online tutors covering Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and Brackley.','/areas.html',body,[crumb_schema([('Areas we cover','/areas.html')])]))


def location_page(p):
    name=p['name'];path='/locations/'+p['slug']+'.html'
    title='Online GCSE, Maths & Physics Tutors in '+name
    lead=f"Need a tutor in {name}? We provide personalised online one-to-one lessons for Primary, KS3, GCSE and A-Level students in {name} and nearby Northamptonshire communities."
    body=hero_page(title,lead,[('Areas we cover','/areas.html'),(name,None)],'Online tutoring in '+p['zone'])
    body+=f'''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-7 area-content"><span class="eyebrow">Tutoring for {E(name)} families</span><h2>Maths, Physics and GCSE tutoring for students in {E(name)}</h2><p>{E(p['specific'])}</p><p>{E(p['benefit'])}</p><p>Ask us about <strong>Maths, Physics, Chemistry, Biology, English, Combined Science and other courses</strong>. Lessons can be tailored to the student's year group and exam board, including AQA, Edexcel, OCR and other UK qualifications where applicable.</p><h3 class="fs-5 mt-4">Common tutoring requests in {E(name)}</h3><ul><li>{E(p['focus'])}</li><li>Year 10 and Year 11 GCSE mock and final-exam preparation</li><li>KS3 confidence-building and sixth-form A-Level practice</li></ul>{button('Find a tutor in '+name)}</div><div class="col-lg-5"><div class="area-panel"><h3>Areas around {E(name)}</h3><p>Online tutoring is available to families in {E(name)} and nearby places, including:</p><ul>'''+''.join(f'<li><i class="bi bi-geo-alt" aria-hidden="true"></i> {E(n)}</li>' for n in p['nearby'])+f'''</ul><p class="form-note mb-0">Lessons are online, not at a local tutoring centre.</p></div><div class="mt-3 subject-feature-image" style="min-height:220px;max-height:260px"><img src="/assets/images/study-session.webp" alt="Books and notes for one-to-one online tuition" loading="lazy" width="960" height="600"></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="section-heading"><span class="eyebrow">Subjects available</span><h2>Choose the right online tutoring subject</h2><p>From GCSE Maths and Physics to A-Level Chemistry and KS3 English, find out what learning support we offer.</p></div>'''+subject_cards()+'''</div></section>'''
    fq=[(f'Do you offer GCSE Maths and Physics tutoring in {name}?',f'Yes. We provide online GCSE Maths and Physics tuition for families in {name}, subject to suitable tutor availability.'),
        (f'Is there a physical tutoring centre in {name}?','No. Our lessons are currently online and one-to-one. Students can join from home.'),
        ('What should I include in my enquiry?','Please include the student year group, subject, exam board, topics they find difficult and preferred times. This helps us discuss tutor options.'),
        ('What are the starting lesson prices?','Up to GCSE level, tuition starts at £20 per hour. A-Level support starts at £25 per hour, depending on the tutor and subject.')]
    body+='''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Local tutoring questions</span><h2>'''+E(name)+''' tutoring FAQs</h2><p>Learn how our one-to-one online lessons work for pupils in this area.</p>'''+button('Ask about lessons')+'''</div><div class="col-lg-7">'''+faqs(fq)+'''</div></div></div></section>'''
    body+=cta('Enquire about online tutoring in '+name+'.','Tell us about your child’s year group and subject. We can discuss a suitable online tutor, starting rates and preferred lesson days.')
    write(path,base(f'{name}, Northamptonshire Tutors | GCSE Maths, Physics & A-Level',f'Online Maths, Physics, Science and English tutors for {name} and nearby Northamptonshire areas. GCSE from £20/hr, A-Level from £25/hr.',path,body,[crumb_schema([('Areas we cover','/areas.html'),(name,path)]),service_schema('Online tutoring for students in '+name,lead,path,area=name+', Northamptonshire'),faq_schema(fq)]))


def contact():
    body=hero_page('Contact Northamptonshire Tutoring','Enquire about an online tutor for GCSE Maths, A-Level Physics, Combined Science, Chemistry, Biology, English or another subject. We will discuss your needs and tutor availability.',[('Contact',None)],'We’re here to help')
    body+='''<section class="section section-soft"><div class="container"><div class="contact-layout"><div><span class="eyebrow">Your next step</span><h2 style="font-size:clamp(2rem,3.5vw,3.1rem)">Let’s find a suitable tutor.</h2><p class="text-secondary mb-4">We support families throughout Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester, Brackley and the wider county.</p><a class="contact-method" href="mailto:northamptonshire@nwttutoring.com"><i class="bi bi-envelope" aria-hidden="true"></i><span><strong>Email our team</strong><span>northamptonshire@nwttutoring.com</span></span></a><a class="contact-method" href="https://wa.me/447480231362?text=Hi%2C%20I%27m%20looking%20for%20an%20online%20tutor%20in%20Northamptonshire."><i class="bi bi-whatsapp" aria-hidden="true"></i><span><strong>WhatsApp us</strong><span>+44 7480 231362</span></span></a><div class="area-panel mt-4"><h3>What helps us match a tutor?</h3><ul><li><i class="bi bi-check-circle"></i> Pupil's year group and subject</li><li><i class="bi bi-check-circle"></i> Exam board and any key topics</li><li><i class="bi bi-check-circle"></i> Preferred days and times</li><li><i class="bi bi-check-circle"></i> Goals or upcoming assessments</li></ul></div></div><div>'''+form('contact-enquiry','New contact enquiry from Northamptonshire Tutoring')+'''</div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">What happens after you enquire?</span><h2>A simple route to your first online lesson</h2><p>We’ll review your request, discuss potential tutor options and confirm the rate and availability before a booking is made.</p></div><div class="row g-3"><div class="col-md-4"><div class="step-row"><span class="step-number">1</span><div><h3>Send your enquiry</h3><p>Tell us what you need support with.</p></div></div></div><div class="col-md-4"><div class="step-row"><span class="step-number">2</span><div><h3>Discuss a tutor</h3><p>We check the right subject and available times.</p></div></div></div><div class="col-md-4"><div class="step-row"><span class="step-number">3</span><div><h3>Confirm a lesson</h3><p>We share the lesson arrangements before you start.</p></div></div></div></div></div></section>'''
    write('contact.html',base('Contact Northamptonshire Tutoring | Enquire About Online Tutors','Contact Northamptonshire Tutoring for Maths, Physics, GCSE and A-Level online lessons. Email northamptonshire@nwttutoring.com or send an enquiry form.','/contact.html',body,[crumb_schema([('Contact','/contact.html')])]))


def blog_index():
    body=hero_page('Northamptonshire tutoring blog','Helpful guidance for parents and students covering GCSE Maths, Physics revision, A-Level study habits and choosing the right online tutor.',[('Blog',None)],'Learning guides & revision advice')
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Latest study guides</span><h2>Practical tutoring advice and revision resources</h2><p>Read our short guides on exam preparation and making the most of online one-to-one tutoring.</p></div>'''+blog_cards(POSTS)+'''</div></section>'''
    body+=cta('Need help with a specific Maths or Physics topic?','You don’t have to work through it alone. Tell us what your child is finding difficult and we’ll discuss tailored online tutoring.')
    write('blog.html',base('Northamptonshire Tutoring Blog | GCSE, Maths & Physics Advice','Read GCSE Maths, GCSE Physics and A-Level study guides for students and parents in Northamptonshire. Practical tips from an online tutoring team.','/blog.html',body,[crumb_schema([('Blog','/blog.html')])]))


def blog_article(post):
    path='/blog/'+post['slug']+'.html'
    content=read('source/blog/'+post['slug']+'.html')
    body=f'''<section class="page-hero"><div class="container">{breadcrumbs([('Blog','/blog.html'),(post['title'],None)])}<span class="eyebrow">{E(post['category'])} study guide</span><h1>{E(post['title'])}</h1><p>{E(post['description'])}</p><div class="post-meta">Published {date.fromisoformat(post['date']).strftime('%d %B %Y')} <span class="mx-2">•</span> {post['read_minutes']} min read</div></div></section><section class="section"><div class="container"><article class="article-content"><figure class="article-figure"><img loading="eager" width="960" height="600" src="/assets/images/{post['image']}" alt="{E(post['category'])} study resources"></figure>{content}<div class="mt-5 p-4 card-soft"><h2 class="mt-0 fs-3">Looking for subject support in Northamptonshire?</h2><p>We can discuss one-to-one online tutoring for GCSE and A-Level students in Northampton, Kettering, Corby, Wellingborough, Rushden and elsewhere in the county.</p>{button('Ask about tutoring')}</div></article></div></section>'''
    article={'@context':'https://schema.org','@type':'BlogPosting','headline':post['title'],'description':post['description'],'datePublished':post['date'],'dateModified':post['date'],'mainEntityOfPage':DOMAIN+path,'image':DOMAIN+'/assets/images/'+post['image'],'author':{'@type':'Organization','name':SITE['brand']},'publisher':{'@id':DOMAIN+'/#organisation'}}
    write(path,base(post['title']+' | Northamptonshire Tutoring',post['description'],path,body,[crumb_schema([('Blog','/blog.html'),(post['title'],path)]),article],ogtype='article'))


def legal():
    privacy=hero_page('Privacy policy','How we use the information you provide when you enquire about online tutoring.',[('Privacy',None)],'Your data')
    privacy+='''<section class="section"><div class="container legal-content"><p><strong>Last reviewed:</strong> 11 November 2026</p><h2>Who we are</h2><p>Northamptonshire Tutoring is part of North Wales Tutoring Group. For questions about personal information submitted through this website, contact <a href="mailto:northamptonshire@nwttutoring.com">northamptonshire@nwttutoring.com</a>.</p><h2>Information we collect</h2><p>When you complete our enquiry form, you may provide your name, email address, telephone number, the student's year group, subjects, course information and the details you choose to include in your message. Please avoid providing sensitive medical or personal details through the enquiry form.</p><h2>How we use that information</h2><p>We use enquiry information to reply to you, discuss tuition options, determine whether suitable tutors may be available and arrange lessons if requested. We may retain appropriate administrative records for managing enquiries and lessons. We do not use contact-form details to send unrelated marketing messages without an appropriate basis.</p><h2>Our legal bases</h2><p>Depending on the circumstances, processing may be necessary to take steps you request before entering into tutoring arrangements, to fulfil agreed services or for legitimate interests in handling genuine enquiries. Other processing may be required to meet legal obligations.</p><h2>Service providers and transfers</h2><p>Our contact form uses <a href="https://web3forms.com/" target="_blank" rel="noopener">Web3Forms</a>, which processes submitted form data and forwards enquiries to our email. Information may be processed outside the UK, including by service providers. Where relevant, we consider the safeguards required by applicable data protection law.</p><h2>Retention and your rights</h2><p>We aim to keep information only for as long as reasonably needed for the stated purposes and applicable record-keeping duties. You may request access, correction, erasure or restriction of your data where the law provides these rights. Contact us using the email above. You may also raise concerns with the UK Information Commissioner's Office (ICO).</p><h2>Website storage</h2><p>We use browser storage to remember your cookie preference. See our <a href="/cookie-policy.html">cookie policy</a> for more information.</p><p>We may update this policy when our services or providers change. Please review this page for the latest version.</p></div></section>'''
    write('privacy.html',base('Privacy Policy | Northamptonshire Tutoring','How Northamptonshire Tutoring uses enquiry form information, contact details and website storage.','/privacy.html',privacy,[crumb_schema([('Privacy','/privacy.html')])]))
    cookies=hero_page('Cookie policy','Information about the browser storage and optional cookies used on Northamptonshire Tutoring.',[('Cookie policy',None)],'Website privacy')
    cookies+='''<section class="section"><div class="container legal-content"><p><strong>Last reviewed:</strong> 11 November 2026</p><h2>How our cookie choices work</h2><p>Our website stores your cookie-banner preference in your browser under the key <code>northamptonshire_tutoring_cookie_choice_v1</code>. This stops the banner displaying every time you move to another page. This is local browser storage, rather than a tracking cookie.</p><h2>Optional analytics and marketing</h2><p>At initial launch, the supplied website does not load Google Analytics, Meta Pixel or advertising trackers. Our banner provides accept and reject options in case consent-controlled services are added later; choosing “Accept optional” does not itself activate tracking on this version of the site. Any future non-essential tracking should be held back unless consent has been given and this policy is updated.</p><h2>External services</h2><p>We load Bootstrap assets and fonts from external providers. Using the contact form sends your enquiry to Web3Forms. These services may process technical data according to their own policies. We do not set advertising cookies through the supplied website code.</p><h2>Change your choice</h2><p>You can reset your selection by removing this site's local storage in your browser settings, then refresh the page. The banner will appear again.</p><h2>Contact</h2><p>Email <a href="mailto:northamptonshire@nwttutoring.com">northamptonshire@nwttutoring.com</a> with questions about the website's privacy practices.</p></div></section>'''
    write('cookie-policy.html',base('Cookie Policy | Northamptonshire Tutoring','Read the Northamptonshire Tutoring cookie policy, including cookie consent choices, browser storage and external services.','/cookie-policy.html',cookies,[crumb_schema([('Cookie policy','/cookie-policy.html')])]))


def search_files():
    urls=['/','/about.html','/areas.html','/contact.html','/blog.html','/privacy.html','/cookie-policy.html']
    urls += ['/'+p['slug']+'.html' for p in SUBJECTS]
    urls += ['/locations/'+p['slug']+'.html' for p in LOCATIONS]
    urls += ['/blog/'+p['slug']+'.html' for p in POSTS]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path in urls:
        sitemap+=f'<url><loc>{DOMAIN+path}</loc><lastmod>2026-11-11</lastmod></url>\n'
    sitemap+='</urlset>\n'
    write('sitemap.xml',sitemap)
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')


def main():
    home();about();areas();contact();blog_index()
    for s in SUBJECTS:service_page(s)
    for p in LOCATIONS:location_page(p)
    for p in POSTS:blog_article(p)
    legal();search_files()
    print('Build complete:',len(list(ROOT.rglob('*.html'))),'HTML files (including shared components / article sources).')

if __name__=='__main__':main()
