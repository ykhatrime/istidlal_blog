from flask import current_app, request, session

from app.extensions import db
from app.models.audit_log import AuditLog
from app.utils.request_utils import client_ip


def log_admin_action(action, entity_type=None, entity_id=None, details=None):
    """Best-effort audit logging. It should never break the primary user action."""
    try:
        db.session.add(AuditLog(
            user_id=session.get('user_id'),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=client_ip(),
        ))
    except Exception as exc:  # pragma: no cover - defensive only
        current_app.logger.warning('Audit log skipped: %s', exc)
