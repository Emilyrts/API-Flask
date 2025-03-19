import unittest
import requests

BASE_URL = "http://127.0.0.1:5000"

class TestProfessores(unittest.TestCase):
    def setUp(self):
        """Reseta o banco antes de cada teste, se a rota existir"""
        try:
            requests.post(f"{BASE_URL}/reseta")
        except requests.exceptions.RequestException:
            print(" Aviso: A rota /reseta não existe ou não está acessível.")

    def test_001_criar_professor(self):
        professor = {
            "nome": "Dr. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Especialista em álgebra"
        }
        response = requests.post(f"{BASE_URL}/professores", json=professor)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())  # Confirma que um ID foi gerado

    def test_002_listar_professores(self):
        """Garante que a listagem funciona corretamente"""
        # Criando um professor antes de listar
        professor = {
            "nome": "Dr. Marcos",
            "idade": 40,
            "materia": "Fisica",
            "observacoes": "professor senior"
        }
        requests.post(f"{BASE_URL}/professores", json=professor)

        # Agora listamos os professores
        response = requests.get(f"{BASE_URL}/professores")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreater(len(response.json()), 0)  



    def test_003_get_professor_por_id(self):
        """Cria um professor e o busca pelo ID correto"""
        professor = {
            "nome": "Dr. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Especialista em álgebra"
        }
        # Criar professor
        response_post = requests.post(f"{BASE_URL}/professores", json=professor)
        self.assertEqual(response_post.status_code, 201)
        
        # Obtém o ID do professor criado
        professor_id = response_post.json().get("id")
        self.assertIsNotNone(professor_id, "Erro: ID não retornado")

        # Buscar professor pelo ID correto
        response_get = requests.get(f"{BASE_URL}/professores/{professor_id}")
        self.assertEqual(response_get.status_code, 200)

        data = response_get.json()
        self.assertEqual(data["id"], professor_id)
        self.assertEqual(data["nome"], professor["nome"])
        self.assertEqual(data["idade"], professor["idade"])
        self.assertEqual(data["materia"], professor["materia"])
        self.assertEqual(data["observacoes"], professor["observacoes"])

    def test_004_deletar_professor(self):
        professor = {
            "nome": "Dr. José",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Professor de álgebra"
        }
        
        response_post = requests.post(f"{BASE_URL}/professores", json=professor)
        self.assertEqual(response_post.status_code, 201)  # Verifica se a criação foi bem-sucedida
        
        # Obter o ID do professor criado
        professor_id = response_post.json()["id"]
        
        # Tentar excluir o professor
        response_delete = requests.delete(f"{BASE_URL}/professores/{professor_id}")
        self.assertEqual(response_delete.status_code, 200)  # Verifica se a exclusão foi bem-sucedida


    def test_005_atualizar_professor(self):
        """Testa a criação e atualização de um professor"""

        # Primeiro, criamos um professor para ser atualizado
        professor_criado = {
            "nome": "Prof. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Professor experiente"
        }

        # Criar o professor (use a rota POST para criar)
        response_criar = requests.post(f"{BASE_URL}/professores", json=professor_criado)
        self.assertEqual(response_criar.status_code, 201)

        # Pega o ID do professor criado a partir da resposta
        professor_id = response_criar.json()['id']

        # Agora, vamos tentar atualizar esse professor com uma requisição POST
        professor_atualizado = {
            "nome": "Prof. João Atualizado",
            "idade": 41,
            "materia": "Física",
            "observacoes": "Professor com novas observações"
        }

        # Enviar a requisição de atualização (usando POST)
        response_atualizar = requests.post(f"{BASE_URL}/professores/{professor_id}", json=professor_atualizado)

        # Verificar se a resposta está correta
        self.assertEqual(response_atualizar.status_code, 200)
        self.assertEqual(response_atualizar.json(), {"mensagem": "Professor atualizado com sucesso!"})

        # Verificar se os dados do professor foram realmente atualizados
        response_verificar = requests.get(f"{BASE_URL}/professores/{professor_id}")
        professor_verificado = response_verificar.json()

        self.assertEqual(professor_verificado['nome'], "Prof. João Atualizado")
        self.assertEqual(professor_verificado['idade'], 41)
        self.assertEqual(professor_verificado['materia'], "Física")
        self.assertEqual(professor_verificado['observacoes'], "Professor com novas observações")


