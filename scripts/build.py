#!/usr/bin/env python3
"""Build accessible, SEO-ready standalone HTML from shared components + JSON.

Run: python3 scripts/build.py
This produces deployable HTML, with headers/footer/cookie HTML inlined so
search engines and visitors see navigation even without client-side JS.
"""
from pathlib import Path
from html import escape as E
from datetime import date
from urllib.parse import quote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: (ROOT / p).read_text(encoding='utf-8')
load = lambda p: json.loads(read(p))
SITE = load('data/site.json')
LOCATIONS = load('data/locations.json')
SUBJECTS = load('data/subjects.json')
POSTS = load('data/blog.json')
TUTORS = load('data/tutors.json')
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
        'description':'Online one-to-one tutoring across Northamptonshire in GCSE and A-Level Maths, Further Maths, Physics, Chemistry, Biology, English, Economics, Business, Computer Science, Humanities, Languages, Psychology and other school subjects.',
        'slogan':SITE['motto'],'email':EMAIL,'telephone':SITE['phone_international'],
        'parentOrganization':{'@type':'Organization','name':SITE['parent'],'url':SITE['parent_url']},
        'areaServed':[{'@type':'AdministrativeArea','name':'Northamptonshire, England'}]+[{'@type':'City','name':n+', Northamptonshire'} for n in AREA_NAMES],
        'sameAs':[SITE['facebook'],SITE['instagram']],
        'hasOfferCatalog':{'@type':'OfferCatalog','name':'Online tutoring subjects','itemListElement':[{'@type':'OfferCatalog','name':s['label'],'url':DOMAIN+'/'+s['slug']+'.html'} for s in SUBJECTS]},
        'knowsAbout':SITE['subject_range']+SITE['exam_boards']}




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
<meta property="og:image" content="{DOMAIN}/assets/images/study-session.webp"><meta property="og:image:alt" content="Personalised online tutoring and revision support">
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
<script defer src="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.all.min.js"></script>
<script defer src="/assets/js/main.js"></script><script defer src="/assets/js/forms.js"></script>
</body></html>'''
    return head




def write(path,html):
    dest=ROOT / path.lstrip('/')
    dest.parent.mkdir(parents=True,exist_ok=True)
    # Use path-relative internal links so both custom-domain hosting and
    # GitHub Pages /northamptonshire-tutoring/ previews work without rewrites.
    if dest.suffix == '.html':
        root_prefix = '../' * (len(dest.relative_to(ROOT).parts) - 1)
        html = re.sub(r'(?P<attr>\b(?:href|src)=([\"\']))/(?P<target>[^\"\']*)',
                      lambda m: m.group('attr') + root_prefix + (m.group('target') or './'), html)
    dest.write_text(html,encoding='utf-8')
    print('built',dest.relative_to(ROOT))


def button(text='Find my tutor',href='/contact.html',style='pink'):
    return f'<a href="{E(href,quote=True)}" class="btn btn-{style}">{E(text)}</a>'




def hero_page(title,lead,crumbs,eyebrow='Northamptonshire online tutoring'):
    return f'''<section class="page-hero"><div class="container">{breadcrumbs(crumbs)}<span class="eyebrow">{E(eyebrow)}</span><h1>{E(title)}</h1><p>{E(lead)}</p><div class="hero-actions d-flex flex-wrap gap-2">{button('Enquire about lessons')}{button('WhatsApp our team',WHATSAPP,'outline-navy')}</div></div></section>'''


def form(id='enquiry-form',subject='New Northamptonshire Tutoring enquiry',intro=False):
    heading = '<div class="enquiry-top"><div><div class="form-tag">Free, no-obligation enquiry</div><h2>Find the right tutor</h2><p class="card-sub">Tell us what your learner needs. We’ll help you choose suitable one-to-one support.</p></div><div class="decor-badge"><i class="bi bi-chat-heart" aria-hidden="true"></i></div></div>' if intro else '<h2>Tell us what your child needs</h2><p class="text-secondary mb-4">Tell us the year group, subject, exam board and ideal lesson times in one message.</p>'
    return f'''<form id="{E(id)}" class="{'enquiry-card' if intro else 'contact-section-form'}" action="#" method="post" data-web3forms>
{heading}
<input type="hidden" name="access_key" value="{E(SITE['web3forms_access_key'])}">
<input type="hidden" name="subject" value="{E(subject)}">
<input type="hidden" name="from_name" value="Northamptonshire Tutoring">
<div class="honeypot" aria-hidden="true" style="position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden"><label for="{id}-bot">Do not fill this</label><input type="checkbox" name="botcheck" id="{id}-bot" tabindex="-1" autocomplete="off"></div>
<div class="row g-3"><div class="col-12"><label class="form-label" for="{id}-name">Your name *</label><input class="form-control" id="{id}-name" name="name" type="text" autocomplete="name" placeholder="Parent or student name" minlength="2" maxlength="100" required></div>
<div class="col-md-6"><label class="form-label" for="{id}-email">Email address *</label><input class="form-control" id="{id}-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" maxlength="200" required></div>
<div class="col-md-6"><label class="form-label" for="{id}-phone">Phone number *</label><input class="form-control" id="{id}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="07… or +44…" minlength="7" maxlength="25" required></div>
<div class="col-12"><label class="form-label" for="{id}-message">How can we help? *</label><textarea class="form-control" id="{id}-message" name="message" rows="4" minlength="10" maxlength="4000" placeholder="For example: Year 10, GCSE Maths Higher Tier, AQA. Struggling with algebra and graphs, looking for lessons on Tuesday evenings." required></textarea></div>
</div><button class="btn btn-pink form-button" type="submit">Request a tutor match</button>
<p class="form-status mt-2 mb-0" role="status" aria-live="polite"></p><p class="form-note mb-0 mt-2">No subscription or commitment to book. We’ll only use your details to discuss tutoring. <a href="/privacy.html">Privacy notice</a>.</p>
</form>'''




def faqs(items):
    return '<div class="faq-list">'+''.join(f'<details class="faq-item"><summary>{E(q)}</summary><div class="faq-answer">{E(a)}</div></details>' for q,a in items)+'</div>'


def cta(heading='Ready to find the right tutor?',desc='Tell us the subject, year group and exam board. We’ll help you take the next step towards personalised online lessons.'):
    return f'''<section class="section"><div class="container"><div class="cta-band"><span class="eyebrow light">Delivering a better future</span><h2>{E(heading)}</h2><p>{E(desc)}</p><div class="d-flex flex-wrap gap-2 mt-4">{button('Find my tutor')}{button('Message on WhatsApp',WHATSAPP,'outline-light')}</div></div></div></section>'''


def subject_cards(items=None):
    items=items or SUBJECTS
    icon_map={'maths-tutoring-northamptonshire':'📐','physics-tutoring-northamptonshire':'⚛️','science-tutoring-northamptonshire':'🧪','gcse-tutoring-northamptonshire':'📝','a-level-tutoring-northamptonshire':'🎓','primary-tutoring-northamptonshire':'✏️','english-tutoring-northamptonshire':'📖','biology-tutoring-northamptonshire':'🧬','chemistry-tutoring-northamptonshire':'⚗️','economics-tutoring-northamptonshire':'📈','business-tutoring-northamptonshire':'💼','computer-science-tutoring-northamptonshire':'💻','humanities-tutoring-northamptonshire':'🌍','languages-tutoring-northamptonshire':'🗣️','psychology-sociology-tutoring-northamptonshire':'🧠','health-social-care-tutoring-northamptonshire':'🩺','entrance-exam-tutoring-northamptonshire':'🏆','further-maths-tutoring-northamptonshire':'➗'}
    out=['<div class="row g-3">']
    for s in items:
        icon=icon_map.get(s['slug'],'📚')
        detail=s.get('short',s['intro'])
        out.append(f'<div class="col-sm-6 col-lg-4"><a class="subject-card card-soft" href="/{s["slug"]}.html"><span class="subject-icon" aria-hidden="true">{icon}</span><h3>{E(s["label"])} tutoring</h3><p>{E(detail)}</p><span class="card-cta">Explore {E(s["label"])} tutoring</span></a></div>')
    return ''.join(out)+'</div>'




def locations_grid():
    return '<div class="area-grid">'+''.join(f'<a class="area-link" href="/locations/{p["slug"]}.html">{E(p["name"])} tutoring</a>' for p in LOCATIONS)+'</div>'


HOME_FAQS=[
 ('What subjects can I book an online tutor for in Northamptonshire?','Our wider NWT Group network covers Maths, Further Maths, Physics, Chemistry, Biology, Combined Science, English Language, English Literature, Economics, Business, Computer Science, History, Geography, Religious Studies, Psychology, Sociology, French, Spanish, Chinese, Welsh, Art & Design, Health & Social Care and more. Tell us your subject and level so we can check the most suitable tutor.'),
 ('How much does GCSE or A-Level tutoring cost?','One-to-one GCSE tutoring starts from £23 per hour and A-Level tutoring starts from £28 per hour. Some specialist subjects and tutors cost more. We always confirm the tutor, lesson fee and availability before you book.'),
 ('Do you offer GCSE Maths and Physics tutoring in Northamptonshire?','Yes. We support GCSE Maths, Further Maths and Physics for students in Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester, Brackley and surrounding towns, with lessons delivered online.'),
 ('Can you match tutors to AQA, Edexcel and OCR exam boards?','Yes. Tell us the awarding body, specification, year group and any course options such as Foundation or Higher tier. Our network also supports WJEC, Eduqas and Cambridge International where suitable.'),
 ('Can we get help with 11+, SATs, TMUA or UCAT preparation?','You can enquire about Year 6 SATs, 11+, 13+, TMUA, UCAT and selected entrance or admissions tests. We match the specific test requirements against tutor expertise and availability.'),
 ('Do you offer lessons at home or in a Northamptonshire centre?','Northamptonshire Tutoring offers online lessons for families across the county. We do not advertise a local physical tutoring centre. Students study from home with a suitable online tutor.'),
 ('Do I need to subscribe or commit to a long contract?','No subscription is needed. We discuss subject, tutor, lesson price and preferred times before you decide whether to book.'),
 ('How do I start my first lesson?','Complete the short form with your name, email, phone and a message such as Year 10 GCSE Maths Higher Tier AQA. We will discuss suitable tutor options and how to arrange your first lesson.'),
]




def blog_cards(posts):
    out=['<div class="row g-4">']
    for p in posts:
        out.append(f'''<div class="col-md-6 col-lg-4"><a class="blog-card card-soft" href="/blog/{p['slug']}.html"><img loading="lazy" width="480" height="300" src="/assets/images/{p['image']}" alt="{E(p['category'])} study materials"><div class="blog-content"><div class="post-meta">{E(p['category'])} · {p['read_minutes']} minute guide</div><h3 class="mt-2">{E(p['title'])}</h3><p>{E(p['description'])}</p><span class="card-cta">Read this guide</span></div></a></div>''')
    return ''.join(out)+'</div>'




def home():
    featured_slugs=['maths-tutoring-northamptonshire','physics-tutoring-northamptonshire','science-tutoring-northamptonshire','english-tutoring-northamptonshire','economics-tutoring-northamptonshire','computer-science-tutoring-northamptonshire','languages-tutoring-northamptonshire','humanities-tutoring-northamptonshire','entrance-exam-tutoring-northamptonshire']
    featured=[SUB_LOOKUP[x] for x in featured_slugs]
    body=f'''<section class="hero"><div class="container"><div class="row g-lg-5 align-items-center"><div class="col-lg-7"><span class="eyebrow hero-eyebrow">Northamptonshire's online tutoring service · Part of NWT Group</span><h1>Online tutors in Northamptonshire <em>for GCSE, A-Level &amp; more.</em></h1><p class="hero-lead">Struggling with a topic? Preparing for mocks? Aiming higher? Find personalised <strong>GCSE, A-Level and school tutoring</strong> in <strong>Maths, Physics, Chemistry, Biology, English, Economics, Business, Computer Science, Humanities, Languages</strong> and more. Helping families in <strong>Northampton, Kettering, Corby, Wellingborough</strong> and across the county.</p><ul class="hero-bullets"><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> GCSE from <strong>£23/hr</strong></li><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> A-Level from <strong>£28/hr</strong></li><li><i class="bi bi-check-circle-fill" aria-hidden="true"></i> No subscriptions or long-term contracts</li></ul><div class="hero-actions">{button('Find my tutor','#enquiry-form')}{button('See all subjects','/subjects.html','outline-navy')}</div><div class="hero-proof"><span class="proof-icon"><i class="bi bi-patch-check" aria-hidden="true"></i></span><span><strong>Matched to the learner, not a generic timetable</strong>Share the subject, year group, exam board and goals. We'll check suitable tutors.</span></div></div><div class="col-lg-5 hero-right">{form('enquiry-form',intro=True)}</div></div><div class="hero-bottom"><div class="row g-3 align-items-stretch"><div class="col-lg-7"><div class="hero-image-panel"><img src="/assets/images/study-session.webp" width="960" height="600" loading="eager" alt="Student preparing for a GCSE exam with study books and revision notes"><div class="image-float"><i class="bi bi-heart-fill" aria-hidden="true"></i> Delivering a better future</div></div></div><div class="col-lg-5"><div class="quick-stats"><div class="quick-stat"><strong>1-to-1</strong><span>Online lessons personalised to you</span></div><div class="quick-stat"><strong>£23<span style="font-size:1rem">/hr</span></strong><span>GCSE tutoring starts from</span></div><div class="quick-stat"><strong>Primary–A-Level</strong><span>Plus entrance exams and adult study</span></div><div class="quick-stat"><strong>All key boards</strong><span>AQA, Edexcel, OCR and more</span></div></div></div></div></div></div></section>
