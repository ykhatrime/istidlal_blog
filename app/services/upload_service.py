"""Upload validation and storage services."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import current_app, flash, request
from werkzeug.utils import secure_filename

from app.audit import log_admin_action

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
BLOCKED_MIME_TYPES = {'image/svg+xml'}


def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_image(file_storage, subfolder: str = 'content') -> str | None:
    """Save an uploaded image under app/static/uploads and return the relative static path."""
    if not file_storage or not file_storage.filename:
        return None

    lang = (request.view_args or {}).get('lang', current_app.config.get('DEFAULT_LANG', 'ar'))
    if not allowed_image(file_storage.filename) or file_storage.mimetype in BLOCKED_MIME_TYPES:
        flash(
            'صيغة الصورة غير مدعومة. استخدم PNG/JPG/JPEG/GIF/WEBP فقط. تم منع SVG لأسباب أمنية.'
            if lang == 'ar'
            else 'Unsupported image type. Use PNG/JPG/JPEG/GIF/WEBP only. SVG uploads are blocked for security.',
            'error',
        )
        return None

    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower()
    filename = f'{uuid4().hex}.{ext}'
    upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_dir / filename)
    log_admin_action('upload_image', 'Upload', None, f'Uploaded {subfolder}/{filename}')
    return f'uploads/{subfolder}/{filename}'
