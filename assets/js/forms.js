(() => {
 'use strict';
 const forms=document.querySelectorAll('form[data-web3forms]');
 forms.forEach(form=>{
   const status=form.querySelector('.form-status');
   const submit=form.querySelector('button[type=submit]');
   const initialText=submit?.innerHTML ?? 'Send enquiry';
   const createdAt=Date.now();
   let lastSubmitAt=0;
   const say=(message,state)=>{if(status){status.textContent=message;status.dataset.state=state}};
   form.addEventListener('submit',async event=>{
     if(!('fetch' in window))return; // HTML POST fallback
     event.preventDefault();
     if(!form.reportValidity())return;
     if(form.elements.botcheck?.checked){return;}
     if(Date.now()-createdAt<1500){say('Please review your details and try again.','error');return;}
     if(Date.now()-lastSubmitAt<15000){say('Please wait a moment before submitting again.','error');return;}
     const phone=String(form.elements.phone?.value||'').replace(/[\s()\-+.]/g,'');
     if(!/^\d{7,15}$/.test(phone)){say('Please enter a valid phone number.','error');form.elements.phone?.focus();return;}
     lastSubmitAt=Date.now();
     submit.disabled=true;submit.innerHTML='Sending… <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>';
     say('Sending your enquiry…','');
     try{
       const payload=Object.fromEntries(new FormData(form).entries());
       payload.botcheck=false;
       const result=await fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)});
       const data=await result.json();
       if(!result.ok || data.success!==true)throw new Error(data.message||'Submission failed');
       form.reset();
       say('Thank you! Your enquiry was sent. Our tutoring team will be in touch.','success');
       const link=form.querySelector('[data-thanks-link]');if(link)link.hidden=false;
       if(typeof window.gtag==='function')window.gtag('event','generate_lead',{form_id:form.id});
     }catch(error){
       console.error('Enquiry submission error:',error);
       say('Your enquiry could not be sent. Please email northamptonshire@nwttutoring.com or message us on WhatsApp.','error');
       lastSubmitAt=0;
     }finally{submit.disabled=false;submit.innerHTML=initialText;}
   });
 });
})();
