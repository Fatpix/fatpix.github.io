(function () {
  var steps = [
    'Creating lobby',
    'Joining lobby',
    'Loading assets',
    'Loading works',
    'All systems go'
  ];
  var log  = document.getElementById('loaderLog');
  var fill = document.getElementById('loaderFill');
  var pct  = document.getElementById('loaderPct');
  var el   = document.getElementById('loader');
  if (!log || !fill || !pct || !el) return;

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

  // Piccolo timeout per sincronizzare il rendering iniziale
  setTimeout(tick, 100);
})();