<section class="trust-strip" aria-label="Exam boards supported"><div class="container trust-inner"><span class="trust-title">Tutor matching for</span><span class="board">AQA</span><span class="board">Pearson Edexcel</span><span class="board">OCR</span><span class="board">WJEC</span><span class="board">Eduqas</span><span class="board">CAIE</span></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Tutoring at every stage</span><h2>From Primary and SATs to GCSE, A-Level and university preparation</h2><p>Your child shouldn't have to fit a one-size-fits-all course. We help you find personalised support that meets their current level, subject, assessment and goals.</p></div><div class="row g-3">'''
    stages=[('✏️','Primary, SATs & 11+','Build reading, writing, Maths and exam confidence in primary school.','/primary-tutoring-northamptonshire.html'),('📗','KS3 & Years 7–9','Tackle knowledge gaps before the step up to GCSE.','/primary-tutoring-northamptonshire.html'),('📝','GCSE & resits','Get specification-focused support for mock exams, Higher/Foundation tiers and final papers.','/gcse-tutoring-northamptonshire.html'),('🎓','A-Level & sixth form','Work on challenging topics, extended answers and exam technique across a broad subject range.','/a-level-tutoring-northamptonshire.html'),('🏆','Entrance & admissions','Ask about 11+, SATs, TMUA, UCAT and specialist test preparation.','/entrance-exam-tutoring-northamptonshire.html'),('💡','Adult & university study','Request suitable help for university Maths, Functional Skills, languages and study goals.','/subjects.html')]
    for icon,name,desc,href in stages:
        body+=f'<div class="col-md-6 col-lg-4"><a class="stage-card" href="{href}"><span class="stage-icon" aria-hidden="true">{icon}</span><h3>{E(name)}</h3><p>{E(desc)}</p><span class="card-cta">Explore tutoring options</span></a></div>'
    body+='</div></div></section>'
    body+='''<section id="subjects" class="section section-soft"><div class="container"><div class="section-heading"><span class="eyebrow">More than Maths, Science and English</span><h2>Online tutors for the subjects your child actually studies</h2><p>Need GCSE Physics equations, A-Level Economics essays, GCSE History, French speaking practice or Computer Science debugging? Our group network covers core subjects, specialist subjects and vocational qualifications. Check the right tutor for the exact course.</p></div>'''+subject_cards(featured)+'''<div class="mt-4 text-center">'''+button('Browse all 18 tutoring services','/subjects.html','outline-navy')+'''</div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-5"><div class="subject-feature-image"><img loading="lazy" width="800" height="800" src="/assets/images/online-tutoring.webp" alt="Student building confidence through online tuition"></div></div><div class="col-lg-7"><span class="eyebrow">Make tutoring time count</span><h2 class="display-font fw-bold mb-3" style="font-size:clamp(2rem,3.8vw,3.25rem)">Don't spend another term guessing what needs fixing.</h2><p class="text-secondary mb-4">A lower mock grade, a difficult topic or a loss of confidence can feel overwhelming. The right one-to-one tutoring helps turn that into an actionable plan, with teaching that follows the student's actual exam specification rather than generic worksheets.</p><div class="proof-check"><i class="bi bi-check-circle-fill"></i><span><strong>Find the gaps</strong>Focus on the topics, exam questions and skills where support will make the most sense.</span></div><div class="proof-check"><i class="bi bi-check-circle-fill"></i><span><strong>Learn with a suitable tutor</strong>Discuss subject, level, pace, learning needs and availability with our team.</span></div><div class="proof-check"><i class="bi bi-check-circle-fill"></i><span><strong>Practise for the real assessment</strong>Build confidence using your specification, past-paper skills and structured explanations.</span></div>'''+button('Tell us what help you need')+'''</div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="d-flex justify-content-between align-items-end flex-wrap gap-3 mb-4"><div class="section-heading mb-0"><span class="eyebrow">Our wider NWT Group tutor network</span><h2>Experienced tutors across a much wider subject range</h2><p>Meet a selection of the group tutors listed in our current parent-company directory. We will check each person's suitability and availability before discussing a lesson.</p></div>'''+button('See more group tutors','/tutors.html','outline-navy')+'''</div>'''+tutor_cards(TUTORS[:8])+'''<p class="tutor-availability-note">These are examples from the wider NWT Group directory, not a guarantee that any individual has spaces available now. Tutor availability and prices vary.</p></div></section>'''
    body+='''<section class="section section-pink"><div class="container"><div class="row align-items-center g-5"><div class="col-lg-6"><span class="eyebrow">Clear starting prices</span><h2 style="font-size:clamp(2rem,3.7vw,3.4rem)">Invest in focused lessons, not another subscription.</h2><p class="text-secondary">One-to-one, online tuition with straightforward hourly rates. You choose whether to proceed after we confirm tutor availability, lesson price and subject fit. Specialist subjects and more experienced tutors may cost more.</p><p class="note-panel"><strong>Other levels and specialist courses?</strong> Ask us for the rate that matches your child’s exact subject, year group and requirements.</p></div><div class="col-lg-6"><div class="row g-3"><div class="col-sm-6"><a class="price-link" href="/contact.html"><div class="price-card"><div class="price-level">GCSE tutoring</div><div class="price">£23<small>/hr</small></div><p>Starting price for a 60-minute GCSE lesson. No subscription.</p><span class="card-cta">Enquire about GCSE</span></div></a></div><div class="col-sm-6"><a class="price-link" href="/contact.html"><div class="price-card featured"><div class="price-level">A-Level tutoring</div><div class="price">£28<small>/hr</small></div><p>Starting price for a 60-minute A-Level lesson. No subscription.</p><span class="card-cta">Enquire about A-Level</span></div></a></div></div></div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading center"><span class="eyebrow">Your first lesson</span><h2>Book the right tutor in three simple steps</h2><p>We do the matching work so you can focus on your child’s learning.</p></div><div class="row g-3"><div class="col-lg-4"><div class="step-row"><span class="step-number">1</span><div><h3>Tell us the subject and exam board</h3><p>Example: Year 10, GCSE Maths Higher Tier, AQA, algebra and graphs.</p></div></div></div><div class="col-lg-4"><div class="step-row"><span class="step-number">2</span><div><h3>Get suitable tutor options</h3><p>We discuss tutor expertise, availability and the exact hourly rate.</p></div></div></div><div class="col-lg-4"><div class="step-row"><span class="step-number">3</span><div><h3>Start learning with purpose</h3><p>Begin online, focused on the topics and goals that matter to the learner.</p></div></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row align-items-end mb-4 g-2"><div class="col-lg-8"><span class="eyebrow">North & West Northamptonshire</span><h2>Online tutoring in Northampton, Kettering, Corby and every corner of the county</h2><p class="text-secondary">From busy Northampton families to students in villages around Towcester, Oundle and Daventry, our online lessons are designed to remove the travel barrier. Wherever you live, access a wider UK tutor network.</p></div><div class="col-lg-4 text-lg-end">'''+button('See all Northamptonshire areas','/areas.html','outline-navy')+'''</div></div>'''+locations_grid()+'''<p class="text-secondary mt-3 mb-0 small">Also serving Oundle, Thrapston, Raunds, Rothwell, Desborough, Burton Latimer, Higham Ferrers, Irthlingborough, Earls Barton, Long Buckby, Silverstone, Brixworth and nearby villages online.</p></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Useful guides</span><h2>Revision advice for students across Northamptonshire</h2><p>Learn how to prepare for exams and get more from one-to-one tutoring.</p></div>'''+blog_cards(POSTS[:3])+'''<div class="mt-4 text-center">'''+button('Read more study guides','/blog.html','outline-navy')+'''</div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Frequently asked questions</span><h2>Online tutoring in Northamptonshire: subjects, pricing and how to start</h2><p class="text-secondary">We know choosing a tutor matters. Find the key answers before you contact us.</p>'''+button('Ask us about a tutor')+'''</div><div class="col-lg-7">'''+faqs(HOME_FAQS)+'''</div></div></div></section>'''
    body+=cta('The next step towards more confident learning starts here.','Tell us the student’s subject, year group, exam board and preferred times. Our team will discuss a suitable tutor, availability and prices with no obligation to book.')
    extra=[service_schema('Online school and exam tutoring in Northamptonshire','GCSE, A-Level, Primary and specialist online tutoring across Northamptonshire in Maths, Sciences, English, Humanities, Business, Computing, Languages and more.','/'),faq_schema(HOME_FAQS)]
    write('index.html',base('Northamptonshire Tutors | GCSE, A-Level & Online Tuition','Find online GCSE and A-Level tutors in Northamptonshire for Maths, Physics, English, Economics, Business, Languages and more. GCSE from £23/hr; A-Level from £28/hr.','/',body,extra))




