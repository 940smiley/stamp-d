function enableLayoutMode(enabled){
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
  const containers=[upload, gallery];
  containers.forEach(c=>{
    if(!c) return;
    if(enabled){
      if(!c.sortable){
        c.sortable=Sortable.create(c,{animation:150,handle:null,onEnd:saveOrder});
      }
      Array.from(c.children).forEach(el=>el.classList.add('resizable'));
    }else{
      if(c.sortable){c.sortable.destroy();c.sortable=null;}
      Array.from(c.children).forEach(el=>el.classList.remove('resizable'));
    }
  });
  document.body.classList.toggle('layout-mode', enabled);
  localStorage.setItem('layout_mode', enabled? '1':'0');
}
function saveOrder(){
  const upload=document.getElementById('upload_results');
  const gallery=document.getElementById('gallery_results');
  if(upload){
    const ids=Array.from(upload.children).map(e=>e.id);
    localStorage.setItem('upload_order', JSON.stringify(ids));
  }
  if(gallery){
    const ids=Array.from(gallery.children).map(e=>e.id);
    localStorage.setItem('gallery_order', JSON.stringify(ids));
  }
}
function applySavedOrder(){
  const upload=document.getElementById('upload_results');
  const savedUp=JSON.parse(localStorage.getItem('upload_order')||'[]');
  savedUp.forEach(id=>{const el=document.getElementById(id);if(el) upload.appendChild(el);});
  const gallery=document.getElementById('gallery_results');
  const savedGal=JSON.parse(localStorage.getItem('gallery_order')||'[]');
  savedGal.forEach(id=>{const el=document.getElementById(id);if(el) gallery.appendChild(el);});
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
  if(toggle){
    toggle.checked=mode;
    enableLayoutMode(mode);
    toggle.addEventListener('change',()=>enableLayoutMode(toggle.checked));
  }
}
document.addEventListener('DOMContentLoaded',()=>{
  applySavedOrder();
});
