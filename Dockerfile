# STAGE 1: Build
FROM python:3.12-slim AS build

# Definindo o diretório de trabalho no container
WORKDIR /usr/src/app

# Instalar dependências do sistema para o PostgreSQL e outras bibliotecas necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualizar o pip para a versão mais recente
RUN pip install --upgrade pip

# Copiar o arquivo requirements.txt para o container
COPY requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do projeto Django
COPY . .

# Expôr a porta padrão do Django
EXPOSE 8000

# Comando para rodar o servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
