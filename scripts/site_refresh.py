#!/usr/bin/env python3
"""Brand refresh, accessible navigation, safeguarding and unique editorial page treatments.
Run after scripts/build.py; no third-party Python dependencies.
This also upgrades existing retained specialist pages without erasing them.
"""
from pathlib import Path
from urllib.parse import quote
from html import escape as E
import json, re, sys, hashlib
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import base, write, crumb_schema, faq_schema, service_schema, DOMAIN
SITE=json.loads((ROOT/'data/site.json').read_text())
LOCATIONS=json.loads((ROOT/'data/locations.json').read_text())
SUBJECTS=json.loads((ROOT/'data/subjects.json').read_text())
REVIEWS=json.loads((ROOT/'data/testimonials.json').read_text(encoding='utf-8'))
PARENT_SUBJECTS={
 'Maths & science': ['Maths','Further Maths','Biology','Chemistry','Physics','Combined Science','Computer Science'],
 'English & languages':['English Language','English Literature','Welsh','French','Spanish','Chinese','Modern Foreign Languages','ESOL / EFL'],
 'Humanities & social sciences':['History','Geography','Religious Studies','Philosophy & Ethics','Psychology','Sociology','Politics','Economics','Business Studies'],
 'Creative & vocational':['Art & Design','Media & Film','Health & Social Care','Childcare','Child Development','Travel & Tourism','Functional Skills'],
 'Primary & advanced':['Primary Maths','Primary English','University Maths','International Baccalaureate (IB)','Advanced Placement (AP)','Professional qualifications']
}
EXAMS=[('Year 6 SATs','sats'),('11 Plus','11-plus'),('13 Plus','13-plus'),('GCSE','gcse'),('A-Level','a-level'),('UCAT','ucat'),('TMUA','tmua'),('GMAT','gmat'),('IB & AP','ib-ap'),('Functional Skills','functional-skills')]
EXAM_CONTENT={
'sats':('Year 6 SATs tutoring','Year 6 SATs Maths, Reading and Grammar preparation','Give your Year 6 child targeted online help with arithmetic, problem-solving, reading comprehension and grammar before their KS2 assessments.','KS2 Mathematics and English','Arithmetic fluency, reasoning, reading, spelling and grammar','Year 6 pupils across Northamptonshire preparing for national curriculum assessments'),
'11-plus':('11 Plus exam preparation','Online 11+ and school entrance exam tutoring','Prepare for your child’s school entrance assessment with structured online tuition in Maths, English, verbal and non-verbal reasoning where relevant to the chosen school.','School-specific entrance assessment','Problem solving, comprehension, verbal and non-verbal reasoning','Year 5 and Year 6 pupils preparing for selective or independent school entrance'),
'13-plus':('13 Plus entrance exam preparation','Online 13+ Common Entrance and scholarship preparation','Support your child with 13+ entrance assessments, analytical writing and problem-solving by checking subject specialists who know the required entry route.','School-specific 13+ assessment','Maths, English, science and reasoning as required by the school','Pupils preparing for independent-school entrance at age 13'),
'gcse':('GCSE exam preparation','GCSE Maths, English, Science and more','Turn revision into a clear, subject-specific plan. Our online GCSE tutors work through specification topics, timed papers, examiner-style answers and GCSE mock exam feedback.','AQA, Edexcel, OCR, Eduqas, WJEC, CAIE','Foundation and Higher Maths, English Language, Biology, Chemistry, Physics, Humanities, Languages and more','Year 10 and Year 11 GCSE pupils, including resit learners'),
'a-level':('A-Level exam preparation','A-Level exam preparation for Year 12 and Year 13','Study demanding sixth-form topics with one-to-one help in A-Level Maths, Physics, Chemistry, Biology, Economics, English, Politics and other subjects, subject to specialist availability.','AQA, Edexcel, OCR, WJEC, Eduqas, CAIE','Pure Maths, Mechanics, Sciences, essays, data analysis, past-paper practice and revision strategy','Year 12, Year 13 and A-Level resit students'),
'ucat':('UCAT exam preparation','UCAT tutoring for aspiring medical and dental students','Get individual support with UCAT question technique, pace, timed practice, decision making and situational judgement using current examination information.','University Clinical Aptitude Test (UCAT)','Verbal reasoning, decision making, quantitative reasoning and situational judgement','Prospective medicine and dentistry applicants'),
 'tmua':('TMUA exam preparation','TMUA Maths admissions test tutoring','Strengthen mathematical reasoning, algebra, proof-style thinking and problem-solving for the TMUA through tailored admissions-test practice.','Test of Mathematics for University Admission (TMUA)','Mathematical reasoning, multi-step problems, accuracy and time management','Applicants to courses requiring or accepting the TMUA'),
 'gmat':('GMAT exam preparation','GMAT exam skills and quantitative tutoring','Ask about advanced quantitative and verbal reasoning support for GMAT preparation, tailored to your starting point and timetable.','Graduate Management Admission Test (GMAT)','Quantitative reasoning, data insights, verbal reasoning and timed strategy','Applicants to business and management postgraduate courses'),
'ib-ap':('IB and AP tutoring','International Baccalaureate and Advanced Placement support','Ask us about one-to-one IB and AP tutoring across Maths, Sciences, Humanities and languages, subject to current tutor expertise and course level.','IB Diploma and Advanced Placement','IB Higher and Standard Level, AP subjects, assessments and problem-solving','Students studying international qualifications from Northamptonshire'),
 'functional-skills':('Functional Skills tutoring','English and Maths Functional Skills exam preparation','Build confidence in practical English and Maths for Functional Skills qualifications, work and further study, with individually paced lessons.','Functional Skills English and Maths','Everyday numeracy, fractions, percentages, reading, writing and applied problems','School leavers, vocational learners and adults')}
