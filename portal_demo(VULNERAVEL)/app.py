from flask import Flask, request, session, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_secreta_123'

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

        conn = get_db()
        cursor = conn.cursor()

        # VULNERÁVEL — concatenação directa do input
        query = "SELECT * FROM alunos WHERE nome = '" + nome + "' AND senha = '" + senha + "'"
        cursor.execute(query)
        aluno = cursor.fetchone()
        conn.close()

        if aluno:
            session['aluno_id'] = aluno['id']
            session['aluno_nome'] = aluno['nome']
            return redirect(url_for('perfil'))
        else:
            erro = 'Username ou senha incorrectos.'

    return render_template('login.html', erro=erro)

# -----------------------------------------------
# ACTUALIZAR NOME — VULNERÁVEL A XSS
# -----------------------------------------------
@app.route('/actualizar_nome', methods=['POST'])
def actualizar_nome():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    novo_nome = request.form['novo_nome']
    # VULNERÁVEL — guarda o input sem sanitizar
    session['nome_apresentacao'] = novo_nome
    return redirect(url_for('perfil'))

# -----------------------------------------------
# PÁGINA DE PERFIL — VULNERÁVEL A XSS
# -----------------------------------------------
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

# -----------------------------------------------
# PÁGINA DE NOTAS — VULNERÁVEL A IDOR
# -----------------------------------------------
@app.route('/notas')
def notas():
    if 'aluno_id' not in session:
        return redirect(url_for('login'))

    # VULNERÁVEL — usa o ID da URL sem verificar
    aluno_id = request.args.get('aluno_id', session['aluno_id'])

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)