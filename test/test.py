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
        # Primeiro, criamos um professor para ser atualizado
        professor_criado = {
            "id": 1,
            "nome": "Prof. João",
            "idade": 40,
            "materia": "Matemática",
            "observacoes": "Professor experiente"
        }

        # Criar o professor (ou use a sua rota de criação, caso seja necessário)
        response_criar = requests.post(f"{BASE_URL}/professores", json=professor_criado)
        self.assertEqual(response_criar.status_code, 201)

        # Agora, vamos tentar atualizar esse professor
        professor_atualizado = {
            "nome": "Prof. João Atualizado",
            "idade": 41,
            "materia": "Física",
            "observacoes": "Professor com novas observações"
        }

        # Enviar a requisição de atualização
        response = requests.post(f"{BASE_URL}/professores/1", json=professor_atualizado)

        # Verificar se a resposta está correta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"mensagem": "Professor atualizado com sucesso!"})



if __name__ == "__main__":
    unittest.main()