def about():
    body=hero_page('About Northamptonshire Tutoring','A Northamptonshire-focused online tutoring service backed by North Wales Tutoring Group. We connect families with subject specialists, tailored lessons and practical support for the exam stage that matters.', [('About us',None)], 'Delivering a better future')
    body+='''<section class="section"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-6"><span class="eyebrow">What we do</span><h2>Delivering a better future, one student at a time</h2><p>One child might be losing confidence with fractions; another might be chasing top A-Level grades in Further Maths, Biology or Economics. Northamptonshire Tutoring helps families find a suitable online tutor who can teach the <strong>right material at the right pace</strong>.</p><p>We are part of <a href="https://nwttutoring.com/" rel="noopener" target="_blank">North Wales Tutoring Group</a>. That means families in Northamptonshire can draw on a much wider network of tutors across the UK rather than relying only on local availability.</p><p><strong>Our promise is a clear, honest process:</strong> tell us the subject, exam board and what needs work. We check suitable tutor options and tell you the price before you book. No subscription is required.</p>'''+button('Find my tutor')+'''</div><div class="col-lg-6"><div class="subject-feature-image"><img loading="lazy" src="/assets/images/online-tutoring.webp" width="800" height="800" alt="Student learning at home with the support of an online tutor"></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="section-heading center"><span class="eyebrow">Why families get in touch</span><h2>Support that starts with the student, not a sales package</h2></div><div class="row g-3"><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">01 / Subject match</span><h3>Specialist support, not generic lessons</h3><p>From GCSE Physics and English to A-Level Economics, French and Health &amp; Social Care, we check relevant teaching experience.</p></div></div><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">02 / Clear next steps</span><h3>Know what you are booking</h3><p>We discuss the tutor, subject, online format, hourly rate and available times before you commit.</p></div></div><div class="col-md-4"><div class="value-card card-soft"><span class="value-num">03 / Your schedule</span><h3>Learn from home</h3><p>Online teaching helps families throughout North and West Northamptonshire avoid travel after school.</p></div></div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-7"><span class="eyebrow">Subjects and exams</span><h2>A wide range of online GCSE, A-Level and school tutoring subjects</h2><p>Our subject options include Maths, Further Maths, Physics, Biology, Chemistry, Combined Science, English Language and Literature, Economics, Business, Computer Science, Geography, History, Religious Studies, Psychology, Sociology, French, Spanish, Chinese, Health &amp; Social Care and more. We also discuss SATs, 11+ and selected university or admissions preparation.</p><p>We match lessons to the <strong>actual course</strong>, including AQA, Pearson Edexcel, OCR, WJEC, Eduqas and Cambridge International where the right tutor is available.</p>'''+button('Explore all tutoring subjects','/subjects.html')+'''</div><div class="col-lg-5"><div class="area-panel"><h3>Northamptonshire towns we support</h3><p>One-to-one lessons online across North and West Northamptonshire:</p>'''+locations_grid()+'''</div></div></div></div></section>'''
    body+=cta('Give your child the support they need to move forward.','Tell us what they are studying and where they need more confidence. We will discuss tutors and next steps with you.')
    write('about.html',base('About Northamptonshire Tutoring | NWT Group Online Tutors','Northamptonshire Tutoring connects local families with online GCSE, A-Level and specialist tutors across the UK-backed North Wales Tutoring Group network.','/about.html',body,[crumb_schema([('About','/about.html')])]))




