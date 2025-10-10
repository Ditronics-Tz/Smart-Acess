from rest_framework.renderers import BaseRenderer

class CSVRenderer(BaseRenderer):
    media_type = '*/*'  # Accept any media type to avoid 406 errors
    format = 'csv'
    charset = 'utf-8'
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, str):
            return data.encode(self.charset)
        if hasattr(data, 'content'):
            return data.content
        return str(data).encode(self.charset)

    def get_rendered_headers(self, renderer_context):
        headers = super().get_rendered_headers(renderer_context)
        headers['Content-Type'] = 'text/csv; charset=utf-8'
        headers['Content-Disposition'] = 'attachment; filename=staff_upload_template.csv'
        return headers