(() => {
  'use strict';
  const form=document.querySelector('form[data-safeguarding]');
  if(!form)return;
  const submit=form.querySelector('button[type=submit]');
  const status=form.querySelector('.form-status');
  const started=Date.now();let lastAttempt=0;
  const message=(txt,error=false)=>{if(status){status.textContent=txt;status.dataset.state=error?'error':'success';}};
  function notice(title,txt,icon){if(window.Swal?.fire)window.Swal.fire({title,text:txt,icon,confirmButtonColor:'#09096a',confirmButtonText:'OK'});else window.alert(title+'\n\n'+txt);}
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    if(!form.reportValidity())return;
    if(form.elements.botcheck?.checked)return;
    if(Date.now()-started<1200){message('Please review your details and try again.',true);return;}
    if(Date.now()-lastAttempt<15000){message('Please wait before sending another report.',true);return;}
    if(!form.elements.access_key?.value){notice('Form not configured','Please email safeguarding@nwttutoring.com directly.','error');return;}
    lastAttempt=Date.now();submit.disabled=true;const old=submit.textContent;submit.textContent='Submitting your report…';message('Submitting your safeguarding report…');
    try{
      const payload=Object.fromEntries(new FormData(form).entries());delete payload.redirect;payload.botcheck=false;payload.name=payload.reporter_name;payload.email=payload.reporter_email;payload.message=payload.concern_details;
      const response=await fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(payload)});
      const result=await response.json();if(!response.ok||result.success!==true)throw Error(result.message||'Unable to submit');
      form.reset();message('Your safeguarding concern has been submitted.');
      notice('Safeguarding concern received','Your report has been submitted to the safeguarding team. If anyone is in immediate danger, call 999.','success');
    }catch(err){console.error('Safeguarding form submission issue:',err);lastAttempt=0;message('We could not submit this report. Please email safeguarding@nwttutoring.com directly, or contact statutory safeguarding services.',true);notice('Report not submitted','Please email safeguarding@nwttutoring.com directly. In an emergency call 999.','error');}
    finally{submit.disabled=false;submit.textContent=old;}
  });
})();
