from flask import Blueprint, render_template, request, redirect, flash
from app.utils.supabase import get_supabase

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    supabase = get_supabase()
    polls = supabase.table('polls').select('*').eq('is_active', True).execute().data
    return render_template('index.html', polls=polls)

@bp.route('/vote/<poll_id>', methods=['GET', 'POST'])
def vote(poll_id):
    supabase = get_supabase()
    poll = supabase.table('polls').select('*').eq('id', poll_id).single().execute().data

    if request.method == 'POST':
        code = request.form['code']
        option = request.form['option']

        if code not in poll['allowed_codes']:
            flash('Código inválido.', 'danger')
            return redirect(request.url)

        existing = supabase.table('votes').select('*')\
            .eq('poll_id', poll_id).eq('code', code).execute().data
        if existing:
            flash('Você já votou.', 'warning')
            return redirect(request.url)

        supabase.table('votes').insert({
            'poll_id': poll_id,
            'code': code,
            'option': option
        }).execute()
        return render_template('thanks.html')

    return render_template('vote.html', poll=poll)