def service_page(s):
    slug=s['slug'];path='/'+slug+'.html';name=s['label']
    body=hero_page(s['h1'],s['intro'],[(name+' tutoring',None)],f'{name} · Online across Northamptonshire')
    body+=f'''<section class="section"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-7 service-content"><span class="eyebrow">A plan for real progress</span><h2>{E(s['outcome'])}</h2><p>{E(s['who'])}</p><p>{E(s['approach'])}</p><h3 class="fs-5 mt-4 mb-3">What your tutor can help with</h3><ul class="detail-list">'''+''.join(f'<li>{E(x)}</li>' for x in s['topics'])+f'''</ul><div class="note-panel mt-4"><strong>Exam boards and qualifications:</strong> {E(s['boards'])}</div><div class="mt-4">{button('Check '+name+' tutor availability')}</div></div><div class="col-lg-5"><div class="subject-feature-image"><img loading="lazy" src="/assets/images/{E(s['image'])}" width="800" height="800" alt="Personalised online {E(name)} lesson preparation"></div></div></div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-4 align-items-center"><div class="col-lg-7"><span class="eyebrow">Teaching matched to the learner</span><h2>From feeling stuck to knowing what to practise next</h2><p>Lessons are most useful when the tutor knows the student’s starting point. Share the year group, subject, awarding body, current grades or concerns, and any upcoming mocks or final assessments. We can then discuss a tutor who is familiar with the required content and can help structure the next steps.</p><p>Whether you are in Northampton, Corby, Kettering, Wellingborough, Rushden, Daventry, Towcester or Brackley, lessons are delivered online. There is no need to find a physical tutoring centre or travel after school.</p></div><div class="col-lg-5"><div class="area-panel"><h3>Why enquire today?</h3><ul><li><i class="bi bi-check-circle"></i> One-to-one support focused on your goals</li><li><i class="bi bi-check-circle"></i> Suitable exam-board and subject matching</li><li><i class="bi bi-check-circle"></i> Clear tutor and lesson pricing</li><li><i class="bi bi-check-circle"></i> No subscription or long-term commitment</li></ul><p class="mt-3 mb-0">{E(s['proof'])}</p></div></div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Available across the county</span><h2>'''+E(name)+''' tutors for Northampton and surrounding Northamptonshire towns</h2><p>Ask about one-to-one support from home throughout North and West Northamptonshire, including smaller towns and villages.</p></div>'''+locations_grid()+'''</div></section>'''
    fq=[(s['faq'],s['answer']),
       (f'Can I request a {name} tutor for my exam board?',f'Yes. Tell us the exact qualification and awarding body such as AQA, Edexcel, OCR, WJEC, Eduqas or Cambridge International. We will check which suitable tutors can support that specification.'),
       ('Are lessons one-to-one or in a physical centre?','Northamptonshire Tutoring provides online one-to-one tuition. Families can join from home in any Northamptonshire town or village.'),
       ('What does online tutoring cost?','GCSE tuition starts from £23 per hour and A-Level tuition starts from £28 per hour. Subject specialists or higher-experience tutors may charge more. Fees and availability are confirmed before booking.')]
    body+='''<section class="section section-soft"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Your questions answered</span><h2>'''+E(name)+''' tutoring FAQs</h2><p>We want you to know exactly how tutoring could help before you decide.</p>'''+button('Ask about '+name+' tutors')+'''</div><div class="col-lg-7">'''+faqs(fq)+'''</div></div></div></section>'''
    body+=cta('Ready for more confident '+name+' learning?',f'Tell us the learner’s year group, exam board and the specific {name} topics they need help with. We will check appropriate tutor options and lesson times.')
    description=s['intro']+' Online tuition serving Northampton, Kettering, Corby, Wellingborough and nearby towns.'
    write(slug+'.html',base(s['title'],description,path,body,[crumb_schema([(name+' tutoring',path)]),service_schema(name+' tuition for Northamptonshire students',s['intro'],path),faq_schema(fq)]))




