from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from app.utils.supabase import get_supabase

bp = Blueprint('public', __name__)

@bp.route('/')
def initial():
    session.pop('role', None)
    return render_template('initial.html')

@bp.route('/role/docente')
def role_docente():
    session.clear()
    session['role'] = 'docente'
    return redirect(url_for('admin.dashboard'))

@bp.route('/role/aluno')
def role_aluno():
    session.clear()
    session['role'] = 'aluno'
    return redirect(url_for('public.index'))

@bp.route('/votacoes')
def index():
    if session.get('role') not in ('aluno',) and not session.get('admin'):
        return redirect(url_for('public.initial'))
    sb = get_supabase()
    # busca todas as enquetes
    polls = sb.table('polls')\
              .select('*')\
              .order('expiration_date', desc=False)\
              .order('is_active', desc=False)\
              .execute().data
    # busca todos os votos num único batch
    ids = [p['id'] for p in polls]
    votes = sb.table('votes').select('*').in_('poll_id', ids).execute().data if ids else []
    # agrupa votos por poll_id
    by_poll = {}
    for v in votes:
        by_poll.setdefault(v['poll_id'], []).append(v)
    # atribui lista de votos a cada poll
    for p in polls:
        p['votes'] = by_poll.get(p['id'], [])
    return render_template('index.html', polls=polls)

@bp.route('/new_poll', methods=['GET', 'POST'])
def new_poll():
    # Apenas docentes/admins podem criar
    if session.get('role') != 'docente' and not session.get('admin'):
        return redirect(url_for('public.initial'))
    sb = get_supabase()

    if request.method == 'POST':
        title       = request.form['title']
        description = request.form['description']
        options     = request.form.getlist('options_list')        # dinâmico
        class_ids   = request.form.getlist('class_ids')          # selecionadas
        expiration  = request.form['expiration_date']

        # Gera todos os códigos válidos (classeID-numero) a partir das classes
        all_allowed = []
        for cid in class_ids:
            cls = sb.table('classes')\
                    .select('student_numbers')\
                    .eq('id', cid)\
                    .single().execute().data
            for num in cls['student_numbers']:
                all_allowed.append(f"{cid}-{str(num).zfill(2)}")

        sb.table('polls').insert({
            'title': title,
            'description': description,
            'options': options,
            'allowed_codes': all_allowed,
            'is_active': True,
            'expiration_date': expiration
        }).execute()
        flash('Votação criada com sucesso.', 'success')
        return redirect(url_for('admin.dashboard'))

    # GET: carrega enquetes e classes existentes para o formulário
    classes = sb.table('classes')\
                .select('id,title')\
                .order('title', desc=False)\
                .execute().data
    return render_template('new_poll.html', classes=classes)

@bp.route('/vote/<poll_id>', methods=['GET', 'POST'])
def vote(poll_id):
    # Apenas alunos podem votar
    if session.get('role') != 'aluno':
        return redirect(url_for('public.initial'))

    sb = get_supabase()
    # Busca a enquete selecionada
    poll = sb.table('polls')\
             .select('*')\
             .eq('id', poll_id)\
             .single().execute().data

    # 1) Extrai IDs das classes permitidas (antes do '-')
    class_ids = sorted({code.rsplit('-', 1)[0] for code in poll['allowed_codes']})
    # 2) Busca títulos dessas classes
    classes = sb.table('classes')\
                .select('id,title')\
                .in_('id', class_ids)\
                .order('title', desc=False)\
                .execute().data

    if request.method == 'POST':
        code   = request.form['code']
        option = request.form['option']
        if code not in poll['allowed_codes']:
            flash('Votação não liberada para este aluno.', 'danger')
            return render_template('vote.html', poll=poll, classes=classes)
        # grava voto
        sb.table('votes').insert({
            'poll_id': poll_id,
            'code': code,
            'option': option
        }).execute()
        return render_template('thanks.html')

    # GET: mostra formulário de validação + votação
    return render_template('vote.html', poll=poll, classes=classes)
