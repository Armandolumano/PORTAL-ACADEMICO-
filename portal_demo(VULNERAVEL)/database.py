import sqlite3

def criar_base_dados():
    conn = sqlite3.connect('portal.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            curso TEXT NOT NULL,
            ano INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina TEXT NOT NULL,
            nota REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS propinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            valor REAL NOT NULL,
            pago INTEGER NOT NULL
        )
    ''')

    cursor.execute("DELETE FROM alunos")
    cursor.execute("DELETE FROM notas")
    cursor.execute("DELETE FROM propinas")

    alunos = [
        (1, 'joao', 'joao@uni.ao', '1234', 'Informatica', 2),
        (2, 'maria', 'maria@uni.ao', 'abcd', 'Gestao', 3),
        (3, 'pedro', 'pedro@uni.ao', 'pass', 'Direito', 1),
    ]
    cursor.executemany(
        "INSERT OR REPLACE INTO alunos (id, nome, email, senha, curso, ano) VALUES (?,?,?,?,?,?)",
        alunos
    )

    notas = [
        (1, 'Matematica', 14),
        (1, 'Programacao', 17),
        (1, 'Base de Dados', 15),
        (2, 'Matematica', 12),
        (2, 'Gestao Empresarial', 18),
        (3, 'Direito Civil', 16),
        (3, 'Direito Penal', 13),
    ]
    cursor.executemany(
        "INSERT INTO notas (aluno_id, disciplina, nota) VALUES (?,?,?)",
        notas
    )

    propinas = [
        (1, 'Janeiro 2025', 15000, 1),
        (1, 'Fevereiro 2025', 15000, 1),
        (1, 'Marco 2025', 15000, 0),
        (2, 'Janeiro 2025', 15000, 1),
        (2, 'Fevereiro 2025', 15000, 0),
        (3, 'Janeiro 2025', 15000, 1),
    ]
    cursor.executemany(
        "INSERT INTO propinas (aluno_id, mes, valor, pago) VALUES (?,?,?,?)",
        propinas
    )

    conn.commit()
    conn.close()
    print("Base de dados criada com sucesso!")

criar_base_dados()