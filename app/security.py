import re
from urllib.parse import urlparse

import bleach


ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'blockquote',
    'ul', 'ol', 'li', 'h2', 'h3', 'h4', 'a', 'img', 'figure',
    'figcaption', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'code', 'pre', 'span', 'div'
]

ALLOWED_HTML_ATTRIBUTES = {
    '*': ['class', 'dir'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'loading', 'decoding'],
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
}

ALLOWED_HTML_PROTOCOLS = ['http', 'https', 'mailto']
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def clean_html(value):
    """Clean rich HTML before saving it to the database."""
    if not value:
        return ''
    cleaned = bleach.clean(
        value,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=ALLOWED_HTML_PROTOCOLS,
        strip=True,
        strip_comments=True,
    )
    cleaned = bleach.linkify(cleaned, skip_tags=['pre', 'code'])
    # Hardening for links opened in new tabs.
    cleaned = cleaned.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
    return cleaned.strip()


def clean_text(value, max_length=None):
    """Remove all HTML from a plain text field and trim length."""
    text = bleach.clean(value or '', tags=[], attributes={}, strip=True, strip_comments=True).strip()
    if max_length and len(text) > max_length:
        return text[:max_length]
    return text


def normalize_email(value, required=False):
    email = clean_text(value, 180).lower()
    if not email and not required:
        return ''
    if not EMAIL_RE.match(email):
        return None
    return email


def safe_external_url(value):
    """Keep only http/https URLs for public links."""
    url = clean_text(value, 255)
    if not url:
        return ''
    parsed = urlparse(url)
    if parsed.scheme not in {'http', 'https'}:
        return ''
    return url
