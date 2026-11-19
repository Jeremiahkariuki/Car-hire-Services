/* RideKari — Drag & Drop Image Widget JS
   Handles: drag/drop, file-picker, paste (Ctrl+V), live preview, clear
*/
(function () {
  'use strict';

  /* ── Helpers ──────────────────────────────────────── */
  function fmt(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function showPreview(widgetId, file) {
    if (!file || !file.type.startsWith('image/')) return;
    var reader = new FileReader();
    reader.onload = function (e) {
      var previewWrap = document.getElementById('rk-dnd-preview-' + widgetId);
      var previewImg  = document.getElementById('rk-dnd-pimg-'    + widgetId);
      var previewName = document.getElementById('rk-dnd-pname-'   + widgetId);
      var previewSize = document.getElementById('rk-dnd-psize-'   + widgetId);
      var zone        = document.getElementById('rk-dnd-zone-'    + widgetId);
      var b64Input    = document.getElementById(widgetId + '_b64');
      if (b64Input) {
        b64Input.value = e.target.result;
      }
      if (!previewWrap) return;
      previewImg.src       = e.target.result;
      previewName.textContent = file.name;
      previewSize.textContent = fmt(file.size);
      previewWrap.style.display = 'flex';
      zone.style.display = 'none';
    };
    reader.readAsDataURL(file);
  }

  /* Assign a File to the hidden <input type=file> via DataTransfer */
  function assignFile(input, file) {
    try {
      var dt = new DataTransfer();
      dt.items.add(file);
      input.files = dt.files;
    } catch (e) {
      /* Fallback: base64 input guarantees submission even if DataTransfer throws */
    }
  }

  /* ── Global clear function (called from onclick in widget HTML) ── */
  window.rkDndClear = function (widgetId) {
    var input       = document.getElementById(widgetId);
    var b64Input    = document.getElementById(widgetId + '_b64');
    var previewWrap = document.getElementById('rk-dnd-preview-' + widgetId);
    var zone        = document.getElementById('rk-dnd-zone-'    + widgetId);
    if (input)       { input.value = ''; }
    if (b64Input)    { b64Input.value = ''; }
    if (previewWrap) { previewWrap.style.display = 'none'; }
    if (zone)        { zone.style.display = 'flex'; }
  };

  /* ── Init one widget ──────────────────────────────── */
  function initWidget(wrapper) {
    var widgetId = wrapper.id.replace('rk-dnd-', '');
    var input    = document.getElementById(widgetId);
    var zone     = document.getElementById('rk-dnd-zone-'    + widgetId);
    if (!input || !zone) return;

    /* File picker change */
    input.addEventListener('change', function () {
      if (input.files && input.files[0]) {
        showPreview(widgetId, input.files[0]);
      }
    });

    /* Drag & Drop on zone */
    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add('rk-drag-over');
    });
    zone.addEventListener('dragleave', function (e) {
      e.preventDefault();
      zone.classList.remove('rk-drag-over');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('rk-drag-over');
      var files = e.dataTransfer && e.dataTransfer.files;
      if (files && files[0]) {
        assignFile(input, files[0]);
        showPreview(widgetId, files[0]);
      }
    });
  }

  /* ── Clipboard paste anywhere on page ─────────────── */
  document.addEventListener('paste', function (e) {
    var items = (e.clipboardData || window.clipboardData).items;
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.startsWith('image/')) {
        var file = items[i].getAsFile();
        /* Apply to the first visible dnd widget */
        var wrapper = document.querySelector('.rk-dnd-wrapper');
        if (!wrapper) return;
        var widgetId = wrapper.id.replace('rk-dnd-', '');
        var input    = document.getElementById(widgetId);
        if (!input) return;
        assignFile(input, file);
        showPreview(widgetId, file);

        /* Show a small toast */
        showPasteToast();
        break;
      }
    }
  });

  function showPasteToast() {
    var t = document.createElement('div');
    t.textContent = '📋 Image pasted from clipboard!';
    t.style.cssText = [
      'position:fixed', 'bottom:28px', 'right:28px', 'z-index:9999',
      'background:#1e3a5f', 'border:1px solid rgba(59,130,246,0.4)',
      'color:#93c5fd', 'font-size:13px', 'font-weight:700',
      'padding:12px 20px', 'border-radius:12px',
      'box-shadow:0 8px 32px rgba(0,0,0,0.5)',
      'animation:rkFadeIn 0.3s ease',
      'transition:opacity 0.4s ease',
    ].join(';');
    document.body.appendChild(t);
    setTimeout(function () { t.style.opacity = '0'; }, 2200);
    setTimeout(function () { t.remove(); }, 2700);
  }

  /* ── Boot on DOMContentLoaded ─────────────────────── */
  function boot() {
    document.querySelectorAll('.rk-dnd-wrapper').forEach(initWidget);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