SUBJECT_ROUTES={
'Maths':'/maths-tutoring-northamptonshire.html','Further Maths':'/further-maths-tutoring-northamptonshire.html',
'Biology':'/biology-tutoring-northamptonshire.html','Chemistry':'/chemistry-tutoring-northamptonshire.html',
'Physics':'/physics-tutoring-northamptonshire.html','Combined Science':'/science-tutoring-northamptonshire.html',
'Computer Science':'/computer-science-tutoring-northamptonshire.html','Business Studies':'/business-tutoring-northamptonshire.html',
'Economics':'/economics-tutoring-northamptonshire.html','Psychology':'/psychology-sociology-tutoring-northamptonshire.html',
'Sociology':'/psychology-sociology-tutoring-northamptonshire.html',
'Health & Social Care':'/health-social-care-tutoring-northamptonshire.html',
'English Language':'/english-tutoring-northamptonshire.html','English Literature':'/english-tutoring-northamptonshire.html',
'Welsh':'/languages-tutoring-northamptonshire.html','French':'/languages-tutoring-northamptonshire.html',
'Spanish':'/languages-tutoring-northamptonshire.html','Chinese':'/languages-tutoring-northamptonshire.html',
'Modern Foreign Languages':'/languages-tutoring-northamptonshire.html','ESOL / EFL':'/languages-tutoring-northamptonshire.html',
'History':'/humanities-tutoring-northamptonshire.html','Geography':'/humanities-tutoring-northamptonshire.html',
'Politics':'/politics-tutoring-northamptonshire.html','Primary Maths':'/primary-tutoring-northamptonshire.html',
'Primary English':'/primary-tutoring-northamptonshire.html','University Maths':'/maths-tutoring-northamptonshire.html',
'Functional Skills':'/exam/functional-skills.html',
'International Baccalaureate (IB)':'/exam/ib-ap.html', 'Advanced Placement (AP)':'/exam/ib-ap.html',
}
def wa_message(context='tutoring'):
    return 'https://wa.me/447480231362?text='+quote(f"Hi Northamptonshire Tutoring, I'd like to enquire about {context}. Could you help me find a suitable online tutor?",safe='')

def nav_html():
    groups=[]
    for group,names in PARENT_SUBJECTS.items():
        links=''.join(f'<li><a class="dropdown-item" href="{E(SUBJECT_ROUTES.get(n,"/subjects.html#"+slugify(n)))}">{E(n)}</a></li>' for n in names)
        groups.append(f'<li class="mega-group"><span class="mega-label">{E(group)}</span><ul>{links}</ul></li>')
    exams=''.join(f'<li><a class="dropdown-item" href="/exam/{slug}.html">{E(title)}</a></li>' for title,slug in EXAMS)
    return '''<a class="skip-link" href="#main-content">Skip to main content</a>
<div class="utility-bar"><div class="container utility-inner"><span><i class="bi bi-stars" aria-hidden="true"></i> Delivering a better future <span class="utility-separator">·</span> Part of <a href="https://nwttutoring.com/" target="_blank" rel="noopener">North Wales Tutoring Group</a></span><a class="utility-contact" href="'''+wa_message()+'''" target="_blank" rel="noopener"><i class="bi bi-whatsapp" aria-hidden="true"></i> +44 7480 231362</a></div></div>
<header class="site-header" id="site-header"><nav class="navbar navbar-expand-lg navbar-light container nav-shell" aria-label="Main navigation"><a class="navbar-brand brand" href="/" aria-label="Northamptonshire Tutoring home"><span class="brand-crest"><img src="/assets/images/nwt-group-mark.png" alt="" width="51" height="51"></span><span class="brand-text"><strong>Northamptonshire</strong><small>TUTORING <span class="brand-pink">•</span> NWT GROUP</small></span></a><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#primaryNavigation" aria-controls="primaryNavigation" aria-expanded="false" aria-label="Open navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="primaryNavigation"><ul class="navbar-nav ms-auto align-items-lg-center"><li class="nav-item"><a class="nav-link" href="/">Home</a></li><li class="nav-item"><a class="nav-link" href="/about.html">About us</a></li>
<li class="nav-item dropdown nav-mega"><button class="nav-link dropdown-toggle border-0 bg-transparent" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-controls="subjectMenu">All subjects</button><div id="subjectMenu" class="dropdown-menu mega-menu"><div class="mega-heading"><strong>Explore tutoring subjects</strong><a class="btn btn-pink btn-sm" href="/subjects.html">View all subjects</a></div><div class="mega-columns"><ul class="mega-categories">'''+''.join(groups)+'''</ul></div></div></li>
<li class="nav-item dropdown"><button class="nav-link dropdown-toggle border-0 bg-transparent" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-controls="examMenu">Exam preparation</button><ul class="dropdown-menu exam-menu" id="examMenu"><li><a class="dropdown-item fw-bold" href="/exam-preparation.html">All exam preparation</a></li><li><hr class="dropdown-divider"></li>'''+exams+'''</ul></li>
<li class="nav-item"><a class="nav-link" href="/tutors.html">Our tutors</a></li><li class="nav-item"><a class="nav-link" href="/blog.html">Blog</a></li><li class="nav-item ms-lg-3"><a class="btn btn-pink nav-cta" href="/contact.html">Find a tutor</a></li></ul></div></nav></header>'''

def slugify(s):return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

