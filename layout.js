function enableLayoutMode(enabled){
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
  const containers=[upload, gallery];
const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
function enableLayoutMode(enabled){
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
  const containers=[upload, gallery];
  containers.forEach(container => {
  containers.forEach(container => {
    if(!container) return;
    if(enabled){
      if(!container.sortable){
        container.sortable=Sortable.create(container,{animation:150,handle:null,onEnd:saveOrder});
      }
      Array.from(container.children).forEach(el=>el.classList.add('resizable'));
    }else{
      if(container.sortable){container.sortable.destroy();container.sortable=null;}
      Array.from(container.children).forEach(el=>el.classList.remove('resizable'));
    }
  });
  document.body.classList.toggle('layout-mode', enabled);
    if(!c) return;
    if(enabled){
      if(!c.sortable){
        c.sortable=Sortable.create(c,{animation:150,handle:null,onEnd:saveOrder});
      }
if(!c.sortable){
        c.sortable=Sortable.create(c,{animation:150,handle:null,onEnd:saveOrder});
      }
      if (c.children) {
        Array.from(c.children).forEach(el=>el.classList.add('resizable'));
      }
    }else{
      if(c.sortable){c.sortable.destroy();c.sortable=null;}
      if (c.children) {
        Array.from(c.children).forEach(el=>el.classList.remove('resizable'));
      }
    }
function enableLayoutMode(enabled){
  const uploadResults = document.getElementById('upload_results');
  const galleryResults = document.getElementById('gallery_results');
  const containers = [uploadResults, galleryResults];

  containers.forEach(container => {
    if(!container) return;
    if(enabled){
      if(!container.sortable){
        container.sortable = Sortable.create(container, {animation: 150, handle: null, onEnd: saveOrder});
      }
      Array.from(container.children).forEach(el => el.classList.add('resizable'));
    } else {
      if(container.sortable){
        container.sortable.destroy();
        container.sortable = null;
      }
      Array.from(container.children).forEach(el => el.classList.remove('resizable'));
    }
  });

  document.body.classList.toggle('layout-mode', enabled);
  localStorage.setItem('layout_mode', enabled ? '1' : '0');
}

function saveOrder(){
  const upload = document.getElementById('upload_results');
// Cache DOM elements
const uploadResults = document.getElementById('upload_results');
const galleryResults = document.getElementById('gallery_results');

function enableLayoutMode(enabled){
  const containers = [uploadResults, galleryResults];
  containers.forEach(c => {
    if(!c) return;
    if(enabled){
  document.body.classList.toggle('layout-mode', enabled);
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
// Cache DOM elements
const uploadResults = document.getElementById('upload_results');
const galleryResults = document.getElementById('gallery_results');

function enableLayoutMode(enabled){
  const containers = [uploadResults, galleryResults];
  containers.forEach(c=>{
    if(!c) return;
    if(enabled){
      if(!c.sortable){
function enableLayoutMode(enabled) {
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
  const containers = [upload, gallery];
  containers.forEach(c => {
    if (!c) return;
    if (enabled) {
      if (!c.sortable) {
        c.sortable = Sortable.create(c, { animation: 150, handle: null, onEnd: saveOrder });
      }
if (!c.sortable) {
        c.sortable = Sortable.create(c, { animation: 150, handle: null, onEnd: saveOrder });
      }
      if (c.children) {
        Array.from(c.children).forEach(el => el.classList.add('resizable'));
      }
    } else {
      if (c.sortable) { c.sortable.destroy(); c.sortable = null; }
      if (c.children) {
        Array.from(c.children).forEach(el => el.classList.remove('resizable'));
      }
    }
  });
  document.body.classList.toggle('layout-mode', enabled);
    } else {
      if (c.sortable) { c.sortable.destroy(); c.sortable = null; }
      Array.from(c.children).forEach(el => el.classList.remove('resizable'));
    }
  });
  document.body.classList.toggle('layout-mode', enabled);
  localStorage.setItem('layout_mode', enabled ? '1' : '0');
}
function saveOrder() {
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');
  if (upload) {
    const ids = Array.from(upload.children).map(e => e.id);
    localStorage.setItem('upload_order', JSON.stringify(ids));
  }
  if (gallery) {
    const ids = Array.from(gallery.children).map(e => e.id);
    localStorage.setItem('gallery_order', JSON.stringify(ids));
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
  if(uploadResults){
    const ids=Array.from(uploadResults.children).map(e=>e.id);
    localStorage.setItem('upload_order', JSON.stringify(ids));
  }
  if(galleryResults){
    const ids=Array.from(galleryResults.children).map(e=>e.id);
    localStorage.setItem('gallery_order', JSON.stringify(ids));
  }
}

function applySavedOrder(){
  const savedUp=JSON.parse(localStorage.getItem('upload_order')||'[]');
  savedUp.forEach(id=>{const el=document.getElementById(id);if(el) uploadResults.appendChild(el);});
}

function applySavedOrder(){
  let savedUp = [];
  try {
    savedUp = JSON.parse(localStorage.getItem('upload_order') || '[]');
  } catch (error) {
    console.error('Error parsing upload_order:', error);
  }
  savedUp.forEach(id=>{const el=document.getElementById(id);if(el) uploadResults.appendChild(el);});
  
  let savedGal = [];
  try {
    savedGal = JSON.parse(localStorage.getItem('gallery_order') || '[]');
  } catch (error) {
    console.error('Error parsing gallery_order:', error);
  }
  savedGal.forEach(id=>{const el=document.getElementById(id);if(el) galleryResults.appendChild(el);});
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
  savedGal.forEach(id=>{const el=document.getElementById(id);if(el) galleryResults.appendChild(el);});
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
  if(toggle){
    toggle.checked=mode;
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
}
function applySavedOrder(){
  const upload=document.getElementById('upload_results');
  let savedUp = [];
  try {
    savedUp = JSON.parse(localStorage.getItem('upload_order') || '[]');
  } catch (error) {
    console.error('Error parsing upload_order:', error);
  }
  savedUp.forEach(id=>{const el=document.getElementById(id);if(el) upload.appendChild(el);});
  const gallery=document.getElementById('gallery_results');
  let savedGal = [];
  try {
    savedGal = JSON.parse(localStorage.getItem('gallery_order') || '[]');
  } catch (error) {
    console.error('Error parsing gallery_order:', error);
  }
  savedGal.forEach(id=>{const el=document.getElementById(id);if(el) gallery.appendChild(el);});
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
}
function applySavedOrder(){
  const upload=document.getElementById('upload_results');
  const gallery=document.getElementById('gallery_results');
  if(upload){
    const savedUp=JSON.parse(localStorage.getItem('upload_order')||'[]');
    savedUp.forEach(id=>{const el=document.getElementById(id);if(el) upload.appendChild(el);});
  }
  if(gallery){
    const savedGal=JSON.parse(localStorage.getItem('gallery_order')||'[]');
    savedGal.forEach(id=>{const el=document.getElementById(id);if(el) gallery.appendChild(el);});
  }
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
  if(toggle){
  const mode=localStorage.getItem('layout_mode')==='1';
  const toggle=document.getElementById('layout_toggle');
  if(toggle){
    toggle.checked=mode;
    enableLayoutMode(mode);
    toggle.addEventListener('change',()=>enableLayoutMode(toggle.checked));
  }
function applySavedOrder() {
  const upload = document.getElementById('upload_results');
  const gallery = document.getElementById('gallery_results');

  if (upload) {
    let savedUp = [];
    try {
      savedUp = JSON.parse(localStorage.getItem('upload_order') || '[]');
    } catch (error) {
      console.error('Error parsing upload_order:', error);
    }
    savedUp.forEach(id => {
      const el = document.getElementById(id);
      if (el) upload.appendChild(el);
    });
  }

  if (gallery) {
    let savedGal = [];
    try {
      savedGal = JSON.parse(localStorage.getItem('gallery_order') || '[]');
    } catch (error) {
      console.error('Error parsing gallery_order:', error);
    }
    savedGal.forEach(id => {
      const el = document.getElementById(id);
      if (el) gallery.appendChild(el);
    });
  }


  const mode = localStorage.getItem('layout_mode') === '1';
  const toggle = document.getElementById('layout_toggle');
  if (toggle) {
    toggle.checked = mode;
    enableLayoutMode(mode);
    toggle.addEventListener('change', () => enableLayoutMode(toggle.checked));
  }
}

document.addEventListener('DOMContentLoaded', () => {
  applySavedOrder();
});
document.addEventListener('DOMContentLoaded',()=>{
  applySavedOrder();
});