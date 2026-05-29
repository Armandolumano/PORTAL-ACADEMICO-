from flask import Flask, request, session, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
import sqlite3
app = Flask(__name__)
app.secret_key = 'chave_secreta_123'
from datetime import timedelta
app.permanent_session_lifetime = timedelta(minutes=1)
bcrypt = Bcrypt(app)
@app.after_request
def adicionar_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net"
    return response
#PRIMEIRO PASSO PARA A COREECÃO DE LIMITE DE TENTATIVA
#-----------------------------------------------------
import time
# Dicionário para guardar tentativas de login
tentativas = {}
def verificar_tentativas(ip):
    agora = time.time()
    if ip not in tentativas:
        tentativas[ip] = []
    tentativas[ip] = [t for t in tentativas[ip] if agora - t < 60]
    if len(tentativas[ip]) >= 3:
        tempo_restante = int(60 - (agora - tentativas[ip][0]))
        return tempo_restante
    return 0

def registar_tentativa(ip):
    if ip not in tentativas:
        tentativas[ip] = []
    tentativas[ip].append(time.time())
#------------------------------------------------------
def get_db():
    conn = sqlite3.connect('portal.db')
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------------------------
# PÁGINA DE LOGIN — VULNERÁVEL A SQL INJECTION
# -----------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        ip = request.remote_addr

        tempo_restante = verificar_tentativas(ip)
        if tempo_restante > 0:
            return render_template('login.html', tempo_restante=tempo_restante)
        conn = get_db()
        cursor = conn.cursor()

        # CORRIGIDO — prepared statements JUNTOS COM O ASH OU SEJA TEMOS O SQL INJECTION CORRIGIDO E AUTENTICAÇÃO COM ASH
        query = "SELECT * FROM alunos WHERE nome = ?"
        cursor.execute(query, (nome,))
        aluno = cursor.fetchone()
        conn.close()

        #AUTENTICAO COM ASHE--------------------------------------------------
        if aluno and bcrypt.check_password_hash(aluno['senha'], senha):
            session.permanent = True
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome']
            return redirect(url_for('perfil'))
        else:
            registar_tentativa(ip)
            erro = 'Username ou senha incorrectos.'
    return render_template('login.html', erro=erro)

# -----------------------------------------------
# PÁGINA DE PERFIL — VULNERÁVEL A XSS
# -----------------------------------------------
def perfil():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos WHERE id = ?", (session['aluno_id'],))
    aluno = cursor.fetchone()
    conn.close()

    return render_template('perfil.html', aluno=aluno)

# -----------------------------------------------
# PÁGINA DE NOTAS — VULNERÁVEL A IDOR
# -----------------------------------------------
@app.route('/notas')
def notas():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    # VULNERÁVEL — usa o ID da URL sem verificar
    aluno_id = request.args.get('aluno_id', session['aluno_id'])
    if int(aluno_id) != int(session['aluno_id']):
        return "Acesso negado. Não tens permissão para ver estes dados.", 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas WHERE aluno_id = ?", (aluno_id,))
    notas = cursor.fetchall()
    cursor.execute("SELECT nome FROM alunos WHERE id = ?", (aluno_id,))
    aluno = cursor.fetchone()
    conn.close()

    return render_template('notas.html', notas=notas, aluno=aluno)

# -----------------------------------------------
# PÁGINA DE PROPINAS — VULNERÁVEL A IDOR
# -----------------------------------------------
@app.route('/propinas')
def propinas():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    # VULNERÁVEL — usa o ID da URL sem verificar
    aluno_id = request.args.get('aluno_id', session['aluno_id'])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM propinas WHERE aluno_id = ?", (aluno_id,))
    propinas = cursor.fetchall()
    cursor.execute("SELECT nome FROM alunos WHERE id = ?", (aluno_id,))
    aluno = cursor.fetchone()
    conn.close()

    return render_template('propinas.html', propinas=propinas, aluno=aluno)

# -----------------------------------------------
# LOGOUT
# -----------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

    # -----------------------------------------------
# ACTUALIZAR NOME — VULNERÁVEL A XSS
# -----------------------------------------------
@app.route('/actualizar_nome', methods=['POST'])
def actualizar_nome():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))
    
    novo_nome = request.form['novo_nome']
    session['nome_apresentacao'] = novo_nome
    return redirect(url_for('perfil'))

@app.route('/perfil')
def perfil():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos WHERE id = ?", (session['aluno_id'],))
    aluno = cursor.fetchone()
    conn.close()

    nome_apresentacao = session.get('nome_apresentacao', None)
    return render_template('perfil.html', aluno=aluno, nome_apresentacao=nome_apresentacao)

if __name__ == '__main__':
    app.run(debug=True)