from flask import Flask, render_template_string, request, session, jsonify, redirect
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "minha_chave_super_secreta_12345"

DB_FILE = "jogo.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # --- ALTERADO: Adicionada a coluna 'pagina_atual' ---
    c.execute('''CREATE TABLE IF NOT EXISTS personagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    raca TEXT,
                    classe TEXT,
                    habilidade INTEGER,
                    energia INTEGER,
                    max_energia INTEGER,
                    sorte INTEGER,
                    provisoes INTEGER,
                    avatar TEXT,
                    pagina_atual TEXT 
                )''')
    conn.commit()
    conn.close()

# --- ALTERADO: Salva também a página inicial ---
def salvar_personagem(nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # --- ALTERADO: Adicionado 'pagina_atual' no INSERT ---
    c.execute('''INSERT INTO personagens 
        (nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, pagina_atual)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, '/aventura')) # Começa na página /aventura
    
    novo_id = c.lastrowid
    conn.commit()
    conn.close()
    return novo_id

# --- ALTERADO: Atualiza também a página atual ---
def atualizar_personagem(pid, energia, sorte, provisoes, pagina_atual):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # --- ALTERADO: Adicionado 'pagina_atual' no UPDATE ---
    c.execute('''UPDATE personagens 
                 SET energia = ?, sorte = ?, provisoes = ?, pagina_atual = ?
                 WHERE id = ?''', 
              (energia, sorte, provisoes, pagina_atual, pid))
    conn.commit()
    conn.close()

def listar_personagens():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nome, raca, classe FROM personagens")
    personagens = c.fetchall()
    conn.close()
    return personagens

def carregar_personagem_por_id(pid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # --- ALTERADO: Seleciona também 'pagina_atual' ---
    c.execute("SELECT id, nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, pagina_atual FROM personagens WHERE id=?", (pid,))
    personagem = c.fetchone()
    conn.close()
    return personagem

if not os.path.exists(DB_FILE):
    init_db()

# Dicionários e listas de Raças/Classes (sem alterações)
MODIFICADORES = { "Humano": { "Guerreiro": {"HABILIDADE": 2, "ENERGIA": 1, "SORTE": 0}, "Mago": {"HABILIDADE": 0, "ENERGIA": 0, "SORTE": 1}, "Arqueiro":  {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 1}, "Ladino": {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 1}, }, "Elfo": { "Guerreiro": {"HABILIDADE": 4, "ENERGIA": 0, "SORTE": 1}, "Mago": {"HABILidade": 2, "ENERGIA": -1, "SORTE": 3}, "Arqueiro": {"HABILIDADE": 4, "ENERGIA": -1, "SORTE": 3}, "Ladino": {"HABILIDADE": 4, "ENERGIA": -1, "SORTE": 2}, }, "Anão": { "Guerreiro": {"HABILIDADE": 3, "ENERGIA": 3, "SORTE": -1}, "Mago": {"HABILIDADE": 1, "ENERGIA": 2, "SORTE": 0}, "Arqueiro": {"HABILIDADE": 3, "ENERGIA": 2, "SORTE": 0}, "Ladino": {"HABILIDADE": 3, "ENERGIA": 2, "SORTE": 0}, }, "Meio-Orc": { "Guerreiro": {"HABILIDADE": 4, "ENERGIA": 2, "SORTE": -1}, "Mago": {"HABILIDADE": 2, "ENERGIA": 1, "SORTE": 0}, "Arqueiro": {"HABILIDADE": 4, "ENERGIA": 1, "SORTE": 0}, "Ladino": {"HABILIDADE": 4, "ENERGIA": 1, "SORTE": 0}, }, "Halfling": { "Guerreiro": {"HABILIDADE": 1, "ENERGIA": 1, "SORTE": 1}, "Mago": {"HABILIDADE": -1, "ENERGIA": 0, "SORTE": 2}, "Arqueiro": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2}, "Ladino": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2}, }, "Gnomo": { "Guerreiro": {"HABILIDADE": 1, "ENERGIA": 1, "SORTE": 1}, "Mago": {"HABILIDADE": -1, "ENERGIA": 0, "SORTE": 3}, "Arqueiro": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 3}, "Ladino": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2}, }, "Meio-Elfo": { "Guerreiro": {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 3}, "Mago": {"HABILIDADE": 0, "ENERGIA": -1, "SORTE": 5}, "Arqueiro": {"HABILIDADE": 2, "ENERGIA": -1, "SORTE": 5}, "Ladino": {"HABILIDADE": 2, "ENERGIA": -1, "SORTE": 4}, } }
RACAS = list(MODIFICADORES.keys())
CLASSES = list(next(iter(MODIFICADORES.values())).keys())

@app.context_processor
def inject_player_stats():
    stats = {
        "player_avatar": session.get("player_avatar"),
        "player_nome": session.get("player_nome"),
        "player_habilidade": session.get("player_habilidade"),
        "player_energia": session.get("player_energia"),
        "player_sorte": session.get("player_sorte"),
        "player_provisions": session.get("player_provisions"),
        "player_max_energia": session.get("player_max_energia"),
        # --- NOVO: Disponibiliza a página salva para os templates ---
        "player_pagina_atual": session.get("player_pagina_atual", "/aventura")
    }
    return stats

# --- CÓDIGO DO STATUS_HTML ALTERADO ---
STATUS_HTML = """
{% if player_nome %}
<style>
    .character-sheet { position: fixed; top: 10px; right: 10px; width: 220px; border: 2px solid #555; background-color: #f9f9f9; padding: 10px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-family: sans-serif; z-index: 1000; user-select: none; }
    #character-sheet-header { cursor: move; background-color: #e0e0e0; margin: -10px -10px 10px -10px; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom: 2px solid #ccc; text-align: center; }
    .character-avatar { width: 100px; height: 100px; border-radius: 50%; border: 3px solid #555; margin: 0 auto 10px auto; display: block; object-fit: cover; }
    .character-sheet h3 { margin-top: 0; padding: 0; border-bottom: none; }
    .character-sheet ul { list-style: none; padding: 0; }
    .character-sheet li { padding: 4px 0; display: flex; justify-content: space-between; align-items: center; }
    .action-button { padding: 5px 10px; font-size: 0.8em; cursor: pointer; border: 1px solid #888; border-radius: 5px; background-color: #d4edda; margin-left: 10px; }
    .action-button:hover { background-color: #c3e6cb; }
    .action-button:disabled { background-color: #ccc; cursor: not-allowed; }
    .save-button { background-color: #d1ecf1; }
    .save-button:hover { background-color: #bee5eb; }
    #save-status { font-size: 0.8em; color: green; margin-left: 5px; }
</style>
<div class="character-sheet" id="character-sheet">
    <div id="character-sheet-header">
        {% if player_avatar %}<img src="{{ url_for('static', filename='avatares/' + player_avatar) }}" alt="Avatar" class="character-avatar">{% endif %}
        <h3>{{ player_nome }}</h3>
    </div>
    <ul>
        <li><b>HABILIDADE:</b> <span>{{ player_habilidade }}</span></li>
        <li><b>ENERGIA:</b> <span><span id="sheet-energia">{{ player_energia }}</span> / {{ player_max_energia }}</span></li>
        <li><b>SORTE:</b> <span id="sheet-sorte">{{ player_sorte }}</span></li>
        <li>
            <b>PROVISÕES:</b> 
            <div>
                <span id="sheet-provisions">{{ player_provisions }}</span>
                <button id="provision-btn" class="action-button" onclick="usarProvisao()" {% if player_provisions <= 0 %}disabled{% endif %}>Usar</button>
            </div>
        </li>
    </ul>
    <div style="text-align: center; margin-top: 10px;">
        <button id="save-btn" class="action-button save-button" onclick="salvarProgresso()">Salvar Jogo</button>
        <span id="save-status"></span>
    </div>
</div>
<script>
    const sheet = document.getElementById('character-sheet');
    const header = document.getElementById('character-sheet-header');
    let isDragging = false, offsetX, offsetY;
    header.addEventListener('mousedown', (e) => { isDragging = true; offsetX = e.clientX - sheet.offsetLeft; offsetY = e.clientY - sheet.offsetTop; e.preventDefault(); });
    document.addEventListener('mousemove', (e) => { if (!isDragging) return; sheet.style.left = e.clientX - offsetX + 'px'; sheet.style.top = e.clientY - offsetY + 'px'; });
    document.addEventListener('mouseup', () => { isDragging = false; });
    document.addEventListener('mouseleave', () => { isDragging = false; });
    async function usarProvisao() {
        const response = await fetch('/usar-provisao', { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await response.json();
        if (data.success) {
            document.getElementById('sheet-energia').textContent = data.player_energia;
            document.getElementById('sheet-provisions').textContent = data.player_provisions;
            if (data.player_provisions <= 0) document.getElementById('provision-btn').disabled = true;
        } else {
            alert(data.message);
            document.getElementById('provision-btn').disabled = true;
        }
    }
    // --- FUNÇÃO DE SALVAR ALTERADA ---
    async function salvarProgresso() {
        const saveButton = document.getElementById('save-btn');
        const saveStatus = document.getElementById('save-status');
        saveButton.disabled = true;
        saveStatus.textContent = 'Salvando...';

        // --- NOVO: Captura a página atual e envia para o servidor ---
        const currentPage = window.location.pathname;

        const response = await fetch('/salvar-progresso', {
            method: 'POST',
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json' // Informa que estamos enviando JSON
            },
            body: JSON.stringify({ pagina_atual: currentPage }) // Envia a página no corpo da requisição
        });
        const data = await response.json();
        if (data.success) {
            saveStatus.style.color = 'green';
            saveStatus.textContent = 'Salvo!';
        } else {
            saveStatus.style.color = 'red';
            saveStatus.textContent = 'Erro!';
        }
        setTimeout(() => { saveStatus.textContent = ''; saveButton.disabled = false; }, 3000);
    }
</script>
{% endif %}
"""

# --- ROTA DE SALVAR ALTERADA ---
@app.route("/salvar-progresso", methods=["POST"])
def salvar_progresso():
    player_id = session.get("player_id")
    if not player_id:
        return jsonify({"success": False, "message": "ID do jogador não encontrado."})
    
    try:
        # --- NOVO: Pega a página atual enviada pelo JavaScript ---
        data = request.get_json()
        pagina_atual = data.get('pagina_atual')
        if not pagina_atual:
             return jsonify({"success": False, "message": "Página atual não informada."})

        energia = session.get("player_energia")
        sorte = session.get("player_sorte")
        provisoes = session.get("player_provisions")

        # --- NOVO: Atualiza a sessão com a página atual ANTES de salvar ---
        session['player_pagina_atual'] = pagina_atual
        
        # --- ALTERADO: Passa a página atual para a função de salvar ---
        atualizar_personagem(player_id, energia, sorte, provisoes, pagina_atual)
        
        return jsonify({"success": True, "message": "Progresso salvo!"})

    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return jsonify({"success": False, "message": "Ocorreu um erro ao salvar."})

@app.route("/")
def home():
    html_home = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8"><style>body{margin:0;padding:0;height:100vh;background-image:url('/static/imagens/background.png');background-size:cover;background-position:center;background-repeat:no-repeat;font-family:Arial,sans-serif;color:white;text-align:center}h1{margin-top:72px;text-shadow:2px 2px 4px black;font-size:48px}a{color:yellow;font-weight:bold;text-decoration:none;font-size:36px}p{font-size:24px}</style></head>
    <body>
        <h1>⚔️ Aventura na Montanha do Cume de Fogo ⚔️</h1>
        <p>Bem-vindo, aventureiro!</p>
        <ul>
            <li><a href='/criar'>➕ Criar Personagem</a></li>
            <li><a href='/personagens'>📜 Personagens Salvos</a></li>
            {% if player_nome %}
                {# --- ALTERADO: O link agora é dinâmico --- #}
                <li><a href='{{ player_pagina_atual }}'>🚀 Continuar Aventura</a></li>
            {% endif %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html_home)

@app.route("/personagens")
def personagens():
    lista = listar_personagens()
    html = "<h1>Personagens Salvos</h1><ul>"
    for p in lista:
        html += f"<li>{p[1]} ({p[2]} {p[3]}) - <a href='/carregar/{p[0]}'>Carregar</a></li>"
    html += "</ul><br><a href='/'>Voltar ao início</a>"
    return html

@app.route("/carregar/<int:pid>")
def carregar(pid):
    p = carregar_personagem_por_id(pid)
    if p:
        # --- ALTERADO: Carrega todos os dados, incluindo a página atual ---
        session["player_id"] = p[0]
        session["player_nome"] = p[1]
        session["player_habilidade"] = p[4]
        session["player_energia"] = p[5]
        session["player_max_energia"] = p[6]
        session["player_sorte"] = p[7]
        session["player_provisions"] = p[8]
        session["player_avatar"] = p[9]
        session["player_pagina_atual"] = p[10] # Carrega a página salva
        
        # --- ALTERADO: Redireciona o jogador para a página salva ---
        return f"<h2>✅ Personagem carregado!</h2><a href='{p[10]}'>Continuar aventura</a>"
    else:
        return "<h2>❌ Personagem não encontrado.</h2><a href='/'>Voltar</a>"

@app.route("/criar", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        session.clear()

    if request.method == "POST":
        nome = request.form.get("nome")
        raca = request.form.get("raca")
        classe = request.form.get("classe")
        mods = MODIFICADORES[raca][classe]

        habilidade = mods['HABILIDADE'] + random.randint(1,6)
        energia = mods['ENERGIA'] + random.randint(1,6) + random.randint(1,6)
        sorte = mods['SORTE'] + random.randint(1,6)
        avatar_filename = f"{raca.lower()}_{classe.lower()}.png"
        
        novo_id = salvar_personagem(nome, raca, classe, habilidade, energia, energia, sorte, 10, avatar_filename)
        
        session["player_id"] = novo_id
        session["player_habilidade"] = habilidade
        session["player_energia"] = energia
        session["player_max_energia"] = energia
        session["player_sorte"] = sorte
        session["player_nome"] = nome
        session["player_provisions"] = 10
        session["player_avatar"] = avatar_filename
        # --- NOVO: Define a página inicial na sessão ao criar ---
        session["player_pagina_atual"] = "/aventura"

        ficha_html = f"""
        <!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>body{{background-image:url('/static/imagens/background.png');background-size:cover;background-position:center;color:white;font-family:Arial,sans-serif;text-align:center}}.ficha{{background-color:rgba(0,0,0,0.6);display:inline-block;padding:20px;padding-top:20px;border-radius:10px}}a{{color:#ffd700;text-decoration:none;margin:5px;font-size:24px;display:inline-block}}h2{{text-shadow:2px 2px 4px black;font-size:36px}}p{{font-size:24px}}ul{{list-style-type:none;padding:0;font-size:24px}}</style></head>
        <body><div class="ficha"><h2>✅ Personagem criado!</h2><p><b>Nome:</b> {nome}</p><p><b>Raça:</b> {raca}</p><p><b>Classe:</b> {classe}</p><h3>Atributos:</h3><ul><li>HABILIDADE: {habilidade}</li><li>ENERGIA: {energia}</li><li>SORTE: {sorte}</li></ul><a href="/"> ➕ Criar outro personagem</a><br><a href="/aventura"> 🚀 Iniciar aventura</a></div></body></html>
        """
        return ficha_html

    html_form = """
    <!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>body{background-image:url('/static/imagens/background.png');background-size:cover;background-position:center;color:white;font-family:Arial,sans-serif;font-size:32px;text-align:center}h1{text-shadow:2px 2px 4px black}h2{text-shadow:2px 2px 4px black;font-size:36px}form{background-color:rgba(0,0,0,0.5);display:inline-block;padding:20px;border-radius:10px}select,input[type="text"]{font-size:20px;padding:5px;margin:10px 0;width:200px}button{font-size:24px;padding:10px 20px;cursor:pointer}</style><h1>Criação de Personagem</h1><form method="POST"><label>Nome: <input type="text" name="nome" required></label><br><br><label>Raça: <select name="raca" required>{% for r in racas %}<option value="{{r}}">{{r}}</option>{% endfor %}</select></label><br><br><label>Classe: <select name="classe" required>{% for c in classes %}<option value="{{c}}">{{c}}</option>{% endfor %}</select></label><br><br><button type="submit"> 🚀 Criar personagem</button></form>
    """
    return render_template_string(html_form, racas=RACAS, classes=CLASSES)

# ... (O restante do seu código, a partir de @app.route("/usar-provisao"), continua exatamente o mesmo)
@app.route("/usar-provisao", methods=["POST"])
def usar_provisao():
    if session.get("player_provisions", 0) > 0:
        max_energia = session.get("player_max_energia", 20)
        
        session["player_provisions"] -= 1
        session["player_energia"] += 4
        
        if session["player_energia"] > max_energia:
            session["player_energia"] = max_energia
            
        session.modified = True
        
        return jsonify({
            "success": True,
            "message": "Você recuperou até 4 pontos de ENERGIA.",
            "player_energia": session["player_energia"],
            "player_provisions": session["player_provisions"]
        })
    else:
        return jsonify({
            "success": False,
            "message": "Você não tem mais provisões!",
            "player_energia": session.get("player_energia"),
            "player_provisions": 0
        })
    
# ... (cole aqui todo o resto do seu código de rotas de aventura, sem alterações)
# Nova página: Aventura
@app.route("/aventura")
def aventura():
    html = STATUS_HTML + """
       <!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: justify;
        }
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
         img { display: block; margin: 0 auto; }
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
    </style> 
    <h1>BOATOS</h1>
    <img src="/static/imagens/arbetura.png" alt="Montanha do Cume de Fogo" style="width:450px;"><br>
    <p>Somente um aventureiro imprudente partiria em uma busca tão perigosa sem primeiro descobrir o máximo possível a respeito da montanha e seus tesouros. Antes da sua chegada ao sopé da Montanha do Cume de Fogo, você passou diversos dias com as pessoas da cidadezinha local, a uns dois dias de viagem da base do monte. Por ser uma pessoa simpática, você não teve muita dificuldade em se relacionar com os camponeses da região. Embora eles contassem muitas histórias sobre o misterioso santuário do Feiticeiro, você não ficou muito convencido de que todas ou alguma delas, na realidade eram baseadas em fatos reais</p>
    <br>
    <p>Os habitantes locais também o incentivaram a fazer um bom mapa de sua trajetória pois sem um mapa você terminaria se perdendo irremediavelmente no interior da montanha. Quando finalmente chegou o seu dia de partir, a vila inteira apareceu para desejar a você uma viagem segura. Os olhos de muitas da mulheres se encheram de lágrimas, tanto das jovens quanto das velhas. Você não conseguiu evitar de pensar se não seriam lágrimas antecipadas de sofrimento, choradas por olhos que não voltariam a vê-lo vivo. </p>
    <br>
    <p><b>Escolha seu próximo passo:</b></p>
    
    <a href="/sair">Sair da cidade</a></li>
    <br>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    <br>
    <br>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/sair")
def sair():
    html = STATUS_HTML + """
        <!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
         img { display: block; margin: 0 auto; }
    a   {
        padding: 15px 20px;
        background-color: #333;
        color: white;
        font-size: 32px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
    }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }     
    </style> 
<body>
    <h1>Você saiu da cidade</h1>
    <p>Finalmente a sua caminhada de dois dias chegou ao fim. Você desembainha a sua espada, coloca-a no chão e suspira aliviado, enquanto se abaixa para se sentar nas pedras cheias de musgo para um momento de descanso. Você se espreguiça, esfrega os olhos e, afinal, olha para a Montanha do Cume de Fogo. A própria montanha em si já tem um ar ameaçador. Algum animal gigantesco parece ter deixado as marcas de suas garras na encosta íngreme diante de você. Penhascos rochosos e pontudos se projetam, formando ângulos estranhos. No cume você já pode vislumbrar a sinistra coloração vermelha provavelmente alguma vegetação misteriosa que deu nome à montanha. Talvez ninguém jamais chegue a saber o que cresce lá em cima, uma vez que escalar o pico deve ser com certeza impossível.</p>
    <img src="/static/imagens/pag13.png" alt="Montanha do Cume de Fogo" style="width:450px;"><br>
    <br>
    <p>Sua busca está para começar. Do outro lado da clareira há uma escura entrada de caverna. Você pega a sua espada, levanta-se e considera que perigos podem estar à sua frente. Mas, com determinação, você recoloca a sua espada na bainha e se aproxima da caverna.</p>
    <br>
    <img src="/static/imagens/pag8.png" alt="Entrada da Caverna" style="width:450px;"><br>
    <p>Você dá uma primeira olhada na penumbra e vê-paredes escuras e úmidas com poças de água no chão de pedra à sua frente. O ar é frio e úmido. Você acende a sua lanterna e avança cautelosamente pela escuridão. Teias de aranha tocam seu rosto e você ouve a movimentação de pés minúsculos: muito provavelmente, ratazanas. Você adentra a caverna. Depois de uns poucos metros, chega logo a uma encruzilhada. </p>
    <br>
    <img src="/static/imagens/pag14.png" alt="Encruzilhada" style="width:450px;">
    <br>
    <br>
    <br>
    <a href="/oste">Você vai virar para o oeste</a>
    <a href="/leste">ou para o leste</a>
    <br><br>
</body>    
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/leste")
def leste():
    html = STATUS_HTML + """
         <!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
         img { display: block; margin: 0 auto; }
     a   {
        padding: 15px 20px;
        background-color: #333;
        color: white;
        font-size: 32px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
    }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }    
    </style> 
    <img src="/static/imagens/pag12.png" alt="Caverna Leste" style="width:450px;"><br>
    <h1>Você virou para o leste</h1>
    <p>Ao virar para o leste, a passagem termina em uma porta de madeira que está trancada. Você não ouve nada do outro lado. Você tem então duas opções:</p>
    <br>
    <br>
    <a href="/derrubar-porta">Tentar derrubar a porta</a>
    <a href="/sair">Dar meia volta e retornar à encruzilhada</a>
    <a href="/">Voltar ao início</a>
    <br>
    <br>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/derrubar-porta", methods=["GET"])
def derrubar_porta():
    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Teste de Habilidade: Derrubar a Porta</title>
        <style>
            #dados { font-size: 1.5em; margin: 10px 0; }
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
         img { display: block; margin: 0 auto; }
     a   {
        padding: 15px 20px;
        background-color: #333;
        color: white;
        font-size: 32px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
    }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }    

    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }    
    </style> 
        </style>
    </head>
    <body>
        <img src="/static/imagens/pag12.png" alt="Caverna Leste" style="width:450px;"><br>
        <h1>Teste de Habilidade: Derrubar a Porta</h1>
        <p>Ao tentar derrubar a porta com o ombro, você precisa testar sua <b>HABILIDADE</b>. Você deve jogar dois dados (2d6).</p>

        <button type="button" onclick="testarHabilidade()">🎲 Testar Habilidade</button>

        <div id="dados">
            <p>Dado 1: <span id="dado1">?</span></p>
            <p>Dado 2: <span id="dado2">?</span></p>
        </div>

        <p id="mensagem"></p>
        <div id="imagem"></div>
        <div id="acao"></div>
        <br><a href="/">Voltar ao início</a>
        <br>
        <br>

        <script>
        async function testarHabilidade() {
            let dado1Span = document.getElementById("dado1");
            let dado2Span = document.getElementById("dado2");
            let mensagemP = document.getElementById("mensagem");
            let imagemDiv = document.getElementById("imagem");
            let acaoDiv = document.getElementById("acao");

            // Animação dos dados
            for (let i = 0; i < 10; i++) {
                dado1Span.textContent = Math.floor(Math.random() * 6 + 1);
                dado2Span.textContent = Math.floor(Math.random() * 6 + 1);
                await new Promise(r => setTimeout(r, 50));
            }

            // Requisição AJAX para o Flask
            let response = await fetch("/teste-habilidade-ajax", {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

            let data = await response.json();

            dado1Span.textContent = data.dado1;
            dado2Span.textContent = data.dado2;
            mensagemP.textContent = data.mensagem;
            imagemDiv.innerHTML = data.imagem; // atualiza a imagem
            acaoDiv.innerHTML = data.link;     // atualiza o link de ação
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/teste-habilidade-ajax", methods=["POST"])
def teste_habilidade_ajax():
    habilidade = session.get("player_habilidade", 6)

    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    resultado = dado1 + dado2

    if resultado <= habilidade:
        mensagem = f"✅ Você rolou {resultado} (Habilidade {habilidade}) e consegue arrombar a porta!"
        link = '<a href="/porta-arrombada">Continuar pela porta</a>'
        imagem = "<img src='/static/imagens/pag11.png' alt='Porta Arrombada' style='width:450px;'>"
    else:
        mensagem = f"💀 Você rolou {resultado} (Habilidade {habilidade}). A porta não cede. Você esfrega o ombro dolorido e decide não tentar novamente, retornando à encruzilhada."
        link = '<a href="/sair">Retornar à encruzilhada</a>'
        imagem = "<img src='/static/imagens/pag10.png' alt='Porta Não Cedeu' style='width:450px;'>"

    return jsonify({
        "dado1": dado1,
        "dado2": dado2,
        "mensagem": mensagem,
        "link": link,
        "imagem": imagem
    })

@app.route("/porta-arrombada")
def porta_arrombada():
    # Inicializa energia do jogador se ainda não existir
    if "player_energia" not in session:
        session["player_energia"] = 10  # valor padrão inicial

    # Reduz 1 ponto de energia
    session["player_energia"] -= 1
    session.modified = True # Garante que a sessão seja salva

    html = STATUS_HTML + f"""
    <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <style>
                  body {{
                    color: black;
                    font-family: Arial, sans-serif;
                    font-size: 20px;
                    text-align: center;
                }}
                .h1 {{
                    text-shadow: 2px 2px 4px black; 
                    text-align: center;
                }}
                img {{ display: block; margin: 0 auto; }}
                img:hover {{ transform: scale(1.05);
                    transition: transform 0.3s ease; }}
                a   {{
                    padding: 10px 15px;
                    background-color: #333;
                    color: white;
                    font-size: 32px;
                    border-radius: 5px;
                    text-align: center;
                    text-decoration: none;
                    justify-content: center;}}
                    
                a:hover {{background-color:#ffffff;
                    color: black;  
                    transform: scale(1.05);
                    transition: transform 0.3s ease;}} 
            
                h2 {{ text-shadow: 2px 2px 4px black; 
                    font-size: 36px; }}
                p {{ font-size: 24px; }}
                ul {{ list-style-type: none; padding: 0;
                     font-size: 24px; }}   
                     
            </style>
        </head>
        <body>
        <img src="/static/imagens/pag9.png" alt="Porta Arrombada" style="width:450px;"><br>
        <h1>Você arrombou a porta</h1>
        <p>A porta se abre de repente e você cai, mas não no chão, e sim em uma espécie de poço. Felizmente, o poço não é muito fundo, tendo menos de dois metros. Você perde 1 ponto de <b>ENERGIA</b> por causa das escoriações sofridas.</p>
        <p><b>Sua energia atual: {session['player_energia']}</b></p>
        <a href="/sair">Você sair do poço e volta à encruzilhada</a><br>
        <br>
        <br>
        <a href="/">Voltar ao início</a>
        <br>
        <br>
        <br>
        </body>
        </html>
   
        """
    return render_template_string(html)

@app.route("/oste", methods=["GET", "POST"])
def oste():
    resultado = None
    mensagem = ""
    extra_texto = ""
    
    if request.method == "POST":
        resultado = random.randint(1, 20)
        if resultado > 10:
            mensagem = "✅ Você teve sorte! A criatura não acorda e você continua."
            extra_texto = "Você continua pela passagem e, à sua esquerda, vê uma abertura misteriosa iluminada por uma luz fraca."
        else:
            mensagem = "💀 Você não teve sorte! Você pisa em terreno mole, faz barulho e a criatura acorda instantaneamente."
    
    html = STATUS_HTML + """
    <!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">  
    <style>
        body  {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
         img { display: block; margin: 0 auto; }
         img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        font-size: 32px;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        justify-content: center;
        padding-bottom: 10px;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    button { font-size: 24px; padding: 10px 20px; cursor: pointer;
    </style>    
    <img src="/static/imagens/pag15.png" alt="Caverna Oeste" style="width:450px;"><br>
    <h1>Você virou para o oeste</h1>
    <p>Ao virar para o oeste, a passagem faz uma curva para o norte. Você se aproxima de um posto de sentinela e vê uma criatura parecida com um Goblin dormindo.
    Você deve então tentar passar na ponta dos pés, o que exige um <b>Teste a sua Sorte</b>.</p>
    
    <form method="POST">
        <button type="submit">🎲 Testar Sorte</button>
    </form>
    
    {% if resultado %}
        <h2>Resultado: {{resultado}}</h2>
        <p>{{mensagem}}</p>
        
        {% if resultado > 10 %}
            <p>{{extra_texto}}</p>
            <a href="/norte">Explorar a abertura à esquerda</a>
        {% else %}
            <a href="/combate">Entrar em combate</a>
        {% endif %}
    {% endif %}
    <a href="/sair">Dar meia volta e retornar à encruzilhada</a><br>
    <br><a href="/">Voltar ao início</a>
    """
    
    return render_template_string(html, resultado=resultado, mensagem=mensagem, extra_texto=extra_texto)

@app.route("/combate", methods=["GET", "POST"])
def combate():
    fim = None

    # Inicializa status do combate se não existir na sessão
    # Inicializa status do jogador se não existir
    if "player_energia" not in session:
        session["player_energia"] = 10  # ou valor padrão que você deseja
    if "player_habilidade" not in session:
        session["player_habilidade"] = 5  # ou valor padrão

    if "orc_energia" not in session:
        session["orc_energia"] = 10  # energia do inimigo
        session["orc_habilidade"] = 4  # habilidade do inimigo
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Quando clicar em "Atacar" via AJAX
    if request.method == "POST":
        # Rolagens
        orc_roll = random.randint(1, 6) + random.randint(1, 6) + session["orc_habilidade"]
        player_roll = random.randint(1, 6) + random.randint(1, 6) + session["player_habilidade"]

        if player_roll > orc_roll:
            session["orc_energia"] -= 2
            mensagem = f"Você venceu a rodada! Orc perde 2 de energia."
        elif orc_roll > player_roll:
            session["player_energia"] -= 2
            mensagem = f"Orc venceu a rodada! Você perde 2 de energia."
        else:
            mensagem = "Empate! Ninguém sofre dano."

        # Verifica se alguém morreu
        if session["orc_energia"] <= 0:
            fim = """ <img src='/static/imagens/continueaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    ✅ Você derrotou a Orc! Continue sua jornada."""
        elif session["player_energia"] <= 0:
            fim = """ <img src='/static/imagens/fimaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    💀 Você foi derrotado... Fim da aventura.
    """

        # Retorno AJAX
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "orc_roll": orc_roll,
                "player_roll": player_roll,
                "player_energia": session["player_energia"],
                "orc_energia": session["orc_energia"],
                "mensagem": mensagem,
                "fim": fim
            })

    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status {  display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 24px; }
        .barra-container { width: 200px; height: 25px; background: #ddd; border-radius: 5px; }
        .barra { height: 100%; border-radius: 5px; transition: width 0.3s, background 0.3s; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <h1>Combate Iniciado!</h1>
    <p>A criatura que acorda é um ORC. Ele se levanta rapidamente e tenta soar um alarme. Você precisa atacá-lo imediatamente!</p>
    <img src="/static/imagens/pag16.png" alt="Caverna Oeste" style="width:450px;"><br>

    <div id="status">
        <div>
            <h2><b>Orc</b></h2>
             <div class="barra-container">
                <div id="barra-orc" class="barra" style="width:{{orc_energia * 100 / 10}}%; background:green;"></div>
            </div>
            <p>Energia: <span id="orc-energia">{{orc_energia}}</span></p>
            <p>Habilidade: {{orc_habilidade}}</p>
        </div>
        <div>
            <h2><b>Você</b></h2>
            <div class="barra-container">
                <div id="barra-jogador" class="barra" style="width:{{player_energia * 100 / 10}}%; background:green;"></div>
            </div>
            <p>Energia: <span id="player-energia">{{player_energia}}</span></p>
            <p>Habilidade: {{player_habilidade}}</p>
        </div>
    </div>

    <p id="mensagem">{{mensagem}}</p>

    <h3>Rolagens:</h3>
    <p>Você: <span id="player-roll">?</span> | Orca: <span id="orc-roll">?</span></p>

    <div id="acoes">
        {% if not fim %}
            <button type="button" onclick="atacar()">⚔️ Atacar!</button>
        {% else %}
            <h2>{{fim}}</h2>
            {% if "derrotou" in fim %}
                <a href="/norte">Continuar pela passagem</a>
            {% endif %}
            <br><a href="/">Voltar ao início</a>
            <a href="/reset">Reiniciar combate</a>
        
        {% endif %}
    </div>

    <script>
    function atualizarBarra(id, valor) {
        const barra = document.getElementById(id);
        const largura = Math.max(0, valor) * 10; // % (supondo max 10)
        barra.style.width = largura + "%";
        if (valor > 6) barra.style.background = "green";
        else if (valor > 3) barra.style.background = "yellow";
        else barra.style.background = "red";
    }

    async function atacar() {
        let playerSpan = document.getElementById("player-roll");
        let orcSpan = document.getElementById("orc-roll");

        function animarRolagem(count = 0) {
            if (count >= 10) return;
            playerSpan.textContent = Math.floor(Math.random() * 6 + 1) + Math.floor(Math.random() * 6 + 1);
            orcSpan.textContent = Math.floor(Math.random() * 6 + 1) + Math.floor(Math.random() * 6 + 1);
            setTimeout(() => animarRolagem(count + 1), 50);
        }

        animarRolagem();

        setTimeout(async () => {
            let response = await fetch("/combate", {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            let data = await response.json();

            playerSpan.textContent = data.player_roll;
            orcSpan.textContent = data.orc_roll;
            document.getElementById("player-energia").textContent = data.player_energia;
            document.getElementById("orc-energia").textContent = data.orc_energia;
            document.getElementById("mensagem").textContent = data.mensagem;

            atualizarBarra("barra-jogador", data.player_energia);
            atualizarBarra("barra-orc", data.orc_energia);

            if (data.fim) {
                let acoesDiv = document.getElementById("acoes");
                let html = `<h2>${data.fim}</h2>`;
                if (data.fim.includes("derrotou")) {
                    html += `<a href="/norte">Continuar pela passagem</a><br>`;
                }
                html += `<a href="/">Voltar ao início</a><br>`;
                html += `<a href="/reset">Reiniciar combate</a>`;
                acoesDiv.innerHTML = html;
            }
        }, 600);
    }
    </script>
    </body>
    </html>
    """

    return render_template_string(
        html,
        mensagem=mensagem,
        player_energia=session["player_energia"],
        orc_energia=session["orc_energia"],
        player_habilidade=session["player_habilidade"],
        orc_habilidade=session["orc_habilidade"],
        fim=fim
    )

    
@app.route("/reset")
def reset():
 # Reinicia apenas os dados do combate
    session.pop("orc_energia", None)
    session.pop("orc_habilidade", None)
    session.pop("player_energia", None)
    session.pop("player_habilidade", None)
    
    # Redireciona para a página de combate
    return redirect("/combate")

@app.route("/norte")
def norte():
    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag17.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você virou para o norte</h1>
    <p>Você continua pela passagem e, à sua esquerda, encontra uma porta de madeira rústica. Ao parar junto a ela, você ouve um som áspero, que pode ser de uma criatura roncando.</p>
    <br>
    <a href="/abrir-a-porta">Abrir a porta</a>
    <a href="/deixar-amuleto">Seguir adiante para o norte</a>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/deixar-amuleto")
def deixar_amuleto():
    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag195.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você seguiu adiante</h1>
    <p>Você continua pela passagem e, mais adiante, vê outra porta na parede oeste. Você escuta, mas não ouve nada. A partir daqui, você tem uma nova escolha:</p>
    <br>
    <a href="/nova-porta">Tentar abrir esta nova porta</a>
    <a href="/encruzilhada">Continuar na direção norte</a>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """

       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/nova-porta")
def nova_porta():
    html = STATUS_HTML +"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag21.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você abriu a nova porta</h1>
    <p>Você abre a porta e entra em um aposento grande e quadrado. Ele parece estar completamente vazio, a não ser por uma argola de ferro no centro do assoalho. A partir daqui, você tem uma nova escolha:.</p>
    <br>
    <a href="/puxar-argola">Puxar a argola</a>
    <a href="/encruzilhada">Sair do aposento e continuar para o norte </a><br>
    <br>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/puxar-argola", methods=["GET", "POST"])
def puxar_argola():
    resultado = None
    mensagem = ""
    extra_texto = ""

    if request.method == "POST":
        resultado = random.randint(1, 20)
        if resultado > 10:
            mensagem = "✅ Você teve sorte! Os dados não te acertaram e você consegue puxar a argola sem problemas."
            extra_texto = "Você sai do aposento e retorna a passagem."
        else:
            mensagem = "💀 Você não teve sorte! Dois dardos envenenados o atingem. Você perde 2 pontos de ENERGIA!"
            
            # Reduz energia em 2
            if "player_energia" in session:
                session["player_energia"] = max(session["player_energia"] - 2, 0)

    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Puxar Argola</title>
    <style>
        #status { display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 { text-shadow: 2px 2px 4px black; text-align: center; }
        h2 { font-size: 36px; } 
        img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
        a {
            display: inline-block;
            padding: 10px 15px;
            background-color: #333;
            color: white;
            border-radius: 5px;
            font-size: 32px;
            text-decoration: none;
            margin-top: 15px;
        }
        a:hover {
            background-color: #fff;
            color: black;
            transform: scale(1.05);
            transition: 0.3s;
        }
        img:hover { transform: scale(1.05); transition: 0.3s; }
        button { font-size: 32px; padding: 10px 20px; cursor: pointer; }
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag6.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você tenta puxar a argola</h1>
    <p>Enquanto você está lutando para puxar a argola do teto, ouve dois pequenos estalos e depois silvos, quando dois dardos minúsculos são disparados na sua direção. <b>Teste sua sorte!</b></p>
    <form method="POST">
        <button type="submit">🎲 Testar Sorte</button>
    </form>
    
    {% if resultado %}
        <h2>Resultado: {{resultado}}</h2>
        <p>{{mensagem}}</p>
        
        {% if resultado > 10 %}
            <p>{{extra_texto}}</p>
            <a href="/encruzilhada">Retornar ao tunel</a>
        {% else %}
            <a href="/encruzilhada">Retornar ao tunel</a>
        {% endif %}
    {% endif %}
    
    <br><a href="/">Voltar ao início</a>
    </body>
    </html>
    """
    return render_template_string(html, resultado=resultado, mensagem=mensagem, extra_texto=extra_texto)

    

@app.route("/abrir-a-porta")
def abrir_a_porta():
    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag18.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você abriu a porta</h1>
    <p>A porta se abre e revela um aposento pequeno e com um cheiro forte. No centro, há uma mesa de madeira com uma vela acesa e uma pequena caixa de madeira em cima. Em um canto, dormindo sobre palha, está um ser baixo e robusto com um rosto feio e cheio de verrugas, o mesmo tipo de criatura que você encontrou no posto de sentinela..</p>
    <br>
    <a href="/deixar-amuleto">Retornar ao corredor e seguir para o norte</a>
    <a href="/pegar-caixa">Tentar pegar a caixa sem acordar o ser; (Teste sua sorte) </a>
    <br>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/pegar-caixa", methods=["GET", "POST"])
def pegar_caixa():
    resultado = None
    mensagem = ""
    extra_texto = ""
    
    if request.method == "POST":
        resultado = random.randint(1, 20)
        if resultado > 10:
            mensagem = "✅ Você teve sorte! A criatura não acorda e você continua."
            extra_texto = "Você sai do aposento e abre a caixa na passagem."
        else:
            mensagem = "💀 Você não teve sorte! A criatura que dormia acorda sobressaltada. Ela se levanta e avança desarmada, mas seus dentes afiados parecem perigosos"
    
    html = STATUS_HTML + """
     <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>

    <img src="/static/imagens/pag7.png" alt="Caverna Oeste" style="width:450px;"><br>
    <h1>Você tenta pegar a caixa</h1>
    <p>Você tentou pegar a caixa <b>Teste a sua Sorte</b>.</p>
    
    <form method="POST">
        <button type="submit">🎲 Testar Sorte</button>
    </form>
    
    {% if resultado %}
        <h2>Resultado: {{resultado}}</h2>
        <p>{{mensagem}}</p>
        
        {% if resultado > 10 %}
            <p>{{extra_texto}}</p>
            <a href="/retornar-corredor">Pegar a caixa e sair</a>
        {% else %}
            <a href="/combateorca">Entrar em combate</a>
        {% endif %}
    {% endif %}
    <br>
    <br>
    <br><a href="/">Voltar ao início</a>
    <a href="/deixar-amuleto">Dar meia volta e retornar à encruzilhada</a><br>
    <br>
    <br>
    </body>
    </html>
    """
    
    return render_template_string(html, resultado=resultado, mensagem=mensagem, extra_texto=extra_texto)
@app.route("/combateorca", methods=["GET", "POST"])
def combate_orca():
    fim = None

    # Inicializa status do combate se não existir na sessão
    if "orc_energia" not in session:
        session["orc_energia"] = 6  # energia do inimigo
        session["orc_habilidade"] = 4  # habilidade do inimigo

    if "player_energia" not in session:
        session["player_energia"] = 10  # energia do jogador
    if "player_habilidade" not in session:
        session["player_habilidade"] = 8  # habilidade do jogador

    mensagem = "O combate começou! Prepare-se!" if request.method == "GET" else ""

    # Quando clicar em "Atacar" via AJAX
    if request.method == "POST":
        # Rolagens
        orca_roll = random.randint(1, 6) + random.randint(1, 6) + session["orc_habilidade"]
        player_roll = random.randint(1, 6) + random.randint(1, 6) + session["player_habilidade"]

        if player_roll > orca_roll:
            session["orc_energia"] -= 2
            mensagem = "Você venceu a rodada! Orca perde 2 de energia."
        elif orca_roll > player_roll:
            session["player_energia"] -= 2
            mensagem = "Orca venceu a rodada! Você perde 2 de energia."
        else:
            mensagem = "Empate! Ninguém sofre dano."


         # Verifica se alguém morreu
        if session["orc_energia"] <= 0:
            fim = """ <img src='/static/imagens/continueaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    ✅ Você derrotou a Orca! Continue sua jornada."""
        elif session["player_energia"] <= 0:
            fim = """ <img src='/static/imagens/fimaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    💀 Você foi derrotado... Fim da aventura.
    """


        # Retorno AJAX
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "orca_roll": orca_roll,
                "player_roll": player_roll,
                "player_energia": session["player_energia"],
                "orca_energia": session["orc_energia"],
                "mensagem": mensagem,
                "fim": fim
            })

    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }  
    </style>
    </head>
    <body>
    <h1>Combate Iniciado!</h1>
    <p>A criatura que acorda é um ORCA. Ele se levanta rapidamente e tenta soar um alarme. Você precisa atacá-lo imediatamente!</p>
    <img src="/static/imagens/pag19.png" alt="Caverna Oeste" style="width:450px;"><br>

    <div id="status">
        <div>
            <p><b>Orca</b></p>
            <ul>
                <li>HABILIDADE: {{orc_habilidade}}</li>
                <li>ENERGIA: <span id="orc-energia">{{orc_energia}}</span></li>
            </ul>
        </div>
        <div>
            <p><b>Você</b></p>
            <ul>
                <li>HABILIDADE: {{player_habilidade}}</li>
                <li>ENERGIA: <span id="player-energia">{{player_energia}}</span></li>
            </ul>
        </div>
    </div>

    <p id="mensagem">{{mensagem}}</p>

    <h3>Rolagens:</h3>
    <p>Você: <span id="player-roll">?</span> | Orca: <span id="orc-roll">?</span></p>

    <div id="acoes">
        {% if not fim %}
            <button type="button" onclick="atacar()">⚔️ Atacar!</button>
        {% else %}
            <h2>{{fim|safe}}</h2>
            {% if "derrotou" in fim %}
                <a href="/retornar-corredor">Continuar pela passagem</a>
            {% endif %}
            <br><a href="/">Voltar ao início</a>
            <a href="/reset">Reiniciar combate</a>
        {% endif %}
    </div>

    <script>
    async function atacar() {
        let playerSpan = document.getElementById("player-roll");
        let orcSpan = document.getElementById("orc-roll");

        for (let i = 0; i < 10; i++) {
            playerSpan.textContent = Math.floor(Math.random() * 12 + 2);
            orcSpan.textContent = Math.floor(Math.random() * 12 + 2);
            await new Promise(r => setTimeout(r, 50));
        }

        let response = await fetch("/combateorca", {
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });
        let data = await response.json();

        playerSpan.textContent = data.player_roll;
        orcSpan.textContent = data.orca_roll;
        document.getElementById("player-energia").textContent = data.player_energia;
        document.getElementById("orc-energia").textContent = data.orca_energia;
        document.getElementById("mensagem").textContent = data.mensagem;

        if (data.fim) {
            let acoesDiv = document.getElementById("acoes");
            let html = `<h2>${data.fim}</h2>`;
            if (data.fim.includes("derrotou")) {
                html += `<a href="/retornar-corredor">Continuar pela passagem</a>`;
            }
            html += `<a href="/">Voltar ao início</a>`;
            html += `<a href="/reset">Reiniciar combate</a>`;
            acoesDiv.innerHTML = html;
        }
    }
    </script>
    </body>
    </html>
    """

    return render_template_string(
        html,
        mensagem=mensagem,
        player_energia=session["player_energia"],
        orc_energia=session["orc_energia"],
        player_habilidade=session["player_habilidade"],
        orc_habilidade=session["orc_habilidade"],
        fim=fim
    )

    
@app.route("/reset")
def reset_combate():
    # Limpa apenas os dados do combate, mantendo a ficha do jogador
    session.pop("orc_energia", None)
    session.pop("orc_habilidade", None)
    session.pop("player_energia", None)
    session.pop("player_habilidade", None)
    return "<h2>Combate reiniciado!</h2><a href='/combateorca'>Voltar</a>"

@app.route("/retornar-corredor")
def retornar_corredor():
    # Atualiza a ficha na sessão
    if "player_sorte" in session:
                session["player_sorte"] += 2
    else:
                session["player_sorte"] = 2  # caso não exista ainda
    html = STATUS_HTML + """
     <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }  
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag20.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Você retornou ao corredor</h1>
    <p>Você retorna ao corredor e abre a caixa, dentro dela, você encontra uma Peça de Ouro e um pequeno camundongo, que deveria ser o animal de estimação da criatura. Você guarda a moeda, solta o camundongo e ele sai correndo. <b>Você ganha 2 pontos de SORTE </b> e continua a jornada</a><br>
    <br>
    <a href="/deixar-amuleto">Seguir adiante</a>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)
@app.route("/encruzilhada")
def encruzilhada():
    html = STATUS_HTML + """
     <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag22.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Continuar na direção norte</h1>
    <p>A passagem segue para o leste por vários metros e depois para o norte, até que você chega a uma encruzilhada. Você pode escolher seguir para:</a><br>
    <br>

    <a href="/norte2">Continuar para o norte</a>
    <a href="/leste2">Virar para o leste</a>
    <a href="/oeste2">Virar para o oeste</a>
    <a href="/nova-porta">Voltar para a porta fechada</a>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)

@app.route("/oeste2")
def oeste2():
    html = STATUS_HTML + """
     <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status { display: flex; gap: 50px; 
        justify-content: center; margin-bottom: 20px; font-size: 24px; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag22.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Continuar na direção oeste</h1>
    <p>Depois de alguns metros, você chega a outra junção de três caminhos. Você pode ir na direção:<br>
    <br>

    <a href="/norte2">Continuar para o norte</a>
    <a href="/leste3">Virar para o leste</a>
    <a href="/encruzilhada">Voltar para a encruzilhada anterior</a>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)

    # STATUS_HTML contém os dados iniciais do personagem
@app.route("/norte2", methods=["GET", "POST"])
def norte2():
    fim = None
    
    # Inicializa sessão do jogador e Bárbaro
    if "player_energia" not in session:
        session["player_energia"] = 10
    if "player_habilidade" not in session:
        session["player_habilidade"] = 7
    if "barbaro_energia" not in session:
        session["barbaro_energia"] = 6
        session["barbaro_habilidade"] = 7
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Inicializa status do combate se não existir na sessão
    if "barbaro_energia" not in session:
        session["barbaro_energia"] = 6  # energia do inimigo
        session["barbaro_habilidade"] = 7  # habilidade do inimigo
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Quando clicar em "Atacar" via AJAX
    if request.method == "POST":
        # Rolagens
        barbaro_roll = random.randint(1, 6) + random.randint(1, 6) + session["barbaro_habilidade"]
        player_roll = random.randint(1, 6) + random.randint(1, 6) + session["player_habilidade"]

        if player_roll > barbaro_roll:
            session["barbaro_energia"] -= 2
            mensagem = f"Você venceu a rodada! Bárbaro perde 2 de energia."
        elif barbaro_roll > player_roll:
            session["player_energia"] -= 2
            mensagem = f"Bárbaro venceu a rodada! Você perde 2 de energia."
        else:
            mensagem = "Empate! Ninguém sofre dano."

        # Verifica se alguém morreu
        if session["barbaro_energia"] <= 0:
            fim = """<img src='/static/imagens/continueaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    ✅ Você derrotou o Bárbaro! Continue sua jornada."""
        elif session["player_energia"] <= 0:
            fim = """<img src='/static/imagens/fimaventura.png' alt='Montanha do Cume de Fogo' style='width:450px;'><br>
    💀 Você foi derrotado... Fim da aventura."""

        # Retorno AJAX
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({
                "barbaro_roll": barbaro_roll,
                "player_roll": player_roll,
                "player_energia": session["player_energia"],
                "barbaro_energia": session["barbaro_energia"],
                "mensagem": mensagem,
                "fim": fim
            })

    html = STATUS_HTML + """
     <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Combate</title>
    <style>
        #status {  display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 24px; }
        .barra-container { width: 200px; height: 25px; background: #ddd; border-radius: 5px; }
        .barra { height: 100%; border-radius: 5px; transition: width 0.3s, background 0.3s; }
        ul { list-style-type: none; padding: 0; }
         body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        
        h1 {
        text-shadow: 2px 2px 4px black;
         text-align: center; }
        h2 { 
          font-size: 36px; } 
         img { display: block; margin: 0 auto; }
        h3 { font-size: 28px; }
        p { font-size: 24px; } 
     a   {
        justify-content: justify;
        padding: 10px 15px;
        background-color: #333;
        color: white;
        border-radius: 5px;
        text-align: center;
        font-size: 32px;
        text-decoration: none;
        justify-content: center;
        }
    a:hover {
        background-color:#ffffff;
        color: black;
        transform: scale(1.05);
        transition: transform 0.3s ease;
        }
    img:hover { transform: scale(1.05);
        transition: transform 0.3s ease; }
    button { font-size: 32px; padding: 10px 20px; cursor: pointer;
    }   
    </style>
    </head>
    <body>
    <img src="/static/imagens/pag5.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Continuar na direção norte</h1>
    <p>A passagem termina em uma porta sólida. Você não ouve nada ao escutar, então tenta a maçaneta, que gira, e você entra no aposento.</p>
    <br>
    <p>Assim que você olha em volta, ouve um grito de guerra atrás de você e, ao se virar, vê um homem selvagem pulando em sua direção com uma grande arma</p>

    <h1>Combate Iniciado!</h1>
    <br>
    <p>Um BÁRBARO tenta te atacar. Você precisa atacá-lo imediatamente!</p>
    <img src="/static/imagens/pag4.png" alt="Caverna Norte" style="width:450px;"><br>

    <div id="status">
        <div>
            <h2>Bárbaro</h2>
            <div class="barra-container">
                <div id="barra-barbaro" class="barra" style="width:{{barbaro_energia * 100 / 10}}%; background:green;"></div>
            </div>
            <p>Energia: <span id="barbaro-energia">{{barbaro_energia}}</span></p>
            <p>Habilidade: {{barbaro_habilidade}}</p>
        </div>
        <div>
            <h2>Você</h2>
            <div class="barra-container">
                <div id="barra-jogador" class="barra" style="width:{{player_energia * 100 / 10}}%; background:green;"></div>
            </div>
            <p>Energia: <span id="player-energia">{{player_energia}}</span></p>
            <p>Habilidade: {{player_habilidade}}</p>
        </div>
    </div>

    <p id="mensagem">{{mensagem}}</p>

    <h3>Rolagens:</h3>
    <p>Você: <span id="player-roll">?</span> | Bárbaro: <span id="barbaro-roll">?</span></p>

    <div id="acoes">
        {% if not fim %}
            <button type="button" onclick="atacar()">⚔️ Atacar!</button>
            <br>
            <br>
        {% else %}
            <h2>{{fim}}</h2>
            {% if "derrotou" in fim %}
                <a href="/norte">Continuar pela passagem</a>
            {% endif %}
            <br><a href="/">Voltar ao início</a>
            <a href="/reset">Reiniciar combate</a>
        {% endif %}
    </div>

    <script>
    function atualizarBarra(id, valor) {
        const barra = document.getElementById(id);
        const largura = Math.max(0, valor) * 10; // % (supondo max 10)
        barra.style.width = largura + "%";
        if (valor > 6) barra.style.background = "green";
        else if (valor > 3) barra.style.background = "yellow";
        else barra.style.background = "red";
    }

    async function atacar() {
        let playerSpan = document.getElementById("player-roll");
        let barbaroSpan = document.getElementById("barbaro-roll");

        function animarRolagem(count = 0) {
            if (count >= 10) return;
            playerSpan.textContent = Math.floor(Math.random() * 6 + 1) + Math.floor(Math.random() * 6 + 1);
            barbaroSpan.textContent = Math.floor(Math.random() * 6 + 1) + Math.floor(Math.random() * 6 + 1);
            setTimeout(() => animarRolagem(count + 1), 50);
        }

        animarRolagem();

        setTimeout(async () => {
            let response = await fetch("/norte2", {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            let data = await response.json();

            playerSpan.textContent = data.player_roll;
            barbaroSpan.textContent = data.barbaro_roll;
            document.getElementById("player-energia").textContent = data.player_energia;
            document.getElementById("barbaro-energia").textContent = data.barbaro_energia;
            document.getElementById("mensagem").textContent = data.mensagem;

            atualizarBarra("barra-jogador", data.player_energia);
            atualizarBarra("barra-barbaro", data.barbaro_energia);

            if (data.fim) {
                let acoesDiv = document.getElementById("acoes");
                let html = `<h2>${data.fim}</h2>`;
                if (data.fim.includes("derrotou")) {
                    html += `<a href="/norte">Continuar pela passagem</a><br>`;
                }
                html += `<a href="/">Voltar ao início</a><br>`;
                html += `<a href="/reset3">Reiniciar combate</a>`;
                acoesDiv.innerHTML = html;
            }
        }, 600);
    }
    </script>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(
    html,
    mensagem=mensagem,
    player_energia=session["player_energia"],
    barbaro_energia=session["barbaro_energia"],
    player_habilidade=session["player_habilidade"],
    barbaro_habilidade=session["barbaro_habilidade"],
    fim=fim
)
@app.route("/reset3")
def reset3():
    session.pop("barbaro_energia", None)
    session.pop("barbaro_habilidade", None)
    session.pop("player_energia", None)
    session.pop("player_habilidade", None)
    return redirect("/norte2")



if __name__ == "__main__":
    app.run(debug=True)