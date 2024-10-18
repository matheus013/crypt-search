import requests
import json

# URL para obter o token
token_url = "http://localhost:8000/api/token/"

# URL para salvar o vetor
save_vector_url = "http://localhost:8000/api/save-vector/"

# Credenciais de login
login_data = {
    "username": "root",
    "password": "root"
}

# Frases de exemplo para gerar textos variados
example_phrases = [
    "Hello, how are you doing today?",
    "Good morning, I hope you are well.",
    "Hi, how is everything going?",
    "Hello, have a great day!",
    "Good evening, how was your day?",
    "What's up?",
    "How have you been?",
    "Nice to meet you!",
    "It's a wonderful day!",
    "Stay safe and take care."
]


# Função para gerar n frases aleatórias
def generate_random_texts(n):
    return [example_phrases[i % len(example_phrases)] for i in range(n)]


# Função para obter o token de acesso JWT
def get_jwt_token():
    response = requests.post(token_url, json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access"]
    else:
        print(f"Erro ao obter o token: {response.status_code} - {response.text}")
        return None


# Função para realizar a requisição POST com os textos
def post_texts(n):
    # Obter o token de acesso
    token = get_jwt_token()
    if not token:
        print("Falha ao obter o token. Encerrando.")
        return

    # Gerar n textos
    data = {
        "text": generate_random_texts(n)
    }

    # Cabeçalhos de autenticação e tipo de conteúdo
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Fazer a requisição POST
    response = requests.post(save_vector_url, headers=headers, data=json.dumps(data))

    # Verificar o resultado
    if response.status_code == 202:
        result = response.json()
        print(f"Sucesso: {n} textos enviados.")
        print(f"Mensagem: {result['message']}")
        print(f"Task ID: {result['task_id']}")
    else:
        print(f"Erro: {response.status_code} - {response.text}")


# Quantidade de textos para gerar e enviar
n = 100

# Enviar os textos
post_texts(n)
