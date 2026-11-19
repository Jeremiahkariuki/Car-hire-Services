"""
RideKari — Drag-and-Drop Image Upload Widget
Replaces the default ClearableFileInput with a modern drop zone.
"""
from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class DragDropImageWidget(ClearableFileInput):
    """
    A file input widget that renders a drag-and-drop zone with:
    - Live image preview on file select / drop
    - Paste-from-clipboard support
    - Current image display (when editing)
    - Clear checkbox
    """
    template_name = None  # We override render() fully

    def render(self, name, value, attrs=None, renderer=None):
        # Build the current-image block when an image is already saved
        current_img_html = ''
        if value and hasattr(value, 'url'):
            current_img_html = format_html(
                '<div class="rk-dnd-current">'
                '  <img src="{}" class="rk-dnd-current-img" alt="Current image">'
                '  <div class="rk-dnd-current-label">Current image</div>'
                '  <label class="rk-dnd-clear">'
                '    <input type="checkbox" name="{}-clear" id="{}-clear-id"> '
                '    Remove image'
                '  </label>'
                '</div>',
                value.url, name, name
            )

        widget_id = attrs.get('id', f'id_{name}') if attrs else f'id_{name}'

        return format_html(
            '''
            <div class="rk-dnd-wrapper" id="rk-dnd-{widget_id}">
              {current_img_html}
              <div class="rk-dnd-zone" id="rk-dnd-zone-{widget_id}">
                <div class="rk-dnd-icon">📸</div>
                <div class="rk-dnd-title">Drag &amp; drop your photo here</div>
                <div class="rk-dnd-sub">or click to browse — also supports paste (Ctrl+V)</div>
                <div class="rk-dnd-formats">JPG · PNG · WEBP · up to 10 MB</div>
                <input type="file" name="{name}" id="{widget_id}"
                       accept="image/*" class="rk-dnd-input">
              </div>
              <input type="hidden" name="{name}_b64" id="{widget_id}_b64" value="">
              <div class="rk-dnd-preview-wrap" id="rk-dnd-preview-{widget_id}" style="display:none;">
                <img class="rk-dnd-preview-img" id="rk-dnd-pimg-{widget_id}" src="" alt="Preview">
                <div class="rk-dnd-preview-info">
                  <span class="rk-dnd-preview-name" id="rk-dnd-pname-{widget_id}"></span>
                  <span class="rk-dnd-preview-size" id="rk-dnd-psize-{widget_id}"></span>
                  <button type="button" class="rk-dnd-remove-btn"
                          onclick="rkDndClear('{widget_id}')">✕ Remove / Change</button>
                </div>
              </div>
            </div>
            ''',
            widget_id=widget_id,
            current_img_html=current_img_html,
            name=name,
        )

    class Media:
        css = {'all': ('admin/css/dnd_widget.css',)}
        js = ('admin/js/dnd_widget.js',)
