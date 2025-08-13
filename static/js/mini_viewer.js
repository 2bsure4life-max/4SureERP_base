(() => {
  const API = `${location.origin.replace(/\/$/,'')}/api`;
  const el = {
    host: document.getElementById('mini-preview'),
    tabs: document.querySelector('#mini-preview .tabs'),
    frame: document.querySelector('#mini-preview iframe'),
    status: document.querySelector('#mini-preview .status')
  };

  function renderTabs(items){
    el.tabs.innerHTML = '';
    items.forEach((d, i) => {
      const b = document.createElement('button');
      b.textContent = d.label || d.dashboardId;
      b.className = 'tab';
      b.onclick = () => select(d);
      el.tabs.appendChild(b);
      if(i===0) select(d);
    });
  }
  function select(d){
    [...el.tabs.children].forEach(btn => btn.classList.remove('active'));
    const idx = [...el.tabs.children].findIndex(b => (b.textContent === (d.label||d.dashboardId)));
    if(idx >= 0) el.tabs.children[idx].classList.add('active');
    el.status.textContent = d.dashboardId;
    el.frame.src = d.embed?.url || '';
  }

  fetch(`${API}/registry/dashboards?tenant=demo`)
    .then(r => r.json())
    .then(arr => Array.isArray(arr) ? arr : [])
    .then(renderTabs)
    .catch(err => {
      el.status.textContent = 'Failed to load dashboards';
      console.error('mini viewer:', err);
    });
})();
