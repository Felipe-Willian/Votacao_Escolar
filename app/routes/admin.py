from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.utils.supabase import get_supabase
from app.charts import generate_chart_data
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/login', methods=['GET','POST'])
def login():
    if session.get('admin'): return redirect(url_for('admin.dashboard'))
    if session.get('role')!='docente': return redirect(url_for('public.initial'))
    if request.method=='POST':
        if request.form['password']=='univesp2025': session['admin']=True; return redirect(url_for('admin.dashboard'))
        flash('Senha incorreta','danger')
    return render_template('login.html')

@bp.route('/logout')
def logout(): session.clear(); return redirect(url_for('public.initial'))

@bp.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('admin.login'))
    sb = get_supabase()
    polls = sb.table('polls').select('*').execute().data
    ids = [p['id'] for p in polls]
    votes = sb.table('votes').select('*').in_('poll_id',ids).execute().data if ids else []
    by_poll={}
    for v in votes: by_poll.setdefault(v['poll_id'],[]).append(v)
    data=[]
    for p in polls:
        chart=generate_chart_data(by_poll.get(p['id'],[]))
        data.append({'poll':p,'chart':chart})
    return render_template('dashboard.html', polls=data)

@bp.route('/new', methods=['GET', 'POST'])
def new_poll():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    sb = get_supabase()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        options = request.form.getlist('options_list')
        class_ids = request.form.getlist('class_ids')
        expiration = request.form['expiration_date']

        # Gera todos os códigos permitidos a partir das classes selecionadas
        all_allowed = []
        for cid in class_ids:
            cls = sb.table('classes').select('student_numbers').eq('id', cid).single().execute().data
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

    # GET: carrega classes para o select multiple
    classes = sb.table('classes').select('id,title').order('title', desc=False).execute().data
    return render_template('new_poll.html', classes=classes)

@bp.route('/delete_poll/<poll_id>')
def delete_poll(poll_id):
    if not session.get('admin'): return redirect(url_for('admin.login'))
    get_supabase().table('polls').delete().eq('id',poll_id).execute()
    return redirect(url_for('admin.dashboard'))

@bp.route('/edit_poll/<poll_id>', methods=['GET', 'POST'])
def edit_poll(poll_id):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    sb = get_supabase()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        options = request.form.getlist('options_list')
        class_ids = request.form.getlist('class_ids')
        expiration = request.form['expiration_date']

        all_allowed = []
        for cid in class_ids:
            cls = sb.table('classes').select('student_numbers').eq('id', cid).single().execute().data
            for num in cls['student_numbers']:
                all_allowed.append(f"{cid}-{str(num).zfill(2)}")

        sb.table('polls').update({
            'title': title,
            'description': description,
            'options': options,
            'allowed_codes': all_allowed,
            'expiration_date': expiration
        }).eq('id', poll_id).execute()
        flash('Votação atualizada.', 'success')
        return redirect(url_for('admin.dashboard'))

    # GET: busca enquete e as classes
    poll = sb.table('polls').select('*').eq('id', poll_id).single().execute().data
    classes = sb.table('classes').select('id,title').order('title', desc=False).execute().data
    # identifica quais classes já estão selecionadas (do allowed_codes)
    selected_classes = sorted({code.split('-')[0] for code in poll['allowed_codes']})
    return render_template('new_poll.html',
                           poll=poll,
                           classes=classes,
                           selected_classes=selected_classes)

@bp.route('/classes', methods=['GET', 'POST'])
def classes():
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    sb = get_supabase()

    if request.method == 'POST':
        title = request.form['title'].strip()
        nums = [int(n) for n in request.form.getlist('nums')]
        exists_list = sb.table('classes').select('id').eq('title', title).execute().data
        exists = len(exists_list) > 0
        if exists:
            flash('Título de classe já existe.', 'warning')
        else:
            sb.table('classes').insert({
                'title': title,
                'student_numbers': nums
            }).execute()
            flash('Classe criada.', 'success')
        return redirect(url_for('admin.classes'))

    classes = sb.table('classes').select('*').order('title', desc=False).execute().data
    edit = None
    return render_template('classes.html', classes=classes, edit=edit)

@bp.route('/classes/edit/<class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    sb = get_supabase()

    if request.method == 'POST':
        title = request.form['title'].strip()
        nums = [int(n) for n in request.form.getlist('nums')]
        sb.table('classes').update({
            'title': title,
            'student_numbers': nums
        }).eq('id', class_id).execute()
        flash('Classe atualizada.', 'success')
        return redirect(url_for('admin.classes'))

    cls_list = sb.table('classes').select('*').eq('id', class_id).execute().data
    cls = cls_list[0] if cls_list else None
    # ao renderizar, passamos 'edit' para pre‑preencher o form
    classes = sb.table('classes').select('*').order('title', desc=False).execute().data
    return render_template('classes.html', classes=classes, edit=cls)

@bp.route('/classes/delete/<class_id>')
def delete_class(class_id):
    if not session.get('admin'):
        return redirect(url_for('admin.login'))
    get_supabase().table('classes').delete().eq('id', class_id).execute()
    flash('Classe excluída.', 'success')
    return redirect(url_for('admin.classes'))