class TestTurmas(unittest.TestCase):
    def setUp(self):
        """Reseta o banco antes de cada teste, se a rota existir"""
        try:
            requests.post(f"{BASE_URL}/reseta")
        except requests.exceptions.RequestException:
            print(" Aviso: A rota /reseta não existe ou não está acessível.")

    def test_006_criar_turma(self):
        turma = {
            "descricao": "9° Ano",
            "professor_id": 1,
            "ativo": True,
            "alunos": [{"nome": "João"}, {"nome": "Maria"}, {"nome": "Ana"}]
        }
        response = requests.post(f"{BASE_URL}/turmas", json=turma)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

    def test_007_listar_turmas(self):
        # Criando uma turma antes de listar
        professor = {
            "descricao": "3° Ano",
            "professor_id": 2,
            "ativo": True,
            "alunos": [{"nome": "Camilla"}, {"nome": "João"}, {"nome": "Maria"}]    
        }
        requests.post(f"{BASE_URL}/turmas", json=professor)

        # Agora listamos os professores
        response = requests.get(f"{BASE_URL}/turmas")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreater(len(response.json()), 0)

    def test_008_buscar_turma_por_id(self):
        """Testa se a busca de uma turma por ID retorna os dados corretos"""
        
        # Criar o professor antes de criar a turma
        professor_criado = {
            "nome": "Prof. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Professor experiente"
        }
        
        response_criar_professor = requests.post(f"{BASE_URL}/professores", json=professor_criado)
        self.assertEqual(response_criar_professor.status_code, 201)

        # Criar a turma para testar a busca
        turma_criada = {
            "descricao": "1° Ano",
            "professor_id": 1,  # Considerando que o professor com ID 1 já existe
            "ativo": True
        }

        response_criar = requests.post(f"{BASE_URL}/turmas", json=turma_criada)
        self.assertEqual(response_criar.status_code, 201)

        # ID da turma criada
        turma_id = response_criar.json()["id"]
        
        # Agora, buscamos a turma pela ID
        response_buscar = requests.get(f"{BASE_URL}/turmas/{turma_id}")
        
        # Verificar se a resposta está correta
        self.assertEqual(response_buscar.status_code, 200)
        
        # Verificar se os dados retornados são os esperados
        turma = response_buscar.json()
        self.assertEqual(turma['id'], turma_id)
        self.assertEqual(turma['descricao'], turma_criada['descricao'])
        self.assertEqual(turma['professor_id'], turma_criada['professor_id'])
        self.assertEqual(turma['ativo'], turma_criada['ativo'])
        self.assertEqual(turma['alunos'], [])  # Inicialmente, a turma não tem alunos, então esperamos uma lista vazia

        
    def test_009_deletar_turma(self):
            turma = {
            "descricao": "8° Ano",
            "professor_id": 4,
            "ativo": True,
            "alunos": [  
            {"nome": "kaka"},
            {"nome": "Ana"},
            {"nome": "Bruna"}
        ]
        }
            response_post = requests.post(f"{BASE_URL}/turmas", json=turma)
            self.assertEqual(response_post.status_code, 201)  # Verifica se a criação foi bem-sucedida
        
        # Obter o ID do professor criado
            turma_id = response_post.json()["id"]
        
        # Tentar excluir o professor
            response_delete = requests.delete(f"{BASE_URL}/turmas/{turma_id}")
            self.assertEqual(response_delete.status_code, 200)  # Verifica se a exclusão foi bem-sucedida


    def test_010_atualizar_turma(self):
        """Testa a criação e atualização de uma turma"""

        # Criar um professor para garantir que ele existe
        professor_criado = {
            "nome": "Prof. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Professor experiente"
        }
        
        # Criar o professor (usando a rota POST para criar)
        response_professor = requests.post(f"{BASE_URL}/professores", json=professor_criado)
        self.assertEqual(response_professor.status_code, 201)

        # Pega o ID do professor criado
        professor_id = response_professor.json()['id']

        # Agora, criamos uma turma com o professor criado
        turma_criada = {
            "descricao": "Turma de Matemática",
            "professor_id": professor_id,  # Usando o professor criado
            "ativo": True
        }

        # Criar a turma (usando a rota POST para criar a turma)
        response_criar = requests.post(f"{BASE_URL}/turmas", json=turma_criada)
        self.assertEqual(response_criar.status_code, 201)

        # Pega o ID da turma criada
        turma_id = response_criar.json()['id']
        self.assertIsNotNone(turma_id, "ID da turma não foi retornado corretamente")
        print(f"ID da turma criada: {turma_id}")  # Debug

        # Agora, vamos tentar atualizar essa turma
        turma_atualizada = {
            "descricao": "Turma de Física",
            "professor_id": professor_id,  # Usando o mesmo professor criado
            "ativo": False
        }

        # Enviar a requisição de atualização
        response_atualizar = requests.put(f"{BASE_URL}/turmas/{turma_id}", json=turma_atualizada)
        print(f"Status Code da Atualização: {response_atualizar.status_code}")
        print(f"Resposta da Atualização: {response_atualizar.json()}")  # Debug

        # Verificar se a resposta está correta
        self.assertEqual(response_atualizar.status_code, 200)
        self.assertEqual(response_atualizar.json(), {"mensagem": "Turma atualizada com sucesso!"})

        # Verificar se os dados da turma foram realmente atualizados
        response_verificar = requests.get(f"{BASE_URL}/turmas/{turma_id}")
        turma_verificada = response_verificar.json()

        self.assertEqual(turma_verificada['descricao'], "Turma de Física")
        self.assertEqual(turma_verificada['professor_id'], professor_id)  # Garantindo que professor_id foi mantido
        self.assertEqual(turma_verificada['ativo'], False)


if __name__ == "__main__":
    unittest.main()