def footer_html():
    top_links=[('All tutoring subjects','/subjects.html'),('Our tutor network','/tutors.html'),('Maths tutors','/maths-tutoring-northamptonshire.html'),('Physics tutors','/physics-tutoring-northamptonshire.html'),('English tutors','/english-tutoring-northamptonshire.html'),('Biology tutors','/biology-tutoring-northamptonshire.html'),('Chemistry tutors','/chemistry-tutoring-northamptonshire.html'),('History and Geography','/humanities-tutoring-northamptonshire.html')]
    more_links=[('Exam preparation','/exam-preparation.html'),('Year 6 SATs','/exam/sats.html'),('11 Plus & 13 Plus','/exam/11-plus.html'),('GCSE exam preparation','/exam/gcse.html'),('A-Level exam preparation','/exam/a-level.html'),('UCAT preparation','/exam/ucat.html'),('TMUA preparation','/exam/tmua.html'),('Northamptonshire locations','/areas.html')]
    def links(x):return ''.join(f'<li><a href="{path}">{E(name)}</a></li>' for name,path in x)
    return f'''<footer class="site-footer" id="site-footer"><div class="container"><div class="footer-top"><div class="footer-brand-column"><a href="/" class="footer-logo-link crest-logo-link" aria-label="Northamptonshire Tutoring home"><img class="footer-group-logo" src="/assets/images/nwt-group-crest-2026.jpg" width="176" height="176" loading="lazy" alt="North Wales Tutoring Group NWT crest in navy, pink, purple and gold"></a><h2>Northamptonshire Tutoring</h2><p class="footer-description"><strong>Online one-to-one tutoring across Northamptonshire</strong> for Primary, SATs, 11+, 13+, GCSE and A-Level students. Find specialist support in <strong>Maths, Further Maths, Physics, Chemistry, Biology, English, Computer Science, Economics, Business, History, Geography, Languages, Psychology, Sociology</strong> and more. Supporting learners in <strong>Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester, Brackley</strong> and surrounding towns. Exam-board support includes <strong>AQA, Pearson Edexcel, OCR, WJEC, Eduqas and Cambridge International</strong>, subject to the learner’s course and tutor availability.</p><p class="footer-motto">Delivering a better future.</p><div class="footer-social"><a href="{E(SITE['facebook'])}" aria-label="Facebook" target="_blank" rel="noopener"><i class="bi bi-facebook" aria-hidden="true"></i></a><a href="{E(SITE['instagram'])}" aria-label="Instagram" target="_blank" rel="noopener"><i class="bi bi-instagram" aria-hidden="true"></i></a></div></div><div><h3>Tutoring subjects</h3><ul>{links(top_links)}</ul></div><div><h3>Exam support</h3><ul>{links(more_links)}</ul></div><div><h3>Contact &amp; safeguarding</h3><ul class="footer-contacts"><li><i class="bi bi-envelope" aria-hidden="true"></i><a href="mailto:northamptonshire@nwttutoring.com">northamptonshire@nwttutoring.com</a></li><li><i class="bi bi-whatsapp" aria-hidden="true"></i><a href="{wa_message()}">+44 7480 231362</a></li><li><i class="bi bi-shield-check" aria-hidden="true"></i><a href="/safeguarding.html">Safeguarding &amp; child protection policy</a></li><li><i class="bi bi-envelope-exclamation" aria-hidden="true"></i><a href="mailto:safeguarding@nwttutoring.com">safeguarding@nwttutoring.com</a></li></ul><a href="/contact.html" class="btn btn-pink footer-button">Enquire about lessons</a></div></div><div class="footer-bottom"><p>© <span data-year>2026</span> Northamptonshire Tutoring. Part of <a href="https://nwttutoring.com/" target="_blank" rel="noopener">North Wales Tutoring Group</a>. All rights reserved.</p><p>Website designed with <span class="heart" aria-label="love">💗</span> by <a href="https://cleandesignuk.com/" target="_blank" rel="noopener">Clean Design UK</a>.</p><div class="legal-links"><a href="/safeguarding.html">Safeguarding</a><a href="/privacy.html">Privacy</a><a href="/cookie-policy.html">Cookies</a></div></div></div></footer>'''

def subject_directory_page(tutor_network=False):
    destination='/tutors.html' if tutor_network else '/subjects.html'
    title=('Find online tutors for every subject in Northamptonshire' if tutor_network else 'Online tutoring subjects in Northamptonshire')
    desc=('Explore the full North Wales Tutoring Group subject network: Maths, Physics, English, Sciences, Business, Computer Science, History, Geography, Psychology, languages, creative and vocational subjects. Subject availability is confirmed when you enquire.' if tutor_network else 'Explore all Northamptonshire online tutoring subjects, from Maths, Physics, Sciences, English and Humanities to Business, languages, Computer Science, Art & Design and vocational qualifications.')
    intro='From Year 6 SATs and GCSEs through to A-Levels, vocational courses and university preparation, we help families enquire about the right subject specialist. Current tutors and availability vary, so we check before confirming a match.'
    cards=''
    for i,(group,names) in enumerate(PARENT_SUBJECTS.items()):
        cards+=f'<section class="directory-category" id="{slugify(group)}"><div class="directory-category-heading"><span class="directory-count">{str(i+1).zfill(2)}</span><div><span class="eyebrow">Subject specialists</span><h2>{E(group)}</h2></div></div><div class="directory-list">'
        for n in names:
            href=SUBJECT_ROUTES.get(n,'/contact.html')
            anchor=slugify(n)
            cards+=f'<a class="directory-subject" href="{href}" id="{anchor}"><strong>{E(n)}</strong><span>Explore tutoring</span></a>'
        cards+='</div></section>'
    head=f'''<section class="page-hero directory-hero"><div class="container"><nav class="breadcrumb-custom" aria-label="Breadcrumb"><a href="/">Home</a> / {E('Our tutors' if tutor_network else 'Subjects')}</nav><span class="eyebrow">Subjects &amp; tutor matching</span><h1>{E(title)}</h1><p>{E(intro)}</p><div class="hero-actions d-flex flex-wrap gap-2"><a class="btn btn-pink" href="/contact.html">Enquire about a subject</a><a class="btn btn-outline-navy" href="/exam-preparation.html">Explore exam preparation</a></div></div></section>'''
    body=head+f'''<section class="section directory-introduction"><div class="container"><div class="directory-intro"><span class="eyebrow">Learning support beyond the core subjects</span><h2>Every learner is different. Your tutoring options should be too.</h2><p>{E(desc)}</p><div class="directory-intro-meta"><strong>{sum(map(len,PARENT_SUBJECTS.values()))}+ subject options</strong><span>AQA · Edexcel · OCR · WJEC · Eduqas · CAIE</span></div></div></div></section><div class="container directory-sections">{cards}</div>'''
    body+='''<section class="section section-soft"><div class="container"><div class="row g-4 align-items-center"><div class="col-lg-7"><span class="eyebrow">Not sure where to start?</span><h2>Tell us your course and we’ll check the right tutor.</h2><p>Send the subject, qualification, exam board, topics and your preferred lesson times. We will confirm who is currently available before you make any booking.</p></div><div class="col-lg-5 text-lg-end"><a class="btn btn-pink" href="/contact.html">Request my tutor match</a></div></div></div></section>'''
    write(destination,base(('Our Online Tutors | 35+ Subjects in Northamptonshire' if tutor_network else 'Tutoring Subjects Northamptonshire | GCSE, A-Level & More'),desc,destination,body,[crumb_schema([('Our tutors' if tutor_network else 'All subjects',destination)])]))