def areas():
    body=hero_page('Online tutors across Northamptonshire towns and villages','Find Maths, Science, English, Humanities, Business, Economics, Languages, GCSE and A-Level online tutoring for families across North and West Northamptonshire. Study at home with UK-wide subject specialists.', [('Locations',None)])
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">North and West Northamptonshire</span><h2>Choose your Northamptonshire town to find online tutoring</h2><p>Every local page covers how our one-to-one tutoring supports families in that area, including nearby villages. Our service is fully online, not a physical tutoring centre.</p></div><div class="row g-3">'''
    for p in LOCATIONS:
        body+=f'''<div class="col-md-6 col-lg-4"><a class="town-card" href="/locations/{p['slug']}.html"><span class="value-num">{E(p['zone'])}</span><h3>{E(p['name'])} tutoring</h3><p>{E(p['benefit'])}</p><span class="card-cta">Explore {E(p['name'])} tutors</span></a></div>'''
    body+='''</div><div class="mt-5 area-panel"><h3>We also support families in smaller towns and villages</h3><p>Lessons can be joined online from Oundle, Thrapston, Raunds, Desborough, Rothwell, Burton Latimer, Higham Ferrers, Irthlingborough, Finedon, Earls Barton, Long Buckby, Silverstone, Brixworth, Roade, Moulton, Kislingbury and neighbouring communities across Northamptonshire.</p></div></div></section>'''
    body+=cta('No tutor near your village? Your options are bigger online.','Tell us the subject and year group. We will check tutors from the wider network who can teach online at a suitable time.')
    write('areas.html',base('Northamptonshire Online Tutors | Northampton, Corby, Kettering & More','Find online GCSE and A-Level tutors throughout Northamptonshire, including Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and Brackley.','/areas.html',body,[crumb_schema([('Locations','/areas.html')])]))




