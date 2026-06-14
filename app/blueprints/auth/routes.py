from datetime import datetime
import random
import time

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from app.audit import log_admin_action
from app.extensions import db, limiter
from app.models.user import User
from app.services.permission_service import login_required

from . import auth_bp

MAX_LOGIN_ATTEMPTS = 5
LOCK_SECONDS = 10 * 60


def _new_login_challenge():
    """Create a simple server-side human verification question."""
    a = random.randint(2, 9)
    b = random.randint(1, 9)
    session['captcha_answer'] = str(a + b)
    return f"{a} + {b}"


def _reset_login_challenge():
    session.pop('captcha_answer', None)


def _is_locked():
    lock_until = session.get('login_lock_until')
    if not lock_until:
        return False, 0

    remaining = int(lock_until - time.time())
    if remaining > 0:
        return True, remaining

    session.pop('login_lock_until', None)
    session['login_attempts'] = 0
    return False, 0


def _register_failed_attempt():
    attempts = int(session.get('login_attempts', 0)) + 1
    session['login_attempts'] = attempts

    if attempts >= MAX_LOGIN_ATTEMPTS:
        session['login_lock_until'] = time.time() + LOCK_SECONDS


def _clear_failed_attempts():
    session.pop('login_attempts', None)
    session.pop('login_lock_until', None)


def _flash_security_error(lang, key='invalid'):
    messages = {
        'ar': {
            'invalid': 'بيانات الدخول غير صحيحة أو فشل التحقق الأمني.',
            'captcha': 'يرجى الإجابة على سؤال التحقق بشكل صحيح.',
            'locked': 'تم إيقاف محاولات الدخول مؤقتًا بسبب كثرة المحاولات. يرجى المحاولة لاحقًا.',
            'bot': 'تم رفض الطلب بسبب الاشتباه بأنه طلب آلي.',
            'inactive': 'هذا المستخدم غير مفعل. يرجى التواصل مع مدير النظام.',
        },
        'en': {
            'invalid': 'Invalid login details or security verification failed.',
            'captcha': 'Please answer the verification question correctly.',
            'locked': 'Login is temporarily locked because of too many attempts. Please try again later.',
            'bot': 'The request was rejected because it looks automated.',
            'inactive': 'This user is inactive. Please contact the system administrator.',
        }
    }
    flash(messages.get(lang, messages['ar']).get(key, messages['ar']['invalid']), 'danger')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('20 per hour', methods=['POST'])
@limiter.limit('5 per minute', methods=['POST'])
def login(lang):
    locked, remaining = _is_locked()

    if request.method == 'POST':
        if locked:
            _flash_security_error(lang, 'locked')
            challenge = _new_login_challenge()
            return render_template('auth/login.html', challenge=challenge, remaining=remaining)

        if request.form.get('website'):
            _register_failed_attempt()
            _flash_security_error(lang, 'bot')
            challenge = _new_login_challenge()
            return render_template('auth/login.html', challenge=challenge, remaining=0)

        expected_answer = session.get('captcha_answer', '')
        user_answer = request.form.get('captcha_answer', '').strip()
        if not expected_answer or user_answer != expected_answer:
            _register_failed_attempt()
            _flash_security_error(lang, 'captcha')
            challenge = _new_login_challenge()
            return render_template('auth/login.html', challenge=challenge, remaining=0)

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                _register_failed_attempt()
                _flash_security_error(lang, 'inactive')
                challenge = _new_login_challenge()
                return render_template('auth/login.html', challenge=challenge, remaining=0)

            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            user.last_login_at = datetime.utcnow()
            log_admin_action('login', 'User', user.id, f'User {user.username} logged in')
            db.session.commit()
            _clear_failed_attempts()
            _reset_login_challenge()
            return redirect(url_for('admin.dashboard', lang=lang))

        _register_failed_attempt()
        _flash_security_error(lang, 'invalid')

    locked, remaining = _is_locked()
    challenge = _new_login_challenge()
    return render_template('auth/login.html', challenge=challenge, remaining=remaining)


@auth_bp.route('/logout')
@login_required
def logout(lang):
    log_admin_action('logout', 'User', session.get('user_id'), f"User {session.get('username')} logged out")
    db.session.commit()
    session.clear()
    return redirect(url_for('main.home', lang=lang))