def exam_pages():
    cards=''.join(f'<a class="exam-tile" href="/exam/{slug}.html"><span>{i+1:02d} / Exam preparation</span><h3>{E(name)}</h3><p>{E(EXAM_CONTENT[slug][1])}</p><strong>Explore preparation</strong></a>' for i,(name,slug) in enumerate(EXAMS))
    body='''<section class="page-hero exam-overview-hero"><div class="container"><nav class="breadcrumb-custom"><a href="/">Home</a> / Exam preparation</nav><span class="eyebrow">From SATs to university admissions</span><h1>Exam preparation tutors in Northamptonshire</h1><p>Find structured one-to-one exam support for Year 6 SATs, 11+, 13+, GCSE, A-Level, UCAT, TMUA, GMAT, Functional Skills and international qualifications. Tell us your exam and we'll check current specialist availability.</p><div class="hero-actions"><a href="/contact.html" class="btn btn-pink">Discuss exam preparation</a></div></div></section>'''
    body+=f'<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">Choose your qualification</span><h2>Prepare for the exam your child is actually sitting</h2><p>Focused exam practice, course-specific questions and a tutor match based on the right qualification and level.</p></div><div class="exam-card-grid">{cards}</div></div></section>'
    body+='''<section class="section section-soft"><div class="container"><div class="row g-4"><div class="col-lg-6"><h2>Practice with purpose. Build confidence for exam day.</h2><p>A good tutor starts with the paper you will sit, the concepts you find difficult and a realistic revision plan. We discuss exam boards and specialist availability before arranging lessons.</p></div><div class="col-lg-6"><div class="exam-note"><strong>School and admissions exams</strong><p>Some entrance tests are school- or provider-specific. We will ask about the exact assessment before confirming whether we have a suitable tutor.</p><a class="btn btn-pink" href="/contact.html">Enquire now</a></div></div></div></div></section>'''
    write('exam-preparation.html',base('Exam Preparation Tutors Northamptonshire | SATs, GCSE, A-Level, UCAT & TMUA','Find online tutors for Year 6 SATs, 11 Plus, 13 Plus, GCSE, A-Level, UCAT, TMUA, GMAT, Functional Skills and IB/AP across Northamptonshire.','/exam-preparation.html',body,[crumb_schema([('Exam preparation','/exam-preparation.html')]),service_schema('Online exam preparation in Northamptonshire','One-to-one online tuition for UK school, entrance, admission and vocational assessments.','/exam-preparation.html')]))
    for i,(name,slug) in enumerate(EXAMS):
        heading,subtitle,opening,spec,topics,forwhom=EXAM_CONTENT[slug]
        path='/exam/'+slug+'.html'
        markers=''.join(f'<span class="exam-marker">{E(x.strip())}</span>' for x in topics.split(','))
        sectiontype=i%4
        faq=[(f'Can I arrange {name} tutoring online in Northamptonshire?',f'You can enquire about {name} preparation and we will check tutor expertise and availability before offering a lesson.'),(f'What should I share about the {name} exam?',f'Please tell us the year group, exact assessment or syllabus, topics of concern, target date and preferred lesson times.'),(f'How are {name} lessons organised?','Lessons can be scheduled as personalised one-to-one online sessions. The approach depends on the student, assessment and tutor available.')]
        body=f'''<section class="page-hero exam-single-hero"><div class="container"><nav class="breadcrumb-custom"><a href="/">Home</a> / <a href="/exam-preparation.html">Exam preparation</a> / {E(name)}</nav><span class="eyebrow">Online exam tutoring in Northamptonshire</span><h1>{E(heading)} for Northamptonshire students</h1><p>{E(opening)}</p><div class="hero-actions d-flex gap-2 flex-wrap"><a class="btn btn-pink" href="/contact.html">Find an exam tutor</a><a class="btn btn-outline-navy" href="{wa_message(name+' preparation')}">Ask us on WhatsApp</a></div></div></section>'''
        body+=f'''<section class="section exam-detail-section"><div class="container"><div class="exam-layout exam-layout-{sectiontype}"><div class="exam-detail-main"><span class="eyebrow">{E(subtitle)}</span><h2>Preparation built around the assessment, not a generic worksheet</h2><p>{E(forwhom)}. Our online tutoring connects learners in Northampton, Kettering, Corby, Wellingborough, Rushden, Daventry, Towcester and Brackley with subject-specialist tutors.</p><p>We tailor the discussion to the specific examination provider, school, syllabus or qualification where relevant, rather than assuming every course follows the same assessment format.</p><div class="marker-list">{markers}</div></div><aside class="exam-detail-aside"><span class="exam-aside-number">{i+1:02d}</span><h3>Assessment focus</h3><p>{E(spec)}</p><strong>Subject coverage depends on current tutor availability.</strong><a href="/contact.html" class="btn btn-pink mt-3">Ask about {E(name)}</a></aside></div></div></section>'''
        body+=f'''<section class="section section-soft"><div class="container"><div class="row g-4 align-items-center"><div class="col-lg-6"><span class="eyebrow">Your next steps</span><h2>From uncertainty to a practical revision plan</h2><p>Tell us your assessment date, strongest and weakest topics, and preferred lesson times. We check current tutor options and explain the next steps before booking.</p><a class="btn btn-pink" href="/contact.html">Start an enquiry</a></div><div class="col-lg-6"><div class="faq-list">{''.join(f'<details class="faq-item"><summary>{E(q)}</summary><div class="faq-answer">{E(a)}</div></details>' for q,a in faq)}</div></div></div></div></section>'''
        write(path,base(f'{heading} Northamptonshire | One-to-One Online Tutors',f'{subtitle} for families across Northampton, Corby, Kettering, Wellingborough and all Northamptonshire. Online one-to-one tutor matching and exam-focused lessons.',path,body,[crumb_schema([('Exam preparation','/exam-preparation.html'),(name,path)]),service_schema(heading,opening,path),faq_schema(faq)]))