def location_page(p):
    name=p['name'];path='/locations/'+p['slug']+'.html'
    title='Online GCSE & A-Level tutors in '+name+', Northamptonshire'
    lead=f'Looking for a tutor in {name}? Access a wider network of online Maths, Physics, Chemistry, Biology, English, Economics, Business, Humanities and language tutors for KS3, GCSE and A-Level students living in {name} and nearby communities.'
    body=hero_page(title,lead,[('Locations','/areas.html'),(name,None)],'Online tutoring for '+p['zone'])
    body+=f'''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-7 area-content"><span class="eyebrow">Support for {E(name)} students</span><h2>Find online tutoring that follows your child’s subjects and exam board</h2><p>{E(p['specific'])}</p><p>{E(p['benefit'])}</p><p>Our team can discuss one-to-one tuition in <strong>Maths, Further Maths, Physics, Chemistry, Biology, Combined Science, English Language and Literature, Economics, Business, Computer Science, History, Geography, Psychology, Languages and more</strong>. The important thing is finding someone who understands the <strong>actual specification</strong>, whether AQA, Edexcel, OCR, WJEC, Eduqas or Cambridge International.</p><h3 class="fs-5 mt-4">Common tutoring enquiries around {E(name)}</h3><ul class="detail-list"><li>{E(p['focus'])}</li><li>Year 10 and Year 11 GCSE mock and final exam revision</li><li>KS3 topic gaps, homework confidence and A-Level subject understanding</li><li>English essays, language speaking practice and subject-specific exam technique</li></ul>{button('Find a tutor for '+name)}</div><div class="col-lg-5"><div class="area-panel"><h3>Tutoring near {E(name)}</h3><p>Our online tutoring is open to families in {E(name)} and neighbouring areas such as:</p><ul>'''+''.join(f'<li><i class="bi bi-geo-alt" aria-hidden="true"></i> {E(n)}</li>' for n in p['nearby'])+f'''</ul><p class="form-note mb-0">Online tutoring is delivered from home. We do not claim a physical teaching centre in {E(name)}.</p></div><div class="mt-3 subject-feature-image" style="min-height:220px;max-height:260px"><img src="/assets/images/study-session.webp" alt="Student preparing for online tutoring and exams" loading="lazy" width="960" height="600"></div></div></div></div></section>'''
    focus=[SUB_LOOKUP[x] for x in ['maths-tutoring-northamptonshire','physics-tutoring-northamptonshire','english-tutoring-northamptonshire','economics-tutoring-northamptonshire','science-tutoring-northamptonshire','languages-tutoring-northamptonshire']]
    body+='''<section class="section section-soft"><div class="container"><div class="section-heading"><span class="eyebrow">Choose your subject</span><h2>GCSE, A-Level, Maths, Physics and specialist tutoring in '''+E(name)+'''</h2><p>Choose the subject closest to what you need. If it's not listed, ask about the wider group network.</p></div>'''+subject_cards(focus)+'''<div class="text-center mt-4">'''+button('View all subjects','/subjects.html','outline-navy')+'''</div></div></section>'''
    fq=[(f'Can I book a GCSE tutor in {name}?',f'Yes. We offer online GCSE tutor matching for families in {name}, including Maths, Science, English, Business, Humanities and other subjects, subject to tutor availability.'),
        (f'Is tutoring in {name} online or face-to-face?','Lessons through Northamptonshire Tutoring are online and one-to-one. There is no advertised physical centre in this town.'),
        ('Do you cover AQA, Edexcel and OCR GCSE specifications?','We check the tutor’s suitability against your precise course and awarding body. Let us know the subject, board and Foundation/Higher tier where relevant.'),
        ('What are lesson prices for GCSE and A-Level?','GCSE online tutoring starts from £23 per hour and A-Level starts from £28 per hour. Some specialists cost more. We confirm the fee and availability before booking.')]
    body+='''<section class="section"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Local tutoring questions</span><h2>'''+E(name)+''' tutoring: FAQs</h2><p>Answers for parents and students looking for online tuition in this area.</p>'''+button('Ask for tutor options')+'''</div><div class="col-lg-7">'''+faqs(fq)+'''</div></div></div></section>'''
    body+=cta('Need a '+name+' tutor who understands the exact course?',f'Share the student’s year group, exam board, subjects and preferred times. We can check online tutor options for families in {name} and nearby villages.')
    write(path,base(f'{name} Tutors | Online GCSE & A-Level Northamptonshire',f'Find online GCSE, A-Level, Maths, Physics, Science, English and specialist tutors in {name}, Northamptonshire. GCSE from £23/hr; A-Level from £28/hr.',path,body,[crumb_schema([('Locations','/areas.html'),(name,path)]),service_schema('Online tutors for learners in '+name,lead,path,area=name+', Northamptonshire'),faq_schema(fq)]))




