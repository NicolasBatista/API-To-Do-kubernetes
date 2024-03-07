# Use a imagem Python 3.9
FROM python:3.9 

# Defina o diretório de trabalho como /app
# WORKDIR /Teste2

# Copie o arquivo requirements.txt para o diretório /app
COPY requirements.txt .

# Instale as dependências listadas em requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código-fonte para /app
COPY . .

# Defina a porta em que o contêiner irá escutar
# EXPOSE 7000

# Execute o comando para iniciar o aplicativo
CMD [ "ddtrace-run", "python", "./app.py" ]
