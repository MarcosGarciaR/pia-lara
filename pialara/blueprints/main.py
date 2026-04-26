from flask import (
    Blueprint, render_template, redirect, url_for, session, request, current_app
)
from flask_login import login_required

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('main/index.html')

@bp.route('/set_language')
def set_language():
    lang = request.args.get('lang')
    if lang in current_app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))