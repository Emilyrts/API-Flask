from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
# Caminho absoluto para o banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///escola.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definição das tabelas
class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id', ondelete="SET NULL"), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    alunos = db.relationship('Aluno', backref='turma', lazy=True)

class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    observacoes = db.Column(db.Text)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)
    turma = db.relationship('Turma', backref='professores', foreign_keys=[turma_id])

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id', ondelete="SET NULL"), nullable=True)
    data_nascimento = db.Column(db.Date, nullable=False)
    nota_primeiro_semestre = db.Column(db.Float, nullable=True)
    nota_segundo_semestre = db.Column(db.Float, nullable=True)
    media_final = db.Column(db.Float, nullable=True)

with app.app_context():
    db.create_all()

#-----------ROTAS----------------------------------------------------
@app.route('/')
def home():
    return jsonify({"mensagem": "Sistema Escolar"}), 200

#Rota para os professores

#Criar um professor
@app.route('/professores', methods=['POST'])
def criar_professor():
    dados = request.json

    if "nome" not in dados or "idade" not in dados or "materia" not in dados:
        return jsonify({"erro": "Campos obrigatórios: nome, idade, materia"}), 400

    novo_professor = Professor(
        nome=dados['nome'],
        idade=dados['idade'],
        materia=dados['materia'],
        observacoes=dados.get('observacoes', '')
    )

    db.session.add(novo_professor)
    db.session.commit()

    return jsonify({
        "mensagem": "Professor cadastrado com sucesso!",
        "id": novo_professor.id 
    }), 201


#Listar professores
@app.route('/professores', methods=['GET'])
def listar_professores():
    professores = Professor.query.all()
    resultado = [
        {
            "id": p.id, 
            "nome": p.nome, 
            "idade": p.idade, 
            "materia": p.materia, 
            "turma": {
            "id": p.turma.id if p.turma else None,
            "descricao": p.turma.descricao if p.turma else None},
            "observacoes": p.observacoes
         }

        for p in professores
    ]
    return jsonify(resultado)


#Buscar Professor por ID
@app.route('/professores/<int:id>', methods=['GET'])
def buscar_professor(id):
    professor = db.session.get(Professor, id) 

    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404
    
    resultado = {
        "id": professor.id, 
        "nome": professor.nome, 
        "idade": professor.idade, 
        "materia": professor.materia, 
        "turma": [{"id": turma.id, "descricao": turma.descricao} for turma in (professor.turma or [])],
        "observacoes": professor.observacoes
    }

    return jsonify(resultado)


# Atualizar Professor
@app.route('/professores/<int:id>', methods=['POST'])
def atualizar_professor(id):

    professor = Professor.query.get_or_404(id, description="Professor não encontrado.")
    
    dados = request.json
    if not dados:
        return jsonify({"erro": "Dados não fornecidos"}), 400

    # Verificar se a turma existe antes de associá-la
    if 'turma_id' in dados:
        turma = Turma.query.get(dados['turma_id'])
        if not turma:
            return jsonify({"erro": "Turma não encontrada."}), 404
        professor.turma_id = dados['turma_id']

    professor.nome = dados.get('nome', professor.nome)
    professor.idade = dados.get('idade', professor.idade)
    professor.materia = dados.get('materia', professor.materia)
    professor.observacoes = dados.get('observacoes', professor.observacoes)

    db.session.commit()
    return jsonify({"mensagem": "Professor atualizado com sucesso!"})

#Excluir um professor
@app.route('/professores/<int:id>', methods=['DELETE'])
def deletar_professor(id):
    professor = db.session.get(Professor, id)

    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404
    
    db.session.delete(professor)
    db.session.commit()
    return jsonify({"mensagem": "Professor deletado com sucesso!"})


#Rota para alunos

#Adicionar aluno
@app.route('/alunos', methods=['POST'])
def criar_aluno():
    dados = request.json

    turma_id = dados.get('turma_id')
    if not turma_id:
        return jsonify({"erro": "Campo 'turma_id' é obrigatório"}), 400
    
    turma = Turma.query.get(turma_id)
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404

    data_nascimento = datetime.strptime(dados['data_nascimento'], '%d-%m-%Y').date()

    novo_aluno = Aluno(
        nome=dados['nome'],
        idade=dados['idade'],
        turma_id=turma.id,
        data_nascimento=data_nascimento,
        nota_primeiro_semestre=dados.get('nota_primeiro_semestre'),
        nota_segundo_semestre=dados.get('nota_segundo_semestre'),
        media_final=dados.get('media_final')
    )
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify({"mensagem": "Aluno cadastrado com sucesso!"}), 201

#Listar Alunos
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    resultado = [
        {
            "id": a.id, 
            "nome": a.nome, 
            "idade": a.idade, 
            "turma": {"id": a.turma.id, "descricao": a.turma.descricao} if a.turma else None,
            'data_nascimento': a.data_nascimento.strftime('%d-%m-%Y'),
            "nota_primeiro_semestre": a.nota_primeiro_semestre, 
            "nota_segundo_semestre": a.nota_segundo_semestre, 
            "media_final": a.media_final
        }
        for a in alunos
    ]
    return jsonify(resultado)

