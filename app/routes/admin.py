from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.utils.supabase import get_supabase
from app.charts import generate_chart_data

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        flash('Senha incorreta.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('public.initial'))

@bp.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    supabase = get_supabase()
    polls = supabase.table('polls').select('*').execute().data
    data = []
    for p in polls:
        votes = supabase.table('votes').select('*').eq('poll_id', p['id']).execute().data
        data.append({'poll': p, 'chart': generate_chart_data(votes)})
    return render_template('dashboard.html', polls=data)

@bp.route('/new', methods=['GET', 'POST'])
def new_poll():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        opts = [o.strip() for o in request.form['options'].split('\n') if o.strip()]
        codes = [c.strip() for c in request.form['codes'].split(',') if c.strip()]
        supabase = get_supabase()
        supabase.table('polls').insert({'title': title, 'description': desc, 'options': opts, 'allowed_codes': codes, 'is_active': True}).execute()
        return redirect(url_for('admin.dashboard'))
    return render_template('new_poll.html')