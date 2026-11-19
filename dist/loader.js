(function () {
  var el = document.getElementById('loader');
  if (!el) return;

  // 1. Riconosci se è un ricaricamento (F5 / Cmd+R)
  var isReload = false;
  try {
    var nav = performance.getEntriesByType('navigation')[0];
    if (nav) {
      isReload = (nav.type === 'reload');
    } else if (performance.navigation) {
      isReload = (performance.navigation.type === 1);
    }
  } catch (e) {}

  // 2. Riconosci se proviene da una navigazione interna (altra pagina del sito)
  var isInternalNav = false;
  if (document.referrer) {
    try {
      var ref = new URL(document.referrer);
      if (ref.origin === window.location.origin) {
        isInternalNav = true;
      }
    } catch (e) {}
  }

  var alreadyShown = sessionStorage.getItem('portfolio_loader_shown');

  // Se è navigazione interna E non è un reload E è già stato mostrato in questa sessione: salta!
  if (isInternalNav && alreadyShown && !isReload) {
    el.remove();
    return;
  }

  // Segna che è stato mostrato per la sessione corrente
  try {
    sessionStorage.setItem('portfolio_loader_shown', '1');
  } catch (e) {}

  var log  = document.getElementById('loaderLog');
  var fill = document.getElementById('loaderFill');
  var pct  = document.getElementById('loaderPct');
  if (!log || !fill || !pct) return;

  var steps = [
    'Creating lobby',
    'Joining lobby',
    'Loading assets',
    'Loading works',
    'All systems go'
  ];

  document.body.style.overflow = 'hidden';

  // Pre-crea tutte le 5 righe per bloccare l'altezza ed evitare qualsiasi reflow o layout shift
  log.innerHTML = '';
  var rowElements = [];
  for (var s = 0; s < steps.length; s++) {
    var riga = document.createElement('div');
    riga.className = 'loader-riga';
    var label = document.createElement('span');
    label.className = 'step-label';
    label.textContent = steps[s];
    var status = document.createElement('span');
    status.className = 'step-status';
    status.textContent = '...';
    riga.appendChild(label);
    riga.appendChild(status);
    log.appendChild(riga);
    rowElements.push({ riga: riga, status: status });
  }

  var i = 0;

  function tick() {
    if (i > 0 && i - 1 < rowElements.length) {
      rowElements[i - 1].status.textContent = 'OK';
      rowElements[i - 1].status.classList.add('ok');
    }

    var progress = Math.round((i / steps.length) * 100);
    fill.style.width = progress + '%';
    pct.textContent  = progress + '%';

    if (i >= steps.length) {
      setTimeout(function () {
        el.classList.add('nascosto');
        el.addEventListener('transitionend', function () {
          el.remove();
          document.body.style.overflow = '';
        }, { once: true });
      }, 350);
      return;
    }

    rowElements[i].riga.classList.add('visibile');
    i++;
    setTimeout(tick, 260 + Math.random() * 160);
  }

  setTimeout(tick, 100);
})();