def contact():
    body=hero_page('Find your Northamptonshire tutor today','Tell us about the student, subject and exam board. We will discuss suitable online tutors for GCSE, A-Level, Primary, KS3, SATs, 11+, university or other specialist subjects.', [('Contact',None)], 'One enquiry, a clearer next step')
    body+='''<section class="section section-soft"><div class="container"><div class="contact-layout"><div><span class="eyebrow">Start here</span><h2>Get tutor options that actually match the student</h2><p class="text-secondary mb-4">No long form, no subscription and no obligation. Tell us the year group, exact subject, exam board and what your learner is struggling with. We help families throughout Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester, Brackley and the surrounding villages.</p><a class="contact-method" href="mailto:northamptonshire@nwttutoring.com"><i class="bi bi-envelope" aria-hidden="true"></i><span><strong>Email Northamptonshire Tutoring</strong><span>northamptonshire@nwttutoring.com</span></span></a><a class="contact-method" href="https://wa.me/447480231362?text=Hi%2C%20I%27m%20looking%20for%20an%20online%20tutor%20in%20Northamptonshire."><i class="bi bi-whatsapp" aria-hidden="true"></i><span><strong>Message us on WhatsApp</strong><span>+44 7480 231362</span></span></a><div class="area-panel mt-4"><h3>Include these details in your message</h3><ul><li><i class="bi bi-check-circle"></i> Student year group (for example, Year 10)</li><li><i class="bi bi-check-circle"></i> Course (GCSE, A-Level, SATs, 11+ etc.)</li><li><i class="bi bi-check-circle"></i> Subject, exam board and tier if relevant</li><li><i class="bi bi-check-circle"></i> Topics, goals and preferred lesson times</li></ul></div></div><div>'''+form('contact-enquiry','New Northamptonshire Tutoring contact enquiry')+'''</div></div></div></section>'''
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">What happens next?</span><h2>A straightforward path to your first lesson</h2><p>Our team reviews what you need and checks suitable tutor options, costs and availability with you.</p></div><div class="row g-3"><div class="col-md-4"><div class="step-row"><span class="step-number">1</span><div><h3>Send the short enquiry</h3><p>Name, email, phone and a message about the student.</p></div></div></div><div class="col-md-4"><div class="step-row"><span class="step-number">2</span><div><h3>Discuss available tutors</h3><p>Subject expertise, lesson times and price are confirmed before booking.</p></div></div></div><div class="col-md-4"><div class="step-row"><span class="step-number">3</span><div><h3>Begin learning online</h3><p>Start with lessons focused on the topics that need attention.</p></div></div></div></div></div></section>'''
    write('contact.html',base('Contact Northamptonshire Tutoring | Find a GCSE or A-Level Tutor','Enquire about GCSE or A-Level tutoring in Northamptonshire for Maths, Physics, English, Economics and more. Email northamptonshire@nwttutoring.com.','/contact.html',body,[crumb_schema([('Contact','/contact.html')])]))




