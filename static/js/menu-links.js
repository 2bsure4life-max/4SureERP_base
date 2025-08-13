document.addEventListener('DOMContentLoaded', () => {
  const map = {
    'btn-sales': '/modules/sales/sales.html',
    'btn-accounting': '/modules/accounting/accounting.html',

    // Placeholders for now — point these wherever you want later:
    'btn-operations': '/owner',
    'btn-recruitment': '/owner',
    'btn-reports': '/owner',
    'btn-settings': '/owner'
  };

  Object.entries(map).forEach(([id, url]) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', () => { window.location.href = url; });
  });
});