def safeguarding_page():
    mail='safeguarding@nwttutoring.com'; key='0bb361ee-84d0-4601-b054-8ef15ab30645'
    top='''<section class="page-hero safeguard-hero"><div class="container"><nav class="breadcrumb-custom" aria-label="Breadcrumb"><a href="/">Home</a> / Safeguarding</nav><span class="eyebrow">Safeguarding and child protection</span><h1>Keeping children and young people safe</h1><p>Northamptonshire Tutoring, part of North Wales Tutoring Group, takes safeguarding seriously throughout online lessons, tutor matching, communications and the management of concerns.</p><div class="hero-actions d-flex flex-wrap gap-2"><a class="btn btn-pink" href="#report-a-concern">Report a safeguarding concern</a><a class="btn btn-outline-navy" href="#safeguarding-policy">Read our policy</a></div></div></section>'''
    emergency='''<section class="section safety-emergency"><div class="container"><div class="emergency-grid"><div><span class="eyebrow">Immediate danger</span><h2>If someone is in danger, call 999.</h2><p>Do not wait for our website form or a response from our team. If a child is at risk and it is not an immediate emergency, contact Northamptonshire Children's Trust's Multi-Agency Safeguarding Hub (MASH) on <a href="tel:03001267000">0300 126 7000</a>.</p></div><div class="safety-contacts"><a href="tel:999" class="btn btn-pink">Call 999 in an emergency</a><a href="https://nctrust.co.uk/report-a-concern-or-request-support/" target="_blank" rel="noopener" class="btn btn-outline-navy">Report to Children's Trust</a></div></div></div></section>'''
    panels=[
       ('Our commitment','We work to promote the welfare of learners and respond appropriately to information suggesting a child may be at risk. Protecting learners takes priority over any commercial considerations. This policy covers tuition, tutoring-related messages, learning platforms and associated contact.'),
       ('People, roles and responsibilities','Jesse is the Designated Safeguarding Lead (DSL) for our group. Tutors and other people providing tuition must maintain professional boundaries, report concerns promptly, preserve factual records and co-operate with safeguarding processes. Our tutoring provider remains responsible for safeguarding processes it controls.'),
       ('Tutor suitability, DBS and vetting','We carry out role-appropriate suitability checks, which may include identity, qualifications or experience, references, safeguarding declarations and DBS information where legally appropriate. A DBS certificate is not a guarantee of future conduct; appropriate professional boundaries and ongoing oversight also matter.'),
       ('Online tutoring safeguards','Tutors must communicate professionally, use agreed channels and avoid inappropriate private contact with learners. Sessions, messages, file sharing and learning tools should be age-appropriate. Parents and carers should have a clear route to report uncomfortable or inappropriate behaviour.'),
       ('Recognising and reporting concerns','Concerns may include neglect, abuse, exploitation, discrimination, bullying, inappropriate messages, grooming, boundary breaches or other behaviours that put a learner at risk. You do not need proof before telling us or contacting authorities.'),
       ('Listening to a learner','Listen calmly, do not promise secrecy, avoid leading questions, record the learner’s own words where possible and report promptly. Do not investigate allegations yourself or circulate sensitive details unnecessarily.'),
       ('Concerns about a tutor or the DSL','You can report any tutor-related concern using the confidential form. If the concern relates to Jesse or you prefer not to report internally, contact Northamptonshire Children’s Trust, the police or the relevant safeguarding authority directly. You do not need our permission to make an external referral.'),
       ('Recording and information sharing','We keep factual, proportionate safeguarding records and share information only where appropriate for protecting learners or meeting legal obligations. Safeguarding information is handled with restricted access and in accordance with applicable data protection requirements.'),
       ('Responding and escalating','We may restrict tutoring arrangements while a concern is assessed, seek specialist advice, notify relevant authorities or report allegations where required. We do not replace statutory investigations, decide whether crimes occurred or promise to keep a concern confidential when safety requires sharing.'),
       ('Policy review and statutory context','We review safeguarding procedures at least annually and when circumstances or relevant guidance change. Our procedures take account of the safeguarding framework applicable in England, including Children Act provisions, Working Together to Safeguard Children, Keeping Children Safe in Education 2026 where relevant, and local safeguarding partnership procedures.')
    ]
    policy=''.join(f'<article class="policy-chapter" id="policy-{i+1}"><span>{i+1:02d}</span><div><h3>{E(head)}</h3><p>{E(content)}</p></div></article>' for i,(head,content) in enumerate(panels))
    body=top+emergency+f'''<section class="section safety-lead"><div class="container"><div class="row g-5 align-items-center"><div class="col-lg-5"><span class="eyebrow">Designated Safeguarding Lead</span><h2>Jesse</h2><p class="lead">Founder &amp; Designated Safeguarding Lead</p><p>Jesse leads our group's safeguarding procedures, including receiving concerns, maintaining proportionate records and seeking advice or referrals when necessary.</p><p>Confidential safeguarding email: <a href="mailto:{mail}">{mail}</a>.</p></div><div class="col-lg-7"><div class="safety-values"><div><i class="bi bi-shield-check" aria-hidden="true"></i><h3>Professional boundaries</h3><p>Appropriate conduct and communication in every lesson.</p></div><div><i class="bi bi-person-check" aria-hidden="true"></i><h3>Role-appropriate checks</h3><p>Suitability and safeguarding checks appropriate to each tutor.</p></div><div><i class="bi bi-megaphone" aria-hidden="true"></i><h3>Clear reporting</h3><p>Parents, learners and tutors can raise a concern.</p></div><div><i class="bi bi-journal-check" aria-hidden="true"></i><h3>Regular review</h3><p>Procedures are reviewed at least annually.</p></div></div></div></div></div></section><section class="section section-soft" id="safeguarding-policy"><div class="container"><div class="safety-policy-layout"><div class="safety-policy-heading"><span class="eyebrow">Safeguarding policy</span><h2>Our safeguarding commitments and procedures</h2><p>Every concern deserves to be taken seriously. The following explains our approach for families, tutors and learners across Northamptonshire.</p><a class="btn btn-pink" href="#report-a-concern">Raise a concern</a></div><div class="policy-chapters">{policy}</div></div></div></section>'''
    body+=f'''<section class="section safety-form-area" id="report-a-concern"><div class="container"><div class="row g-5"><div class="col-lg-5"><span class="eyebrow">Confidential reporting</span><h2>Report a safeguarding concern</h2><p>Use this form if you have a concern about a learner's safety or someone's behaviour in connection with our tutoring service. You do not need to prove what happened before reporting.</p><div class="safety-warning"><strong>This form is not monitored for emergencies.</strong><p>For immediate danger call 999. For other child protection concerns you may contact Northamptonshire Children's Trust on <a href="tel:03001267000">0300 126 7000</a>.</p></div><p>Prefer email? Write directly to <a href="mailto:{mail}">{mail}</a>.</p></div><div class="col-lg-7"><form id="safeguardingForm" class="safeguarding-form contact-section-form" action="#" method="POST" data-safeguarding><h2>Safeguarding concern form</h2><p>We will handle the report as sensitively as possible and may need to share relevant information to protect a learner.</p><input type="hidden" name="access_key" value="{key}"><input type="hidden" name="subject" value="URGENT: Northamptonshire Tutoring Safeguarding Concern"><input type="hidden" name="source" value="Northamptonshire Tutoring Safeguarding Page"><input name="botcheck" type="checkbox" autocomplete="off" tabindex="-1" aria-hidden="true" style="display:none!important"><fieldset><legend>Your details</legend><div class="row g-3"><div class="col-md-6"><label class="form-label" for="sg-name">Your name *</label><input class="form-control" id="sg-name" name="reporter_name" required maxlength="120"></div><div class="col-md-6"><label class="form-label" for="sg-email">Email address *</label><input class="form-control" type="email" id="sg-email" name="reporter_email" required></div><div class="col-md-6"><label class="form-label" for="sg-phone">Phone / WhatsApp number</label><input class="form-control" type="tel" id="sg-phone" name="reporter_phone"></div><div class="col-md-6"><label class="form-label" for="sg-relation">Your relationship to the learner *</label><select class="form-select" id="sg-relation" name="relationship_to_learner" required><option value="">Select relationship</option><option>Parent</option><option>Carer</option><option>Learner</option><option>Tutor</option><option>Family member</option><option>Other</option></select></div></div></fieldset><fieldset><legend>Learner and tutor</legend><div class="row g-3"><div class="col-md-6"><label class="form-label" for="sg-learner">Learner's name (if known)</label><input class="form-control" id="sg-learner" name="learner_name"></div><div class="col-md-6"><label class="form-label" for="sg-tutor">Tutor concerned (if applicable)</label><input class="form-control" id="sg-tutor" name="tutor_concerned"></div><div class="col-12"><label class="form-label" for="sg-context">Where did the concern arise?</label><select class="form-select" id="sg-context" name="concern_context"><option value="">Please select</option><option>Online lesson</option><option>Message or communication</option><option>In-person lesson</option><option>Behaviour outside tutoring</option><option>Other</option></select></div></div></fieldset><fieldset><legend>What happened?</legend><div class="row g-3"><div class="col-md-6"><label class="form-label" for="sg-date">Date of concern</label><input class="form-control" type="date" id="sg-date" name="incident_date"></div><div class="col-md-6"><label class="form-label" for="sg-time">Approximate time</label><input class="form-control" type="time" id="sg-time" name="incident_time"></div><div class="col-12"><label class="form-label" for="sg-details">Describe the concern *</label><textarea class="form-control" id="sg-details" name="concern_details" rows="7" maxlength="9000" placeholder="Please describe what you know, including relevant dates, words used and what concerns you. Do not include or upload explicit images of children." required></textarea></div><div class="col-12"><label class="form-label" for="sg-action">Have you already taken any action or contacted an authority?</label><textarea class="form-control" id="sg-action" name="actions_already_taken" rows="3" maxlength="3000" placeholder="Optional"></textarea></div></div></fieldset><button type="submit" class="btn btn-pink safeguarding-submit-btn">Submit safeguarding concern</button><p class="form-status" role="status" aria-live="polite"></p><p class="form-note">Submitted securely through Web3Forms. This report is separate from our standard tutoring enquiry process. Read our <a href="/privacy.html">privacy policy</a>.</p></form></div></div></div></section>'''

    path='/safeguarding.html'
    html=base('Safeguarding & Child Protection | Northamptonshire Tutoring','Read Northamptonshire Tutoring safeguarding policy, Designated Safeguarding Lead Jesse, how to report a concern and the confidential safeguarding@nwttutoring.com contact.',path,body,[crumb_schema([('Safeguarding',path)])])
    html=html.replace('<script defer src="/assets/js/forms.js"></script>','<script defer src="/assets/js/forms.js"></script><script defer src="/assets/js/safeguarding.js"></script>')
    write(path,html)

