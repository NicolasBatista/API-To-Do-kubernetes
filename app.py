from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
import json
import requests
import io
import base64
import tkinter as tk
from tkinter import filedialog
import logging


app = Flask(__name__)
app.secret_key = 'null'

# Tela de Login
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('index.html')

# Rota para autenticar o usuário
@app.route('/login', methods=['POST'])
def login():
    # Obter os dados do formulário
    username = request.form['username']
    password = request.form['password']

    # Fazer a requisição para a API
    resource = 'user'
    service = 'login'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
      "username": username,
      "password": password
    }

    headers = {'Content-type': 'application/json'}

    dados = requests.post(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(dados.text)

    # Verificar se o login foi bem-sucedido
    if 'token' in dicionario:
        # Armazenar informações de login em variáveis de sessão
        session['id'] = dicionario['id']
        session['name'] = dicionario['name']
        session['email'] = dicionario['email']
        session['token'] = dicionario['token']
        session['picture'] = dicionario['picture']
        # Redirecionar para a página de início
        return redirect(url_for('telaInicio'))
    else:
        # Caso contrário, exibir uma mensagem de erro
        return render_template('index.html', error='Usuário ou senha inválidos')

# Tela de Cadastro de usuário
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para Cadastrar o usuário
@app.route('/cadastro', methods=['POST'])
def handle_cadastro():
    resource = 'user'
    service = 'new'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
        "name": request.form['name'],
        "email": request.form['email'],
        "username": request.form['username'],
        "password": request.form['password']
    }

    headers = {'Content-type': 'application/json'}

    dados = requests.post(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(dados.text)

    if 'error' in dicionario:
        # Exibe uma mensagem de erro
        flash('Erro ao criar usuário', 'error')
        return redirect(url_for('cadastro'))

    # Redireciona o usuário para a página de login
    flash('Usuário criado com sucesso!', 'success')
    return redirect(url_for('home'))

# Tela Inicial da Aplicação
@app.route('/telaInicio')
def telaInicio():
    # Verificar se o usuário está logado
    if 'token' not in session:
        return redirect(url_for('index'))

     # Define o payload da requisição
    payload = session['id']
    # Define a url, os headers e faz a requisição POST
    resource = 'task'
    service = 'search'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"
    headers = {
        'Content-type': 'application/json',
        'Authorization': session['token']
    }
    dados = requests.post(url, data=json.dumps(payload), headers=headers)
    # Trata a resposta da requisição
    if dados.status_code == 200:
        tarefas = json.loads(dados.content)
        return render_template('telaInicio.html', tarefas=tarefas)
    else:
        return 'Erro ao buscar tarefas'

# Tela para Exibir informações do Perfil
@app.route('/telaInicio/infoPerfil')
def infoPerfil():
    id= session['id']
    name=session['name']
    email=session['email']
    token=session['token']
    picture=session['picture']
    
    return render_template('infoPerfil.html', id=id, name=name, email=email, token=token, picture=picture)

# Tela para Editar informações do Perfil
@app.route('/telaInicio/editarPerfil')
def editarPerfil():
    id= session['id']
    name=session['name']
    email=session['email']
    token=session['token']
    picture=session['picture']
    return render_template('editarPerfil.html', id=id, name=name, email=email, token=token, picture=picture)

@app.route('/telaInicio/editarPerfil/salvar', methods=['POST'])
def salvarEditarPerfil():
    id = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    token = request.form.get('token')
    picture = request.form.get('picture')

    # Update (exceto senha)
    resource = 'user'
    service = 'update'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
      "name": name,
      "email": email,
      "username": username,
      "password": password,
      "picture": picture
    }

    headers = {
        'Content-type': 'application/json', 
        "Authorization": session['token']
    }

    response = requests.put(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(response.text)

    print(dicionario, '\n')
    for i in dicionario:
        print(f'{i}: {dicionario.get(i)}')
    return jsonify(dicionario)

# Tela para editar usuario
@app.route('/telaInicio/editarUsuario')
def editarUsuario():
    return render_template('editarUsuario.html')

# Tela para editar usuario
@app.route('/telaInicio/editarUsuario/salvar', methods=['POST'])
def salvarEditarUsuario():
    resource = 'user'
    service = 'updateuserpass'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
      "username": request.form['username'],
      "password": request.form['password'],
      "new_username": request.form['new_username'],
      "new_password": request.form['new_password'] 
    }

    headers = {
        'Content-type': 'application/json', 
        "Authorization": session['token']
    }

    response = requests.put(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(response.text)

    return redirect(url_for('telaInicio'))

# Tela para Editar Tarefas
@app.route('/telaInicio/editarTarefas')
def editarTarefas():
    return render_template('editarTarefas.html')

# Rota para editar uma tarefa específica
@app.route('/telaInicio/editarTarefas/salvar', methods=['GET', 'POST'])
def salvarEditarTarefas():
    task_id = request.form.get('id')
    name= request.form.get('name')
    realized= request.form.get('realized')

    resource = 'task'
    service = 'update'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
        "id": task_id,
        "name": name,
        "realized": realized      
        }
    headers = {
        'Content-type': 'application/json', 
        "Authorization": session['token']
        }

    dados = requests.put(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(dados.text)

    print(dicionario, '\n')
    for i in dicionario:
        print(f'{i}: {dicionario.get(i)}')

    return redirect(url_for('telaInicio'))

# Tela para Excluir Tarefas
@app.route('/telaInicio/excluirTarefas')
def excluirTarefas():
    return render_template('excluirTarefas.html')

# Rota para excluir uma tarefa específica
@app.route('/telaInicio/excluirTarefas/excluir', methods=['GET', 'POST'])
def excluirTarefa():
    # Excluir
    task_id = request.form.get('id')
    resource = 'task'
    service = 'delete'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {"id": task_id}
    headers = {
        'Content-type': 'application/json', 
        "Authorization": session['token']
        }

    dados = requests.delete(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(dados.text)

    print(dicionario, '\n')
    for i in dicionario:
        print(f'{i}: {dicionario.get(i)}')

    return redirect(url_for('telaInicio'))

# Tela para Criar Nova Tarefa
@app.route('/telaInicio/novaTarefa')
def novaTarefa():
    return render_template('newTask.html')

@app.route('/telaInicio/novaTarefa/criarNovaTarefa', methods=['POST'])
def criarNovaTarefa():
    nome = request.form.get('nome')
    resource = 'task'
    service = 'new'
    url = f"https://todolist-api.edsonmelo.com.br/api/{resource}/{service}/"

    payload = {
      "name": nome
    }

    headers = {
        'Content-type': 'application/json', 
        "Authorization": session['token']
        }

    dados = requests.post(url, data=json.dumps(payload), headers=headers)
    dicionario = json.loads(dados.text)

    if dados.status_code == 201:
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('telaInicio'))
    else:
        flash('Erro ao criar tarefa', 'error')
        return redirect(url_for('novaTarefa'))


# Rota para Deslogar da Aplicação
@app.route('/logout')
def logout():
    # Remove a sessão do usuário
    session.pop('usuario', None)
    # Redireciona para a página de login
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0') # debug=True