#Buscar aluno por ID
@app.route('/alunos/<int:id>', methods=['GET'])
def buscar_aluno(id):
    aluno = db.session.get(Aluno, id)
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404
    
    resultado = {

            "id": aluno.id, 
            "nome": aluno.nome, 
            "idade": aluno.idade, 
            "turma": {"id": aluno.turma.id, "descricao": aluno.turma.descricao} if aluno.turma else None,
            'data_nascimento': aluno.data_nascimento.strftime('%d-%m-%Y'),
            "nota_primeiro_semestre": aluno.nota_primeiro_semestre, 
            "nota_segundo_semestre": aluno.nota_segundo_semestre, 
            "media_final": aluno.media_final
        }
    
    return jsonify(resultado)


@app.route('/alunos/<int:id>', methods=['PUT'])
def atualizar_aluno(id):
    aluno = db.session.get(Aluno, id)

    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404

    dados = request.json

    if 'turma_id' in dados:
        turma = Turma.query.get(dados['turma_id'])
        if not turma:
            return jsonify({"erro": "Turma não encontrada"}), 404
        aluno.turma_id = turma.id

    if 'nome' in dados:
        aluno.nome = dados['nome']
    
    if 'idade' in dados:
        aluno.idade = dados['idade']

    if 'data_nascimento' in dados:
        aluno.data_nascimento = datetime.strptime(dados['data_nascimento'], '%d-%m-%Y').date()

    if 'nota_primeiro_semestre' in dados:
        aluno.nota_primeiro_semestre = dados['nota_primeiro_semestre']

    if 'nota_segundo_semestre' in dados:
        aluno.nota_segundo_semestre = dados['nota_segundo_semestre']

    if 'media_final' in dados:
        aluno.media_final = dados['media_final']
    
    db.session.commit()
    return jsonify({"mensagem": "Aluno atualizado com sucesso!"})


#Excluir Aluno
@app.route('/alunos/<int:id>', methods=['DELETE'])
def deletar_alunos(id):
    alunos = db.session.get(Aluno, id)

    if not alunos:
        return jsonify({"erro": "Aluno não encontrado"}), 404
    
    db.session.delete(alunos)
    db.session.commit()
    return jsonify({"mensagem": "Aluno deletado com sucesso!"})


#Rotas para Turma

#Adicionar Turmas
@app.route('/turmas', methods=['POST'])
def adicionar_turma():
    dados = request.json
    nova_turma = Turma(
        descricao=dados['descricao'],
        professor_id=dados['professor_id'],
        ativo=dados.get('ativo', True)
    )
    db.session.add(nova_turma)
    db.session.commit()
    return jsonify({'mensagem': 'Turma adicionada com sucesso!', 'id': nova_turma.id}), 201

#Listar turmas 
@app.route('/turmas', methods=['GET'])
def listar_turmas():
    turmas = Turma.query.all()
    resultado = []
    for turma in turmas:
        resultado.append({
            'turma_id': turma.id,
            'descricao': turma.descricao,
            'professor_id': turma.professor_id,
            'ativo': turma.ativo,
            'alunos': [{'id': aluno.id, 'nome': aluno.nome} for aluno in turma.alunos]
        })
    return jsonify(resultado)

#Buscar turma por ID
@app.route('/turmas/<int:id>', methods=['GET'])
def buscar_turma_por_id(id):
    turma = db.session.get(Turma,id)     

    if turma:
        return jsonify({
            'id': turma.id,
            'descricao': turma.descricao,
            'professor_id': turma.professor_id,
            'ativo': turma.ativo,
            'alunos': [{'id': aluno.id, 'nome': aluno.nome} for aluno in turma.alunos]
        })
    return jsonify({'mensagem': 'Turma não encontrada'}), 404

# Atualizar Turma
@app.route('/turmas/<int:id>', methods=['PUT'])
def atualizar_turma(id):
    turma = db.session.get(Turma, id)

    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404

    dados = request.json

    # Atualizando os campos da turma
    if 'descricao' in dados:
        turma.descricao = dados['descricao']

    if 'professor_id' in dados:
        professor = Professor.query.get(dados['professor_id'])
        if not professor:
            return jsonify({"erro": "Professor não encontrado"}), 404
        turma.professor_id = dados['professor_id']

    if 'ativo' in dados:
        turma.ativo = dados['ativo']

    db.session.commit()
    return jsonify({"mensagem": "Turma atualizada com sucesso!"})



#Excluir Turma
@app.route('/turmas/<int:id>', methods=['DELETE'])
def deletar_turma(id):
    turmas = db.session.get(Turma,id)

    if not turmas:
        return jsonify({"erro": "Turma não encontrado"}), 404
    
    db.session.delete(turmas)
    db.session.commit()
    return jsonify({"mensagem": "Turma deletado com sucesso!"})

#Rota para resetar o banco de dados
@app.route('/reseta', methods=['POST'])
def resetar_banco():
    try:
        db.drop_all()  # Remove todas as tabelas
        db.create_all()  # Recria todas as tabelas
        return jsonify({"mensagem": "Banco de dados resetado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
