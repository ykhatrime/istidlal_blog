from app import create_app
from config import TestingConfig


def test_app_factory_creates_app():
    app = create_app(TestingConfig)
    assert app is not None
    assert app.config["TESTING"] is True


def test_core_routes_are_registered():
    app = create_app(TestingConfig)
    rules = {rule.endpoint for rule in app.url_map.iter_rules()}
    assert "main.home" in rules
    assert "main.services" in rules
    assert "auth.login" in rules
    assert "admin.dashboard" in rules


def test_services_page_renders():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        response = client.get("/ar/services")
    assert response.status_code == 200
    assert "الخدمات".encode() in response.data


def test_internal_analytics_tracks_public_page_views():
    from app.extensions import db
    from app.models.page_view import PageView

    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        response = client.get("/ar/services")
        assert response.status_code == 200
    with app.app_context():
        assert PageView.query.count() == 1
        view = PageView.query.first()
        assert view.path == "/ar/services"
        assert view.page_type == "services"
        assert view.ip_hash
        assert len(view.ip_hash) == 64