def page_classification(path):
    if path=='index.html':return 'home'
    if path=='safeguarding.html':return 'safety'
    if path.startswith('locations/'):return 'town'
    if path.startswith('exam/'):return 'qualification'
    if path.startswith('blog/'):return 'article'
    if path.endswith('-tutoring-northamptonshire.html'):return 'service'
    if path in ('tutors.html','subjects.html'):return 'directory'
    if path=='exam-preparation.html':return 'exam-directory'
    return {'about.html':'about','contact.html':'contact','areas.html':'areas','blog.html':'blog','privacy.html':'policy','cookie-policy.html':'policy'}.get(path,'general')

def offer_panel(path,kind,variant):
    if kind=='service':
        label=path.removesuffix('.html').removesuffix('-tutoring-northamptonshire').replace('-',' ').title()
        subj=next((s for s in SUBJECTS if s['slug']+'.html'==path),None)
        lead=subj['who'] if subj else f'Personalised online {label} tuition, delivered by a suitable subject-specialist tutor from the NWT network.'
        topics=subj['topics'][:3] if subj else [f'{label} concepts','Past-paper skills','Confidence and exam technique']
        target=E(label);prompt=f'{label} tutor'
    elif kind=='town':
        slug=Path(path).stem
        town=next((x for x in LOCATIONS if x['slug']==slug),None)
        label=town['name'] if town else slug.title()
        lead=(town.get('specific') or town.get('benefit')) if town else f'Personalised one-to-one tutoring for {label} pupils.'
        topics=[f'GCSE {label} learners','A-Level exam board support','KS2 & KS3 foundations']
        target=f'{E(label)} families';prompt=f'online tutoring in {label}'
    else:return ''
    chips=''.join('<span>'+E(v)+'</span>' for v in topics)
    layouts=[
     f'<div class="insight-side insight-dark"><span class="insight-num">01 / Personalised support</span><h2>{target}, let’s make the next topic feel achievable.</h2><p>{E(lead)}</p><a class="btn btn-pink" href="/contact.html">Discuss a tutor match</a></div><div class="insight-chips">{chips}</div>',
     f'<div class="insight-side insight-light"><span class="insight-num">02 / Where progress starts</span><h2>Know what to work on next.</h2><p>{E(lead)}</p><div class="insight-chips">{chips}</div></div><div class="insight-stripe"><strong>{target}</strong><span>Online 1-to-1 lessons</span><a class="btn btn-pink" href="/contact.html">Check availability</a></div>',
     f'<div class="insight-side insight-minimal"><span class="insight-num">03 / Built for your goals</span><h2>More than revision. A clear way forward.</h2><p>{E(lead)}</p><a class="btn btn-outline-navy" href="/contact.html">Enquire about {E(prompt)}</a></div><div class="insight-chips">{chips}</div>',
     f'<div class="insight-side insight-feature"><span class="insight-num">04 / Lessons with purpose</span><h2>Better questions. Better understanding.</h2><p>{E(lead)}</p><div class="insight-chips">{chips}</div><a class="btn btn-pink" href="/contact.html">Get started</a></div>'
    ]
    return f'<section class="insight-section insight-variant-{variant%4}" aria-label="Tailored tutoring support"><div class="container"><div class="insight-grid">{layouts[variant%4]}</div></div></section>'

