(() => {
 'use strict';
 const forms=document.querySelectorAll('form[data-web3forms]');
 forms.forEach(form=>{
   const status=form.querySelector('.form-status');
   const submit=form.querySelector('button[type=submit]');
   const initialText=submit?.innerHTML ?? 'Send enquiry';
   const createdAt=Date.now();
   let lastSubmitAt=0;
   const say=(message,state)=>{if(status){status.textContent=message;status.dataset.state=state;}};
   const alertResult=(title,text,icon)=>{
     if(window.Swal?.fire){window.Swal.fire({icon,title,text,confirmButtonText:'OK',confirmButtonColor:'#09096a',allowOutsideClick:true});}
     else {window.alert(title+'\n\n'+text);}
   };
   form.addEventListener('submit',async event=>{
     event.preventDefault(); // Never navigate to Web3Forms or a thank-you URL
     if(!form.reportValidity())return;
     if(form.elements.botcheck?.checked)return;
     if(Date.now()-createdAt<1200){say('Please check your details and try again.','error');return;}
     if(Date.now()-lastSubmitAt<15000){say('Please wait before submitting again.','error');return;}
     const phone=String(form.elements.phone?.value||'').replace(/[\s()\-+.]/g,'');
     if(!/^\d{7,15}$/.test(phone)){say('Please enter a valid telephone number.','error');form.elements.phone?.focus();return;}
     lastSubmitAt=Date.now();
     submit.disabled=true;submit.innerHTML='Sending… <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>';
     say('Sending your enquiry…','');
     try{
       const payload=Object.fromEntries(new FormData(form).entries());
       delete payload.redirect;
       payload.botcheck=false;
       const response=await fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)});
       const result=await response.json();
       if(!response.ok || result.success!==true)throw new Error(result.message||'Submission failed');
       form.reset();
       say('Your enquiry has been sent. Our team will be in touch soon.','success');
       alertResult('Thank you!','Your enquiry has been received. Our team will be in touch with you soon.','success');
       if(typeof window.gtag==='function')window.gtag('event','generate_lead',{form_id:form.id});
     }catch(error){
       console.error('Enquiry submission error:',error);
       say('We could not submit your enquiry. Please contact northamptonshire@nwttutoring.com or use WhatsApp.','error');
       alertResult('Could not send enquiry','Please email northamptonshire@nwttutoring.com or message our team on WhatsApp.','error');
       lastSubmitAt=0;
     }finally{submit.disabled=false;submit.innerHTML=initialText;}
   });
 });
})();
