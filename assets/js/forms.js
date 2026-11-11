(() => {
  'use strict';
  // Web3Forms is called with fetch, never with a browser form navigation.
  // Keep this script defer-loaded on every page with a contact form.
  const forms = document.querySelectorAll('form[data-web3forms]');
  const safeMessage = (form, message, state) => {
    const node = form.querySelector('.form-status');
    if (node) { node.textContent=message; node.dataset.state=state; }
  };
  const showPopup = (title, text, icon) => {
    if (window.Swal && typeof window.Swal.fire === 'function') {
      return window.Swal.fire({title, text, icon, confirmButtonText:'OK', confirmButtonColor:'#09096A', customClass:{popup:'nt-swal-popup'},heightAuto:false});
    }
    // Accessible fallback when SweetAlert CDN cannot load.
    window.alert(`${title}\n\n${text}`);
  };
  const params = new URLSearchParams(location.search);
  if (params.has('tutor')) {
    const tutor = String(params.get('tutor')||'').slice(0,70).replace(/[<>]/g,'').trim();
    if (tutor) forms.forEach(form=>{
      const msg=form.querySelector('textarea[name="message"]');
      if (msg && !msg.value.trim()) msg.value=`Hello, I would like to ask about ${tutor} and suitable online tutoring. My student's year group, subject and exam board are: `;
    });
  }
  for (const form of forms) {
    const submit = form.querySelector('button[type="submit"]');
    const initialHTML = submit?.innerHTML || 'Send my enquiry';
    const initTime = Date.now();
    let lastSubmit = 0;
    form.addEventListener('submit',async event=>{
      event.preventDefault();
      if (!form.reportValidity()) return;
      const bot = form.querySelector('[name="botcheck"]');
      if (bot?.checked) return;
      if (Date.now()-initTime<1200) {safeMessage(form,'Please review your message and try again.','error');return;}
      if (Date.now()-lastSubmit<15000) {safeMessage(form,'Please wait a few seconds before trying again.','error');return;}
      const phone = String(form.elements.phone?.value || '').replace(/[\s()\-+.]/g,'');
      if (!/^\d{7,15}$/.test(phone)) {safeMessage(form,'Please enter a valid contact number.','error');form.elements.phone?.focus();return;}
      lastSubmit=Date.now();
      submit.disabled=true;
      submit.innerHTML='Sending enquiry… <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
      safeMessage(form,'Sending your enquiry…','');
      try {
        const data=Object.fromEntries(new FormData(form).entries());
        delete data.botcheck;
        const response=await fetch('https://api.web3forms.com/submit',{
          method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data),redirect:'error'
        });
        const result=await response.json();
        if (!response.ok || result.success!==true) throw new Error(result.message || 'Unsuccessful submission');
        form.reset();
        safeMessage(form,'Thank you! Our team will be in touch with you soon.','success');
        showPopup('Thank you!','Your enquiry has been sent successfully. Our team will be in touch with you soon.','success');
        if (typeof window.gtag==='function') window.gtag('event','generate_lead',{form_id:form.id});
      } catch(e) {
        console.error('Web3Forms enquiry failed',e);
        safeMessage(form,'We could not send your enquiry. Please try again, email northamptonshire@nwttutoring.com or WhatsApp us.','error');
        showPopup('Something went wrong','Your enquiry could not be sent. Please try again or contact us by WhatsApp.','error');
        lastSubmit=0;
      } finally {
        submit.disabled=false;
        submit.innerHTML=initialHTML;
      }
    });
  }
})();