def local_schema(path,kind):
    towns=[x['name'] for x in LOCATIONS]
    place=next((x['name'] for x in LOCATIONS if path=='locations/'+x['slug']+'.html'),'Northamptonshire')
    places=[{'@type':'AdministrativeArea','name':'Northamptonshire, England'}, {'@type':'AdministrativeArea','name':'North Northamptonshire, England'}, {'@type':'AdministrativeArea','name':'West Northamptonshire, England'}]
    places += [{'@type':'City','name':x+', Northamptonshire, England'} for x in towns]
    return {'@context':'https://schema.org','@type':['EducationalOrganization','LocalBusiness'],
      '@id':DOMAIN+'/#organisation','name':'Northamptonshire Tutoring','url':DOMAIN+'/',
      'logo':DOMAIN+'/assets/images/nwt-group-crest-2026.jpg',
      'image':DOMAIN+'/assets/images/study-session.webp',
      'description':'Online one-to-one tutoring and exam preparation for students in Northamptonshire, including GCSE and A-Level Maths, Physics, Chemistry, Biology, English, Computer Science, Economics, Humanities, languages and other subjects.',
      'telephone':SITE['phone_international'],'email':SITE['email'],
      'priceRange':'GCSE from £23/hr; A-Level from £28/hr',
      'hasOfferCatalog':{'@type':'OfferCatalog','name':'Northamptonshire online tutoring services','itemListElement':[
        {'@type':'OfferCatalog','name':'GCSE tutoring from £23 per hour','url':DOMAIN+'/exam/gcse.html'},
        {'@type':'OfferCatalog','name':'A-Level tutoring from £28 per hour','url':DOMAIN+'/exam/a-level.html'},
        {'@type':'OfferCatalog','name':'SATs and entrance exam preparation','url':DOMAIN+'/exam-preparation.html'}]},
      'areaServed':places,'sameAs':[SITE['facebook'],SITE['instagram']],
      'parentOrganization':{'@type':'Organization','name':'North Wales Tutoring Group','url':SITE['parent_url']},
      'knowsAbout':[n for names in PARENT_SUBJECTS.values() for n in names]+['SATs','11+','13+','UCAT','TMUA','GMAT','GCSE','A-Level','AQA','Pearson Edexcel','OCR','WJEC','Eduqas','Cambridge International']}

def group_review_section():
    """Faithfully reproduce parent-company feedback without attributing it to this branch."""
    cards=[]
    for item in REVIEWS:
        name=E(item['name']);role=E(item['role']);context=E(item['context'])
        quote=E(item['quote'])
        cards.append(
            '<article class="nt-review-card">'
            '<span class="nt-review-category">'+context+'</span>'
            '<blockquote>'+quote+'</blockquote>'
            '<div class="nt-review-byline"><span class="nt-review-avatar" aria-hidden="true">'+name[:1]+'</span>'
            '<span><strong>'+name+'</strong><small>'+role+'</small></span></div></article>'
        )
    return (
        '<section id="nt-group-testimonials" class="nt-testimonials section" aria-labelledby="nt-review-title">'
        '<div class="container"><div class="nt-review-head"><div>'
        '<span class="eyebrow">Real family feedback from our parent group</span>'
        '<h2 id="nt-review-title">What families and students say about North Wales Tutoring</h2>'
        '<p>Unedited feedback from families and students supported by North Wales Tutoring Group. '
        'These are group-wide reviews, not claims about Northamptonshire-specific students.</p>'
        '</div></div>'
        '<div class="nt-review-grid" data-mobile-carousel="reviews">'+''.join(cards)+'</div>'
        '<p class="nt-review-attribution">Testimonials reproduced exactly from '
        '<a href="https://northwalestutoring.com/" target="_blank" rel="noopener">'
        'North Wales Tutoring</a>, our parent group.</p></div></section>'
    )