def blog_index():
    body=hero_page('GCSE, A-Level and subject revision advice for Northamptonshire','Practical guidance for parents and students on exam preparation, GCSE Maths and Physics, A-Level study habits and choosing the right tutor.',[('Blog',None)],'Revision and tutoring resources')
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Practical subject advice</span><h2>Revision guides, study habits and online tutoring advice</h2><p>Use these guides alongside school teaching and one-to-one tutoring. Need help in English, Economics, Biology or another subject? See our full range of tutoring subjects.</p></div>'''+blog_cards(POSTS)+'''<div class="mt-4 text-center">'''+button('See all subject support','/subjects.html','outline-navy')+'''</div></div></section>'''
    body+=cta('Need more than a revision guide?','If your child needs help turning practice into confident exam answers, tell us the subject and stage. We will discuss appropriate online tuition.')
    write('blog.html',base('Northamptonshire Tutoring Blog | GCSE & A-Level Revision','Read GCSE and A-Level study guides and tutoring advice for Northamptonshire families. Revision, Maths, Physics and online tutor matching.','/blog.html',body,[crumb_schema([('Blog','/blog.html')])]))




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
    cookies+='''<section class="section"><div class="container legal-content"><p><strong>Last reviewed:</strong> 11 November 2026</p><h2>How our cookie choices work</h2><p>Our website stores your cookie-banner preference in your browser under the key <code>northamptonshire_tutoring_cookie_choice_v1</code>. This stops the banner displaying every time you move to another page. This is local browser storage, rather than a tracking cookie.</p><h2>Optional analytics and marketing</h2><p>At initial launch, the supplied website does not load Google Analytics, Meta Pixel or advertising trackers. Our banner provides accept and reject options in case consent-controlled services are added later; choosing “Accept optional” does not itself activate tracking on this version of the site. Any future non-essential tracking should be held back unless consent has been given and this policy is updated.</p><h2>External services</h2><p>We load fonts, Bootstrap Icons and the SweetAlert2 confirmation library from external providers. Using the contact form sends your enquiry to Web3Forms. These services may process technical data according to their own policies. We do not set advertising cookies through the supplied website code.</p><h2>Change your choice</h2><p>You can reset your selection by removing this site's local storage in your browser settings, then refresh the page. The banner will appear again.</p><h2>Contact</h2><p>Email <a href="mailto:northamptonshire@nwttutoring.com">northamptonshire@nwttutoring.com</a> with questions about the website's privacy practices.</p></div></section>'''
    write('cookie-policy.html',base('Cookie Policy | Northamptonshire Tutoring','Read the Northamptonshire Tutoring cookie policy, including cookie consent choices, browser storage and external services.','/cookie-policy.html',cookies,[crumb_schema([('Cookie policy','/cookie-policy.html')])]))


def search_files():
    urls=['/','/about.html','/areas.html','/subjects.html','/tutors.html','/contact.html','/blog.html','/privacy.html','/cookie-policy.html']
    urls += ['/'+p['slug']+'.html' for p in SUBJECTS]
    urls += ['/locations/'+p['slug']+'.html' for p in LOCATIONS]
    urls += ['/blog/'+p['slug']+'.html' for p in POSTS]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path in urls:sitemap+=f'<url><loc>{DOMAIN+path}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n'
    sitemap+='</urlset>\n'
    write('sitemap.xml',sitemap)
    write('robots.txt',f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')




def tutor_cards(profiles):
    out=['<div class="row g-3">']
    for p in profiles:
        img=(f'<img loading="lazy" width="600" height="600" src="/assets/images/tutors/{E(p["image"])}" alt="{E(p["name"])} from the NWT Group tutor network">' if p.get('image') else f'<div class="tutor-avatar" aria-hidden="true">{E(p["initials"])}</div>')
        href='/contact.html?tutor='+quote(p['name'],safe='')
        out.append(f'''<div class="col-12 col-sm-6 col-lg-4 col-xl-3"><a class="tutor-card card-soft" href="{href}" aria-label="Ask our team about {E(p['name'])}"><div class="tutor-photo">{img}</div><div class="tutor-info"><span class="tutor-chip">{E(p['level'])}</span><h3>{E(p['name'])}</h3><div class="tutor-subject">{E(p['subjects'])}</div><p>{E(p['summary'])}</p><span class="card-cta">Ask about {E(p['name'])}</span></div></a></div>''')
    return ''.join(out)+'</div>'




def subjects_page():
    body=hero_page('All online tutoring subjects in Northamptonshire','Find one-to-one online tutors for Maths, Physics, Chemistry, Biology, English, Further Maths, Economics, Business, Computer Science, History, Geography, Languages, Psychology, vocational qualifications and more.', [('Subjects',None)], '18 subject and exam pathways')
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Find the exact subject</span><h2>Maths and Physics specialists, English tutors and a full range of GCSE and A-Level subjects</h2><p>Not every learner needs the same help. Select the subject or stage below for the topics, qualifications and exam boards we can discuss. The group network offers a wider range of tutors than a single school or local tutoring centre.</p></div>'''+subject_cards()+'''</div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-5"><div class="col-lg-7"><span class="eyebrow">More subjects by request</span><h2>Can't see the exact course on this page?</h2><p>Our wider UK tutor network also covers Religious Studies, Art &amp; Design, Media &amp; Film, Politics, Sociology, Chinese, Welsh, ESOL, Functional Skills, Child Development, Childcare, Travel &amp; Tourism, university Maths and selected vocational qualifications. Ask us about the particular specification rather than assuming a subject isn't available.</p><p><strong>Exams and courses:</strong> AQA, Pearson Edexcel, OCR, WJEC, Eduqas, Cambridge International, selected BTEC courses, SATs, 11+, 13+, TMUA and UCAT, subject to a suitable specialist.</p>'''+button('Check my subject and tutor options')+'''</div><div class="col-lg-5"><div class="area-panel"><h3>What to include in your enquiry</h3><ul><li><i class="bi bi-check-circle"></i> Student year group / qualification</li><li><i class="bi bi-check-circle"></i> Subject and exam board</li><li><i class="bi bi-check-circle"></i> Foundation or Higher tier if relevant</li><li><i class="bi bi-check-circle"></i> Difficult topics and upcoming exams</li><li><i class="bi bi-check-circle"></i> Days and times that work for you</li></ul></div></div></div></div></section>'''
    body+=cta('One short enquiry. A more suitable tutor match.','Tell us exactly what your child studies, even if it is an unusual subject or vocational unit. We will check whether an appropriate tutor has availability.')
    write('subjects.html',base('All Tutoring Subjects Northamptonshire | GCSE & A-Level Tutors','Online tutors in Northamptonshire for GCSE, A-Level, Maths, Physics, Biology, Chemistry, English, Economics, Business, Computer Science, Humanities and Languages.','/subjects.html',body,[crumb_schema([('Subjects','/subjects.html')])]))




def tutors_page():
    body=hero_page('Meet our online tutoring team for Northamptonshire students','Find experienced Maths, Science, English, Business, Economics, Languages, Humanities and vocational tutors from the wider North Wales Tutoring Group network. Ask us to check suitability and live availability.', [('Tutors',None)], 'A wider team, more options')
    body+='''<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Meet the group network</span><h2>Find the tutor who suits the subject and the student</h2><p>These are selected tutors listed on the parent company’s current public directory, covering a wide choice of subjects, age groups and teaching approaches. Profiles here are simple cards, not individual profile pages. We confirm tutor availability, exact rates and suitability before discussing a booking.</p></div>'''+tutor_cards(TUTORS)+'''<div class="note-panel mt-4">Some tutors may already be fully booked or unable to take a particular time slot. We will never treat a displayed card as a guaranteed booking or a promise of a particular lesson rate.</div></div></section>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-7"><span class="eyebrow">Personal tutor matching</span><h2>Don't see a tutor or subject that fits?</h2><p>Let us do the search. Tell us the subject, year group, exam board, any tutor preferences and when lessons would fit your week. We can check other tutors across the wider group, including Maths, Further Maths, Science, English, Economics, Business, Languages, Humanities and vocational specialists.</p>'''+button('Request a personalised tutor match')+'''</div><div class="col-lg-5"><div class="subject-feature-image"><img src="/assets/images/online-tutoring.webp" alt="Personalised online teaching session" loading="lazy" width="800" height="800"></div></div></div></div></section>'''
    body+=cta('The right teaching approach can make all the difference.','Ask our team about a tutor, subject, lesson price or learning goal. We will discuss availability without any obligation to proceed.')
    write('tutors.html',base('Online Tutors Northamptonshire | Maths, English, Science & More','Browse selected NWT Group tutors for Northamptonshire students: Maths, Physics, Biology, Chemistry, English, Economics, Business, Languages and more.','/tutors.html',body,[crumb_schema([('Tutors','/tutors.html')])]))




def main():
    home();about();areas();subjects_page();tutors_page();contact();blog_index()
    for s in SUBJECTS:service_page(s)
    for p in LOCATIONS:location_page(p)
    for p in POSTS:blog_article(p)
    legal();search_files()
    print('Build complete:',len(list(ROOT.rglob('*.html'))),'HTML files (including shared components / article sources).')



if __name__=="__main__":
    main()
