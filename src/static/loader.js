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
  var i = 0;

  document.body.style.overflow = 'hidden';

  function tick() {
    // Segna lo step precedente come OK
    if (i > 0) {
      var prev = log.lastElementChild;
      if (prev) prev.innerHTML = steps[i - 1] + ' <span class="ok">OK</span>';
    }

    var progress = Math.round(i / steps.length * 100);
    fill.style.width = progress + '%';
    pct.textContent  = progress + '%';

    if (i >= steps.length) {
      // Tutto caricato: fade out
      setTimeout(function () {
        el.classList.add('nascosto');
        el.addEventListener('transitionend', function () {
          el.remove();
          document.body.style.overflow = '';
        }, { once: true });
      }, 300);
      return;
    }

    var line = document.createElement('div');
    line.textContent = steps[i] + '...';
    log.appendChild(line);
    i++;
    setTimeout(tick, 250 + Math.random() * 200);
  }

  tick();
})();