def refresh_all():
    NAV=nav_html();FOOT=footer_html();count=0
    skip={'source','components','.git','_site','node_modules'}
    pages=[p for p in ROOT.rglob('*.html') if not any(part in skip for part in p.relative_to(ROOT).parts) and not p.name.startswith('preview-')]
    for n,p in enumerate(sorted(pages)):
        rel=p.relative_to(ROOT).as_posix();kind=page_classification(rel)
        txt=p.read_text(encoding='utf8')
        # Preserve emergency contact guidance but remove the separate external-reporting panel.
        if kind=='safety':
            txt=re.sub(r'<section class="section section-soft"><div class="container"><span class="eyebrow">Guidance &amp; external reporting</span>[\\s\\S]*?</section>','',txt,count=1)
        # Parent-group reviews are added to key conversion pages without rewriting the quotes.
        if kind in ('home','about','contact') and 'id="nt-group-testimonials"' not in txt:
            txt=txt.replace('</main>',group_review_section()+'</main>',1)
        # A purpose-built 1200 x 630 brand image is used by WhatsApp, LinkedIn and Facebook.
        social_image=DOMAIN+'/assets/images/nwt-group-social-1200x630.jpg'
        txt=re.sub(r'<meta property="og:image" content="[^"]*">',lambda m:'<meta property="og:image" content="'+social_image+'">',txt,count=1)
        txt=re.sub(r'<meta property="og:image:alt" content="[^"]*">',lambda m:'<meta property="og:image:alt" content="North Wales Tutoring Group crest and Northamptonshire Tutoring brand">',txt,count=1)
        for prop,value in [('og:image:width','1200'),('og:image:height','630'),('og:image:type','image/jpeg')]:
            if 'property="'+prop+'"' not in txt:
                txt=txt.replace('</head>','<meta property="'+prop+'" content="'+value+'"></head>',1)
        if 'name="twitter:image"' not in txt:
            txt=txt.replace('</head>','<meta name="twitter:image" content="'+social_image+'"></head>',1)
        if 'name="twitter:image:alt"' not in txt:
            txt=txt.replace('</head>','<meta name="twitter:image:alt" content="North Wales Tutoring Group branded crest"></head>',1)
        # Tracking only starts after visitors agree to optional cookies.
        for jsfile in ('mobile-cards.js','gtm-consent.js'):
            if '/assets/js/'+jsfile not in txt and 'assets/js/'+jsfile not in txt:
                txt=txt.replace('</body>','<script defer src="/assets/js/'+jsfile+'"></script></body>',1)
        m=re.search(r'<a class="skip-link"[\s\S]*?</header>',txt)
        if m:txt=txt[:m.start()]+NAV+txt[m.end():]
        else:print('WARN: missing nav',rel)
        txt,repl=re.subn(r'<footer\b[^>]*>[\s\S]*?</footer>',lambda m:FOOT,txt,count=1)
        if not repl:print('WARN: missing footer',rel)
        # Every page shares the true service-area organisation, without inventing a physical address.
        scripts=re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',txt)
        replacement_schema=json.dumps(local_schema(rel,kind),ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
        replaced=False
        for s in scripts:
            try:data=json.loads(s)
            except json.JSONDecodeError:continue
            if data.get('@id')==DOMAIN+'/#organisation':
                txt=txt.replace('<script type="application/ld+json">'+s+'</script>','<script type="application/ld+json">'+replacement_schema+'</script>',1)
                replaced=True;break
        if not replaced:txt=txt.replace('</head>','<script type="application/ld+json">'+replacement_schema+'</script></head>',1)
        for tag in ('<meta name="geo.placename" content="Northamptonshire, England">','<meta property="og:locale" content="en_GB">'):
            if tag not in txt:txt=txt.replace('</head>',tag+'</head>',1)
        # Location-relevant page metadata; no pretend offices, false Google rankings or fabricated results.
        if kind=='town':
            town=p.stem.title();description=f'Find online GCSE, A-Level, Maths, Physics, English, Science and wider subject tutors for {town}, Northamptonshire. Personalised 1-to-1 lessons; GCSE from £23/hr and A-Level from £28/hr.'
            txt=re.sub(r'(<meta name="description" content=")[^"]*(")',lambda m:m.group(1)+E(description,quote=True)+m.group(2),txt,count=1)
        elif kind=='service':
            slug=p.stem.replace('-tutoring-northamptonshire','').replace('-',' ')
            description=f'Find one-to-one online {slug} tutors for Northampton, Corby, Kettering, Wellingborough and wider Northamptonshire. Exam-board-focused GCSE and A-Level support; ask about current availability.'
            txt=re.sub(r'(<meta name="description" content=")[^"]*(")',lambda m:m.group(1)+E(description,quote=True)+m.group(2),txt,count=1)
        # Distinct editorial hero and content-treatment per page; stable variant assignment.
        variant=int(hashlib.md5(rel.encode()).hexdigest(),16)%10
        if '<body' in txt:
            txt=re.sub(r'<body(?:\s[^>]*)?>',f'<body class="page-{kind} layout-{variant}" data-layout="{variant}">',txt,count=1)
        if kind in ('service','town') and 'insight-section' not in txt:
            m=re.search(r'<section class="page-hero"[\s\S]*?</section>',txt)
            if m:
                txt=txt[:m.end()]+offer_panel(rel,kind,variant)+txt[m.end():]
        # Use a useful, route-specific pre-filled WhatsApp opening, without sharing form details.
        context= 'tutoring in Northamptonshire'
        if kind=='service':context=p.stem.replace('-tutoring-northamptonshire','').replace('-',' ')+' tutoring'
        elif kind=='town':context='online tutoring in '+p.stem.title()
        elif kind=='qualification':context=p.stem.replace('-',' ').upper()+' exam preparation'
        elif kind=='safety':context='standard tutoring enquiries (not safeguarding concerns)'
        msg=wa_message(context)
        if kind=='safety':txt=re.sub(r'<a class="whatsapp-float"[\s\S]*?</a>','',txt)
        else:
            txt=re.sub(r'<a class="whatsapp-float"[\s\S]*?</a>',f'<a class="whatsapp-float" href="{E(msg,quote=True)}" target="_blank" rel="noopener" aria-label="Ask Northamptonshire Tutoring about {E(context,quote=True)} on WhatsApp"><i class="bi bi-whatsapp" aria-hidden="true"></i><span>Message us</span></a>',txt,count=1)
            if 'class="whatsapp-float"' not in txt:txt=txt.replace('</body>',f'<a class="whatsapp-float" href="{E(msg,quote=True)}" target="_blank" rel="noopener" aria-label="Message on WhatsApp"><i class="bi bi-whatsapp" aria-hidden="true"></i><span>Message us</span></a></body>')
        # Pre-fill every WhatsApp contact link, not only the floating action.
        # Keep existing explicit messages intact; never place form contents in the URL.
        txt=re.sub(r'(href=["\']https://wa\.me/447480231362)(["\'])',
                   lambda m:m.group(1)+'?text='+quote(f"Hi Northamptonshire Tutoring, I'd like to ask about {context}. Could you help me?",safe='')+m.group(2),txt)
        # Guarantee contextually correct links in a GitHub Pages project subdirectory and custom domain.
        prefix='../'* (len(p.relative_to(ROOT).parts)-1)
        txt=re.sub(r'(?P<attr>\b(?:href|src)=(["\']))/(?P<target>[^"\']*)',lambda m:m.group('attr')+prefix+(m.group('target') or './'),txt)
        p.write_text(txt,encoding='utf8');count+=1
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    urls=['/' if p.name=='index.html' else '/'+p.relative_to(ROOT).as_posix() for p in sorted(pages)]
    for u in sorted(urls,key=lambda x:(x!='/ ',x)):
        sitemap+=f'<url><loc>{DOMAIN+u}</loc><lastmod>2026-11-11</lastmod></url>\n'
    (ROOT/'sitemap.xml').write_text(sitemap+'</urlset>\n',encoding='utf8')
    print('Refreshed',count,'HTML pages; added full local service schema, footer crest, unique layouts and navigation')

if __name__=='__main__':
    (ROOT/'components/navbar.html').write_text(nav_html(),encoding='utf8')
    (ROOT/'components/footer.html').write_text(footer_html(),encoding='utf8')
    subject_directory_page(False);subject_directory_page(True)
    exam_pages();safeguarding_page()
    refresh_all()
