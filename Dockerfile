# Usando uma imagem oficial do Python
FROM python:3.10-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos de dependências
COPY requirements.txt .

# Instalar as dependências
RUN apt-get update && \
    apt-get install -y build-essential libgmp-dev python3-dev git && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o restante do código para o contêiner
COPY . .

# Expôr a porta que o Django usa para o servidor de desenvolvimento
EXPOSE 8000

# Comando para rodar o Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
