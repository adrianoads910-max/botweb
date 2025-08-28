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
    # --- ALTERADO: Adicionadas colunas 'habilidade_1' e 'habilidade_2' ---
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
                    pagina_atual TEXT,
                    habilidade_1 TEXT,
                    habilidade_2 TEXT,
                    xp INTEGER DEFAULT 0,          -- <-- ADICIONAR
                    habilidade_3 TEXT DEFAULT 'Nenhuma' -- <-- ADICIONAR
                )''')
    conn.commit()
    conn.close()

# --- ALTERADO: Adicionado 'xp' e 'habilidade_3' na criação ---
def salvar_personagem(nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, hab1, hab2):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Adicionamos as colunas e os valores iniciais (0 para xp, 'Nenhuma' para hab3)
    c.execute('''INSERT INTO personagens 
        (nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, pagina_atual, habilidade_1, habilidade_2, xp, habilidade_3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'Nenhuma')''',
        (nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, '/aventura', hab1, hab2))
    
    novo_id = c.lastrowid
    conn.commit()
    conn.close()
    return novo_id

# --- ALTERADO: Adicionado 'xp' e 'habilidade_3' no update ---
def atualizar_personagem(pid, energia, sorte, provisoes, pagina_atual, xp, hab3):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''UPDATE personagens 
                 SET energia = ?, sorte = ?, provisoes = ?, pagina_atual = ?, xp = ?, habilidade_3 = ?
                 WHERE id = ?''', 
              (energia, sorte, provisoes, pagina_atual, xp, hab3, pid))
    conn.commit()
    conn.close()

def listar_personagens():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, nome, raca, classe, avatar FROM personagens")
    personagens = c.fetchall()
    conn.close()
    return personagens

def excluir_personagem_por_id(pid):
    """Exclui um personagem do banco de dados pelo seu ID."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM personagens WHERE id=?", (pid,))
    conn.commit()
    conn.close()

# Em carregar_personagem_por_id()
def carregar_personagem_por_id(pid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # --- ALTERADO: Seleciona também xp e habilidade_3 ---
    c.execute("SELECT id, nome, raca, classe, habilidade, energia, max_energia, sorte, provisoes, avatar, pagina_atual, habilidade_1, habilidade_2, xp, habilidade_3 FROM personagens WHERE id=?", (pid,))
    personagem = c.fetchone()
    conn.close()
    return personagem

if not os.path.exists(DB_FILE):
    init_db()

# Dicionários e listas de Raças/Classes (sem alterações)
MODIFICADORES = {
    "Humano": {
        "Guerreiro": {"HABILIDADE": 2, "ENERGIA": 1, "SORTE": 0},
        "Mago": {"HABILIDADE": 0, "ENERGIA": 0, "SORTE": 1},
        "Arqueiro": {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 1},
        "Ladino": {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 1},
    },
    "Elfo": {
        "Guerreiro": {"HABILIDADE": 4, "ENERGIA": 0, "SORTE": 1},
        "Mago": {"HABILIDADE": 2, "ENERGIA": -1, "SORTE": 3},
        "Arqueiro": {"HABILIDADE": 4, "ENERGIA": -1, "SORTE": 3},
        "Ladino": {"HABILIDADE": 4, "ENERGIA": -1, "SORTE": 2},
    },
    "Anão": {
        "Guerreiro": {"HABILIDADE": 3, "ENERGIA": 3, "SORTE": -1},
        "Mago": {"HABILIDADE": 1, "ENERGIA": 2, "SORTE": 0},
        "Arqueiro": {"HABILIDADE": 3, "ENERGIA": 2, "SORTE": 0},
        "Ladino": {"HABILIDADE": 3, "ENERGIA": 2, "SORTE": 0},
    },
    "Meio-Orc": {
        "Guerreiro": {"HABILIDADE": 4, "ENERGIA": 2, "SORTE": -1},
        "Mago": {"HABILIDADE": 2, "ENERGIA": 1, "SORTE": 0},
        "Arqueiro": {"HABILIDADE": 4, "ENERGIA": 1, "SORTE": 0},
        "Ladino": {"HABILIDADE": 4, "ENERGIA": 1, "SORTE": 0},
    },
    "Halfling": {
        "Guerreiro": {"HABILIDADE": 1, "ENERGIA": 1, "SORTE": 1},
        "Mago": {"HABILIDADE": -1, "ENERGIA": 0, "SORTE": 2},
        "Arqueiro": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2},
        "Ladino": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2},
    },
    "Gnomo": {
        "Guerreiro": {"HABILIDADE": 1, "ENERGIA": 1, "SORTE": 1},
        "Mago": {"HABILIDADE": -1, "ENERGIA": 0, "SORTE": 3},
        "Arqueiro": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 3},
        "Ladino": {"HABILIDADE": 1, "ENERGIA": 0, "SORTE": 2},
    },
    "Meio-Elfo": {
        "Guerreiro": {"HABILIDADE": 2, "ENERGIA": 0, "SORTE": 3},
        "Mago": {"HABILIDADE": 0, "ENERGIA": -1, "SORTE": 5},
        "Arqueiro": {"HABILIDADE": 2, "ENERGIA": -1, "SORTE": 5},
        "Ladino": {"HABILIDADE": 2, "ENERGIA": -1, "SORTE": 4},
    },
    "Dinossauro": {
        "Guerreiro": {"HABILIDADE": 5, "ENERGIA": 3, "SORTE": -2},
        "Mago":      {"HABILIDADE": -2, "ENERGIA": 2, "SORTE": -1},
        "Arqueiro":  {"HABILIDADE": 3, "ENERGIA": 1, "SORTE": -1},
        "Ladino":    {"HABILIDADE": 3, "ENERGIA": 1, "SORTE": -3},
    },
    "Draconiano": {
        "Guerreiro": {"HABILIDADE": 5, "ENERGIA": 4, "SORTE": 0},
        "Mago":      {"HABILIDADE": 0, "ENERGIA": 3, "SORTE": 1},
        "Arqueiro":  {"HABILIDADE": 4, "ENERGIA": 2, "SORTE": 1},
        "Ladino":    {"HABILIDADE": 3, "ENERGIA": 3, "SORTE": 3},
    }

}

RACAS = list(MODIFICADORES.keys())
CLASSES = list(next(iter(MODIFICADORES.values())).keys())
# (Adicione este bloco de código perto do início do seu arquivo)

HABILIDADES_DATA = {
    # Ataques para Classes Físicas
    "Ataque Poderoso": {"bonus": 2, "tipo": "ataque", "classes": ["Guerreiro", "Arqueiro", "Ladino"]},
    "Golpe Preciso": {"bonus": 1, "tipo": "ataque", "classes": ["Guerreiro", "Arqueiro", "Ladino"]},
    "Fúria de Batalha": {"bonus": 3, "tipo": "ataque", "classes": ["Guerreiro"]},
    "Tiro Certeiro": {"bonus": 3, "tipo": "ataque", "classes": ["Arqueiro"]},
    "Ataque Furtivo": {"bonus": 3, "tipo": "ataque", "classes": ["Ladino"]},

    # Magias para Mago
    "Bola de Fogo": {"bonus": 3, "tipo": "magia", "classes": ["Mago"]},
    "Raio de Gelo": {"bonus": 2, "tipo": "magia", "classes": ["Mago"]},
    "Míssil Mágico": {"bonus": 1, "tipo": "magia", "classes": ["Mago"]},
}

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
        "player_pagina_atual": session.get("player_pagina_atual", "/aventura"),
         # --- LINHAS ADICIONADAS ---
        # Agora estamos entregando as habilidades para o template da ficha
        "player_habilidade_1": session.get("player_habilidade_1", "Nenhuma"),
        "player_habilidade_2": session.get("player_habilidade_2", "Nenhuma"),
        "player_habilidade_3": session.get("player_habilidade_3", "Nenhuma"), # Adicionado no passo anterior
        "player_xp": session.get("player_xp", 0)  # <-- ADICIONE ESTA LINHA
    }
    return stats

# (Substitua toda a sua variável STATUS_HTML por esta)

STATUS_HTML = """
{% if player_nome %}
<style>
    /* --- REGRA ÚNICA E CORRIGIDA PARA A FICHA --- */
    .character-sheet { 
        position: fixed; 
        top: 10px; 
        right: 10px; 
        width: 280px;      /* Largura aumentada */
        min-width: 280px;  /* Largura mínima aumentada */
        min-height: 150px; 
        border: 2px solid #555; 
        background-color: #f9f9f9; 
        padding: 10px; 
        border-radius: 8px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.2); 
        font-family: sans-serif; 
        z-index: 1000; 
        user-select: none; 
        transition: all 0.3s ease;
    }

    /* --- ESTILOS DAS BARRAS DE PROGRESSO --- */
    .barra-container { 
        width: 100%;
        height: 12px; 
        background-color: #555; 
        border: 1px solid #333;
        border-radius: 5px; 
        margin-top: 4px;
    }
    .barra { 
        height: 100%; 
        border-radius: 4px; 
        transition: width 0.4s ease-in-out, background-color 0.4s ease-in-out; 
    }

    /* --- OUTROS ESTILOS DA FICHA --- */
    #character-sheet-header { 
        cursor: pointer; 
        background-color: #e0e0e0; 
        margin: -10px -10px 10px -10px; 
        padding: 10px; 
        border-top-left-radius: 8px; 
        border-top-right-radius: 8px; 
        border-bottom: 2px solid #ccc; 
        text-align: center; 
        display: flex;
        flex-direction: column; 
        align-items: center;
    }
    .character-avatar { 
        width: 250px; 
        height: 250px; 
        border-radius: 50%; 
        border: 3px solid #555; 
        margin-bottom: 5px; 
        object-fit: cover; 
    }
    .character-sheet h3 { margin: 0; padding: 0; }
    .character-sheet ul { list-style: none; padding: 0; margin: 0; }
    .character-sheet li { 
        padding: 4px 0; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        font-size: 0.9em;
    }
    .action-button { 
        padding: 5px 10px; 
        font-size: 0.8em; 
        cursor: pointer; 
        border: 1px solid #888; 
        border-radius: 5px; 
        background-color: #d4edda; 
        margin-left: 10px; 
    }
    .action-button:hover { background-color: #c3e6cb; }
    .action-button:disabled { background-color: #ccc; cursor: not-allowed; }
    .save-button { background-color: #d1ecf1; }
    .save-button:hover { background-color: #bee5eb; }
    .rest-button { background-color: #fff3cd; }
    .rest-button:hover { background-color: #ffeeba; }
    #save-status { font-size: 0.8em; color: green; margin-left: 5px; }
    /* Linha CORRIGIDA */
    /* Linha ATUAL (incorreta) */
    .minimizado ul, .minimizado .action-buttons-container { display: none !important; }

    /* --- ESTILOS DO REDIMENSIONAMENTO --- */
    .resizer {
        width: 10px; height: 10px;
        position: absolute;
        background: transparent;
        z-index: 1001;
    }
    .resizer.nw { top: -2px; left: -2px; cursor: nwse-resize; }
    .resizer.ne { top: -2px; right: -2px; cursor: nesw-resize; }
    .resizer.sw { bottom: -2px; left: -2px; cursor: nesw-resize; }
    .resizer.se { bottom: -2px; right: -2px; cursor: nwse-resize; }
    .resizer.n { top: -2px; left: 50%; transform: translateX(-50%); cursor: ns-resize; width: 100%; height: 5px; }
    .resizer.s { bottom: -2px; left: 50%; transform: translateX(-50%); cursor: ns-resize; width: 100%; height: 5px; }
    .resizer.e { top: 50%; right: -2px; transform: translateY(-50%); cursor: ew-resize; width: 5px; height: 100%; }
    .resizer.w { top: 50%; left: -2px; transform: translateY(-50%); cursor: ew-resize; width: 5px; height: 100%; }
</style>

<div class="character-sheet" id="character-sheet">
    <div id="character-sheet-header">
        {% if player_avatar %}
            <img src="{{ url_for('static', filename='avatares/' + player_avatar) }}" alt="Avatar" class="character-avatar">
        {% endif %}
        <h3>{{ player_nome }}</h3>
    </div>
    <ul>
        <li style="flex-direction: column; align-items: flex-start;">
            <div style="width: 100%; display: flex; justify-content: space-between;">
                <b>ENERGIA:</b>
                <span><span id="sheet-energia">{{ player_energia }}</span> / {{ player_max_energia }}</span>
            </div>
            <div class="barra-container">
                <div id="barra-energia" class="barra"></div>
            </div>
        </li>
        <li><b>HABILIDADE:</b> <span id="sheet-habilidade">{{ player_habilidade }}</span></li>
        <li><b>SORTE:</b> <span id="sheet-sorte">{{ player_sorte }}</span></li>
        <li style="flex-direction: column; align-items: flex-start;">
            <div style="width: 100%; display: flex; justify-content: space-between;">
                <b>XP:</b>
                <span><span id="sheet-xp">{{ player_xp }}</span> / 100</span>
            </div>
            <div class="barra-container">
                <div id="barra-xp" class="barra"></div>
            </div>
        </li>
        <li>
            <b>PROVISÕES:</b> 
            <div>
                <span id="sheet-provisions">{{ player_provisions }}</span>
                <button id="provision-btn" class="action-button" onclick="usarProvisao()" {% if player_provisions <= 0 %}disabled{% endif %}>Usar</button>
            </div>
        </li>
        <li><b>HABILIDADE 1:</b> <span>{{ player_habilidade_1 }}</span></li>
        <li><b>HABILIDADE 2:</b> <span>{{ player_habilidade_2 }}</span></li>
    </ul>
    <div class="action-buttons-container" style="text-align: center; margin-top: 10px; display: flex; justify-content: center; align-items: center;">
        <button id="rest-btn" class="action-button rest-button" onclick="descansoRapido()" {% if player_provisions <= 0 %}disabled{% endif %}>Descansar</button>
        <button id="save-btn" class="action-button save-button" onclick="salvarProgresso()">Salvar</button>
        <span id="save-status"></span>
    </div>

     <!-- alças de resize -->
    <div class="resizer nw"></div>
    <div class="resizer ne"></div>
    <div class="resizer sw"></div>
    <div class="resizer se"></div>
    <div class="resizer n"></div>
    <div class="resizer s"></div>
    <div class="resizer e"></div>
    <div class="resizer w"></div>


</div>

<script>
    // --- ELEMENTOS E VARIÁVEIS GLOBAIS ---
    const sheet = document.getElementById('character-sheet');
    const header = document.getElementById('character-sheet-header');
    let isDragging = false, offsetX, offsetY, dragTimeout, isClick = true;

    // --- LÓGICA DE ARRASTAR E MINIMIZAR ---
    header.addEventListener('mousedown', (e) => { 
        isDragging = true; 
        isClick = true; 
        offsetX = e.clientX - sheet.offsetLeft; 
        offsetY = e.clientY - sheet.offsetTop; 
        dragTimeout = setTimeout(() => { isClick = false; }, 150); 
        e.preventDefault(); 
    });
    document.addEventListener('mousemove', (e) => { 
        if (!isDragging || isClick) return; 
        sheet.style.left = e.clientX - offsetX + 'px'; 
        sheet.style.top = e.clientY - offsetY + 'px'; 
    });
    document.addEventListener('mouseup', () => { 
        if (isDragging && isClick) { 
            sheet.classList.toggle('minimizado'); 
        } 
        isDragging = false; 
        clearTimeout(dragTimeout); 
    });

    // --- FUNÇÕES DE ATUALIZAÇÃO DAS BARRAS ---
    // Função para a barra de ENERGIA
    function atualizarBarraEnergia(valor, max_valor) {
        const barra = document.getElementById('barra-energia');
        if (!barra || !max_valor || max_valor === 0) return;
        const porcentagem = Math.max(0, valor) * 100 / max_valor;
        barra.style.width = porcentagem + "%";
        if (porcentagem > 60) {
            barra.style.backgroundColor = "#28a745"; // Verde
        } else if (porcentagem > 30) {
            barra.style.backgroundColor = "#ffc107"; // Amarelo
        } else {
            barra.style.backgroundColor = "#dc3545"; // Vermelho
        }
    }

    // Função para a barra de XP
    function atualizarBarraXp(valor, max_valor) {
        const barra = document.getElementById('barra-xp');
        if (!barra || !max_valor || max_valor === 0) return;
        const porcentagem = Math.max(0, valor) * 100 / max_valor;
        barra.style.width = porcentagem + "%";
        barra.style.backgroundColor = "#007bff"; // Azul
    }

    // --- FUNÇÕES DOS BOTÕES DE AÇÃO ---
    async function usarProvisao() {
        const response = await fetch('/usar-provisao', { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await response.json();
        if (data.success) {
            document.getElementById('sheet-energia').textContent = data.player_energia;
            document.getElementById('sheet-provisions').textContent = data.player_provisions;
            atualizarBarraEnergia(data.player_energia, {{ player_max_energia }});
            if (data.player_provisions <= 0) {
                document.getElementById('provision-btn').disabled = true;
            }
        } else {
            alert(data.message);
        }
    }

    async function salvarProgresso() {
        const saveStatus = document.getElementById('save-status');
        saveStatus.textContent = 'Salvando...';
        const response = await fetch('/salvar-progresso', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
            body: JSON.stringify({ pagina_atual: window.location.pathname })
        });
        const data = await response.json();
        if(data.success) {
            saveStatus.style.color = 'green';
            saveStatus.textContent = 'Salvo!';
        } else {
            saveStatus.style.color = 'red';
            saveStatus.textContent = 'Erro!';
        }
        setTimeout(() => { saveStatus.textContent = ''; }, 3000);
    }

    async function descansoRapido() {
        const restButton = document.getElementById('rest-btn');
        const saveStatus = document.getElementById('save-status');
        restButton.disabled = true;
        saveStatus.textContent = 'Descansando...';
        const response = await fetch('/descanso-rapido', { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await response.json();
        if (data.success) {
            document.getElementById('sheet-energia').textContent = data.player_energia;
            document.getElementById('sheet-sorte').textContent = data.player_sorte;
            document.getElementById('sheet-provisions').textContent = data.player_provisions;
            atualizarBarraEnergia(data.player_energia, {{ player_max_energia }});
            saveStatus.style.color = 'blue';
            saveStatus.textContent = 'Você descansou!';
            if (data.player_provisions <= 0) {
                document.getElementById('provision-btn').disabled = true;
                restButton.disabled = true;
            } else {
                restButton.disabled = false;
            }
        } else {
            alert(data.message);
            restButton.disabled = false;
        }
        setTimeout(() => { saveStatus.textContent = ''; }, 4000);
    }

    // --- LÓGICA DE REDIMENSIONAMENTO (CORRIGIDA) ---
    const resizers = sheet.querySelectorAll('.resizer');
    let isResizing = false;
    let currentResizer;
    let initialMouseX, initialMouseY;
    let initialWidth, initialHeight, initialTop, initialLeft;
    const minWidth = 180;
    const minHeight = 150;
    resizers.forEach(resizer => {
        resizer.addEventListener('mousedown', e => {
            isResizing = true;
            currentResizer = resizer;
            initialMouseX = e.clientX;
            initialMouseY = e.clientY;
            const rect = sheet.getBoundingClientRect();
            initialWidth = rect.width;
            initialHeight = rect.height;
            initialTop = rect.top;
            initialLeft = rect.left;
            e.preventDefault();
            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
        });
    });
    function resize(e) {
        if (!isResizing) return;
        const dx = e.clientX - initialMouseX;
        const dy = e.clientY - initialMouseY;
        if (currentResizer.classList.contains('se')) {
            const newWidth = initialWidth + dx;
            const newHeight = initialHeight + dy;
            if (newWidth > minWidth) sheet.style.width = newWidth + 'px';
            if (newHeight > minHeight) sheet.style.height = newHeight + 'px';
        } else if (currentResizer.classList.contains('sw')) {
            const newWidth = initialWidth - dx;
            const newHeight = initialHeight + dy;
            if (newWidth > minWidth) {
                sheet.style.width = newWidth + 'px';
                sheet.style.left = initialLeft + dx + 'px';
            }
            if (newHeight > minHeight) sheet.style.height = newHeight + 'px';
        } else if (currentResizer.classList.contains('ne')) {
            const newWidth = initialWidth + dx;
            const newHeight = initialHeight - dy;
            if (newWidth > minWidth) sheet.style.width = newWidth + 'px';
            if (newHeight > minHeight) {
                sheet.style.height = newHeight + 'px';
                sheet.style.top = initialTop + dy + 'px';
            }
        } else if (currentResizer.classList.contains('nw')) {
            const newWidth = initialWidth - dx;
            const newHeight = initialHeight - dy;
            if (newWidth > minWidth) {
                sheet.style.width = newWidth + 'px';
                sheet.style.left = initialLeft + dx + 'px';
            }
            if (newHeight > minHeight) {
                sheet.style.height = newHeight + 'px';
                sheet.style.top = initialTop + dy + 'px';
            }
        } else if (currentResizer.classList.contains('e')) {
            const newWidth = initialWidth + dx;
            if (newWidth > minWidth) sheet.style.width = newWidth + 'px';
        } else if (currentResizer.classList.contains('w')) {
            const newWidth = initialWidth - dx;
            if (newWidth > minWidth) {
                sheet.style.width = newWidth + 'px';
                sheet.style.left = initialLeft + dx + 'px';
            }
        } else if (currentResizer.classList.contains('n')) {
            const newHeight = initialHeight - dy;
            if (newHeight > minHeight) {
                sheet.style.height = newHeight + 'px';
                sheet.style.top = initialTop + dy + 'px';
            }
        } else if (currentResizer.classList.contains('s')) {
            const newHeight = initialHeight + dy;
            if (newHeight > minHeight) sheet.style.height = newHeight + 'px';
        }
    }
    function stopResize() {
        isResizing = false;
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResize);
    }

    // --- INICIALIZAÇÃO DAS BARRAS ---
    document.addEventListener('DOMContentLoaded', () => {
        atualizarBarraEnergia({{ player_energia }}, {{ player_max_energia }});
        atualizarBarraXp({{ player_xp }}, 100);
    });
    
</script>
{% endif %}
"""
# (Adicione esta nova rota ao seu arquivo main.py)

@app.route("/descanso-rapido", methods=["POST"])
def descanso_rapido():
    # Verifica se o jogador tem provisões para descansar
    if session.get("player_provisions", 0) > 0:
        
        # Deduz o custo de 1 provisão
        session["player_provisions"] -= 1
        
        # Calcula a cura de energia (2d6)
        cura_energia = random.randint(1, 6) + random.randint(1, 6)
        
        # Recupera a energia, sem ultrapassar o máximo
        energia_atual = session.get("player_energia", 0)
        max_energia = session.get("player_max_energia", 1)
        session["player_energia"] = min(max_energia, energia_atual + cura_energia)
        
        # Recupera 1 ponto de sorte
        session["player_sorte"] = session.get("player_sorte", 0) + 1
        
        session.modified = True
        
        # Retorna uma resposta de sucesso com os dados atualizados
        return jsonify({
            "success": True,
            "message": f"Você descansou e recuperou {cura_energia} de Energia e 1 de Sorte.",
            "player_energia": session["player_energia"],
            "player_sorte": session["player_sorte"],
            "player_provisions": session["player_provisions"]
        })
    else:
        # Retorna uma resposta de falha se não houver provisões
        return jsonify({
            "success": False,
            "message": "Você não tem provisões para descansar!"
        })

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
        # --- NOVO: Pega o XP e a hab3 da sessão ---
        xp = session.get("player_xp", 0)
        hab3 = session.get("player_habilidade_3", "Nenhuma")

        # --- NOVO: Atualiza a sessão com a página atual ANTES de salvar ---
        session['player_pagina_atual'] = pagina_atual
        
         # --- ALTERADO: Passa os novos dados para a função de salvar ---
        atualizar_personagem(player_id, energia, sorte, provisoes, pagina_atual, xp, hab3)
        
        return jsonify({"success": True, "message": "Progresso salvo!"})

    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return jsonify({"success": False, "message": "Ocorreu um erro ao salvar."})

@app.route("/")
def home():
    html_home = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="UTF-8">
    <style>
    body    {margin:0;padding:0;height:100vh;background-image:url('/static/imagens/background.png');background-size:cover;background-position:center;background-repeat:no-repeat;font-family:Arial,sans-serif;color:white;text-align:center}
    div {background-color: rgba(0, 0, 0, 0.5);
    display=flex;}
    ul {list-style: none;}
    h1  {margin-top:72px;text-shadow:2px 2px 4px black;font-size:48px}
    h1:hover { font-size: 52px;
    transform: scale(1.05);
        transition: transform 0.3s ease
    }
    a   {color:yellow;font-weight:bold;text-decoration:none;font-size:36px}p{font-size:24px}
    a:hover { font-size: 40px;
    transform: scale(1.05);
        transition: transform 0.3s ease
    }
    </style>
    </head>
    <body>
    <div>
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
    </div>    
    </body>
    </html>
    """
    return render_template_string(html_home)

@app.route("/personagens")
def personagens():
    lista = listar_personagens()
    
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Personagens Salvos</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                color: #333;
                margin: 0;
                padding: 20px;
                display: flex;
                justify-content: center;
            }
            .container {
                width: 100%;
                max-width: 650px;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }
            ul {
                list-style: none;
                padding: 0;
            }
            li {
                background: #fff;
                margin-bottom: 12px;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            li:hover {
                transform: translateY(-4px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
            }
            .char-info {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .list-avatar {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                border: 2px solid #eee;
                object-fit: cover;
            }
            .char-actions {
                display: flex;
                gap: 10px;
            }
            
            .btn {
                text-decoration: none;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                transition: background-color 0.2s ease, transform 0.2s ease;
                font-size: 0.9em;
                border: none;
                cursor: pointer;
            }
            .btn:hover {
                transform: scale(1.05);
            }
            .nomes {font-size: 20px;}
            .btn-carregar { background-color: #3498db; }
            .btn-carregar:hover { background-color: #2980b9; }
            
            .btn-excluir { background-color: #e74c3c; }
            .btn-excluir:hover { background-color: #c0392b; }

            .voltar {
                display: block;
                width: fit-content;
                margin: 30px auto 0 auto;
                background-color: #7f8c8d;
            }
            .voltar:hover {
                background-color: #6c7a7b;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📜 Personagens Salvos</h1>
            <ul>
    """

    if not lista:
        html += "<p style='text-align: center;'>Nenhum personagem foi criado ainda.</p>"
    
    # Este loop agora corresponde EXATAMENTE aos dados da função listar_personagens
    for p in lista:
        # p[0]=id, p[1]=nome, p[2]=raca, p[3]=classe, p[4]=avatar
        html += f"""
                <li>
                    <div class="char-info">
                        <img src="/static/avatares/{p[4]}" alt="Avatar" class="list-avatar">
                        <span class="nomes"><b>{p[1]}</b> ({p[2]} {p[3]})</span>
                    </div>
                    <div class="char-actions">
                        <a href="/carregar/{p[0]}" class="btn btn-carregar">Carregar</a>
                        <a href="/excluir/{p[0]}" class="btn btn-excluir" onclick="return confirm('Tem certeza que deseja excluir {p[1]}? Esta ação não pode ser desfeita.');">Excluir</a>
                    </div>
                </li>
        """

    html += """
            </ul>
            <a href="/" class="btn voltar">Voltar ao início</a>
        </div>
    </body>
    </html>
    """
    return html

# (Substitua toda a sua função @app.route("/carregar/<int:pid>") por esta)
# (Substitua toda a sua função @app.route("/carregar/<int:pid>") por esta)

@app.route("/carregar/<int:pid>")
def carregar(pid):
    p = carregar_personagem_por_id(pid)
    if p:
        # Carrega os dados do personagem na sessão (lógica inalterada)
        session["player_id"] = p[0]
        session["player_nome"] = p[1]
        session["player_habilidade"] = p[4]
        session["player_energia"] = p[5]
        session["player_max_energia"] = p[6]
        session["player_sorte"] = p[7]
        session["player_provisions"] = p[8]
        session["player_avatar"] = p[9]
        session["player_pagina_atual"] = p[10]
            # --- NOVO: Carrega as habilidades do personagem na sessão ---
        session["player_habilidade_1"] = p[11]
        session["player_habilidade_2"] = p[12]
         # --- NOVO: Carrega o XP e a habilidade 3 na sessão ---
        session["player_xp"] = p[13]
        session["player_habilidade_3"] = p[14]
        
        # --- HTML ATUALIZADO com a imagem do avatar ---
        html_sucesso = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Personagem Carregado</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    background-image: url('/static/imagens/background.png');
                    background-size: cover;
                    background-position: center;
                    font-family: Arial, sans-serif;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }}
                .container {{
                    background-color: rgba(0, 0, 0, 0.7);
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                /* --- NOVO: Estilo para o avatar --- */
                .loaded-avatar {{
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    border: 4px solid #ffd700;
                    margin-bottom: 20px;
                    object-fit: cover;
                }}
                h2 {{
                    font-size: 2.5em;
                    margin-top: 0;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px black;
                }}
                p {{
                    font-size: 1.2em;
                    margin-bottom: 30px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 15px 30px;
                    background-color: #ffd700;
                    color: #333;
                    font-size: 1.2em;
                    font-weight: bold;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: transform 0.2s ease, background-color 0.2s ease;
                    margin: 0 10px;
                }}
                .btn:hover {{
                    transform: scale(1.05);
                    background-color: #ffec8b;
                }}
                .btn-secondary {{
                    background-color: transparent;
                    color: #fff;
                    border: 2px solid #fff;
                }}
                .btn-secondary:hover {{
                    background-color: #fff;
                    color: #333;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="/static/avatares/{p[9]}" alt="Avatar" class="loaded-avatar">
                
                <h2>✅ Personagem Carregado!</h2>
                <p>Prepare-se para continuar sua jornada, <b>{p[1]}</b>.</p>
                <a href='{p[10]}' class="btn">Continuar Aventura</a>
                <a href='/' class="btn btn-secondary">Menu Principal</a>
            </div>
        </body>
        </html>
        """
        
        return html_sucesso
    else:
        # A página de erro continua a mesma, pois não há avatar para mostrar
        html_erro = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>Erro ao Carregar</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    background-image: url('/static/imagens/background.png');
                    background-size: cover;
                    background-position: center;
                    font-family: Arial, sans-serif;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }
                .container {
                    background-color: rgba(0, 0, 0, 0.7);
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                h2 {
                    font-size: 2.5em;
                    margin-top: 0;
                    text-shadow: 2px 2px 4px black;
                    color: #e74c3c;
                }
                .btn {
                    display: inline-block;
                    padding: 15px 30px;
                    background-color: #ffd700;
                    color: #333;
                    font-size: 1.2em;
                    font-weight: bold;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: transform 0.2s ease, background-color 0.2s ease;
                }
                .btn:hover {
                    transform: scale(1.05);
                    background-color: #ffec8b;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>❌ Personagem não encontrado</h2>
                <a href='/' class="btn">Voltar ao Menu</a>
            </div>
        </body>
        </html>
        """
        return html_erro

@app.route("/excluir/<int:pid>")
def excluir(pid):
    excluir_personagem_por_id(pid)
    # Redireciona o usuário de volta para a lista de personagens atualizada
    return redirect("/personagens")
# (Substitua toda a sua função @app.route("/criar") por esta)

@app.route("/criar", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        session.clear()

    if request.method == "POST":
        nome = request.form.get("nome")
        raca = request.form.get("raca")
        classe = request.form.get("classe")
        habilidades_escolhidas = request.form.getlist("habilidades")
        
        hab1 = habilidades_escolhidas[0] if len(habilidades_escolhidas) > 0 else "Nenhuma"
        hab2 = habilidades_escolhidas[1] if len(habilidades_escolhidas) > 1 else "Nenhuma"

        mods = MODIFICADORES[raca][classe]
        habilidade = mods['HABILIDADE'] + random.randint(1,6)
        energia = mods['ENERGIA'] + random.randint(1,6) + random.randint(1,6)
        sorte = mods['SORTE'] + random.randint(1,6)
        avatar_filename = f"{raca.lower()}_{classe.lower()}.png"
        
        novo_id = salvar_personagem(nome, raca, classe, habilidade, energia, energia, sorte, 10, avatar_filename, hab1, hab2)
        
        session["player_id"] = novo_id
        session["player_habilidade"] = habilidade
        session["player_energia"] = energia
        session["player_max_energia"] = energia
        session["player_sorte"] = sorte
        session["player_nome"] = nome
        session["player_provisions"] = 10
        session["player_avatar"] = avatar_filename
        session["player_pagina_atual"] = "/aventura"
        session["player_habilidade_1"] = hab1
        session["player_habilidade_2"] = hab2
        # --- NOVO: Define os valores iniciais na sessão ---
        session["player_xp"] = 0
        session["player_habilidade_3"] = "Nenhuma"

        # --- FICHA FINAL COM FONTE MAIOR ---
        ficha_html = f"""
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<style>
    body {{
        background-image: url('/static/imagens/background.png');
        background-size: cover;
        background-position: center;
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
    }}
    .ficha {{
        background-color: rgba(0,0,0,0.7);
        display: inline-block;
        padding: 30px;
        border-radius: 15px;
        max-width: 600px;
    }}
    .final-avatar {{
        width: 120px; height: 120px; border-radius: 50%;
        border: 3px solid #ffd700; margin-bottom: 15px;
    }}
    a {{
        color: #ffd700; text-decoration: none; margin: 10px;
        font-size: 24px; display: inline-block;
    }}
    a:hover {{ transform: scale(1.05); }}
    h2 {{
        text-shadow: 2px 2px 4px black; font-size: 36px; margin-bottom: 20px;
    }}
    .info-principal p {{
        font-size: 30px; /* <-- ALTERADO DE 26px PARA 30px */
        margin: 10px 0;
    }}
    .info-principal b {{
        color: #ffd700;
    }}
    .habilidades {{
        margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1);
        border-radius: 10px; font-size: 20px; font-style: italic;
    }}
    .atributos ul {{
        list-style-type: none; padding: 0; margin: 0; font-size: 22px;
    }}
    .atributos li {{
        margin: 6px 0;
    }}
</style></head>
<body>
    <div class="ficha">
        <img src="/static/avatares/{avatar_filename}" alt="Avatar" class="final-avatar">
        <h2>✅ Personagem criado!</h2>

        <div class="info-principal">
            <p><b>Nome:</b> {nome}</p>
            <p><b>Raça:</b> {raca}</p>
            <p><b>Classe:</b> {classe}</p>
        </div>

        <div class="habilidades">
            <h3>Habilidades</h3>
            <p>{hab1}</p>
            <p>{hab2}</p>
        </div>

        <div class="atributos">
            <h3>Atributos</h3>
            <ul>
                <li><b>HABILIDADE:</b> {habilidade}</li>
                <li><b>ENERGIA:</b> {energia}</li>
                <li><b>SORTE:</b> {sorte}</li>
            </ul>
        </div>

        <a href="/">➕ Criar outro personagem</a>
        <a href="/aventura">🚀 Iniciar aventura</a>
    </div>
</body></html>
"""
        return ficha_html

    # --- FORMULÁRIO COM NOVO DESIGN DAS HABILIDADES ---
    html_form = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body { background-image: url('/static/imagens/background.png'); background-size: cover; background-position: center; color: white; font-family: Arial, sans-serif; text-align: center; }
            h1 { text-shadow: 2px 2px 4px black; }
            form { background-color: rgba(0, 0, 0, 0.7); display: inline-block; padding: 25px; border-radius: 10px; max-width: 500px; }
            #avatar-preview { width: 200px; height: 200px; border-radius: 50%; border: 4px solid #fff; margin-bottom: 15px; object-fit: cover; }
            label, .habilidades-label { display: block; margin-top: 15px; font-size: 18px; }
            select, input[type="text"] { font-size: 18px; padding: 8px; margin-top: 5px; width: 95%; border-radius: 5px; border: 1px solid #ccc; }
            button { font-size: 20px; padding: 12px 24px; cursor: pointer; margin-top: 20px; }
            
            /* --- NOVOS ESTILOS PARA HABILIDADES --- */
            .habilidades-label { margin-bottom: 10px; font-size: 20px; }
            .habilidades-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 10px; /* Espaçamento entre os cards */
                margin-top: 10px;
            }
            .habilidade-opcao {
                border: 2px solid #666;
                border-radius: 8px;
                padding: 12px;
                background-color: rgba(255,255,255,0.05);
                cursor: pointer;
                transition: all 0.2s ease-in-out;
            }
            .habilidade-opcao:hover {
                border-color: #ffd700;
                background-color: rgba(255,255,255,0.15);
            }
            .habilidade-opcao input[type="checkbox"] {
                display: none; /* Esconde o checkbox padrão */
            }
            .habilidade-opcao label {
                margin: 0; /* Reseta a margem da label interna */
                pointer-events: none; /* Faz o clique atravessar a label e ir para o div */
            }
            /* Estilo para quando a habilidade está SELECIONADA */
            .habilidade-opcao.selecionada {
                background-color: rgba(255, 215, 0, 0.2);
                border-color: #ffd700;
                color: #fff;
            }

        </style>
    </head>
    <body>
        <h1>Criação de Personagem</h1>
        <form method="POST">
            <img id="avatar-preview" src="/static/avatares/humano_guerreiro.png" alt="Prévia">
            <label>Nome: <input type="text" name="nome" required></label>
            <label>Raça:
                <select id="raca-select" name="raca" required>
                    {% for r in racas %}<option value="{{r}}">{{r}}</option>{% endfor %}
                </select>
            </label>
            <label>Classe:
                <select id="classe-select" name="classe" required>
                    {% for c in classes %}<option value="{{c}}">{{c}}</option>{% endfor %}
                </select>
            </label>
            
            <p class="habilidades-label"><b>Escolha 2 Habilidades:</b></p>
            <div class="habilidades-container">
                {% for nome, dados in habilidades_data.items() %}
                <div class="habilidade-opcao" data-classes="{{ dados.classes|join(',') }}" onclick="toggleCheckbox(this)">
                    <input type="checkbox" name="habilidades" value="{{ nome }}" id="{{ nome }}">
                    <label for="{{ nome }}">{{ nome }} (+{{ dados.bonus }})</label>
                </div>
                {% endfor %}
            </div>

            <button type="submit">🚀 Criar personagem</button>
        </form>

        <script>
            const racaSelect = document.getElementById('raca-select');
            const classeSelect = document.getElementById('classe-select');
            const avatarPreview = document.getElementById('avatar-preview');
            const checkboxes = document.querySelectorAll('.habilidade-opcao input[type=checkbox]');
            const habilidadeOpcoes = document.querySelectorAll('.habilidade-opcao');
            
            // --- NOVA FUNÇÃO PARA CLICAR NO 'CARD' ---
            function toggleCheckbox(divElement) {
                const checkbox = divElement.querySelector('input[type="checkbox"]');
                // Inverte o estado do checkbox se ele não estiver desabilitado
                if (!checkbox.disabled) {
                    checkbox.checked = !checkbox.checked;
                    // Dispara o evento 'change' manualmente para rodar a lógica de validação
                    checkbox.dispatchEvent(new Event('change'));
                }
            }

            function atualizarAvatar() {
                const raca = racaSelect.value.toLowerCase();
                const classe = classeSelect.value.toLowerCase();
                avatarPreview.src = `/static/avatares/${raca}_${classe}.png`;
            }
            
            function atualizarHabilidades() {
                const classeSelecionada = classeSelect.value;
                habilidadeOpcoes.forEach(opcao => {
                    const classesPermitidas = opcao.getAttribute('data-classes');
                    if (classesPermitidas.includes(classeSelecionada)) {
                        opcao.style.display = 'block';
                    } else {
                        opcao.style.display = 'none';
                        const checkbox = opcao.querySelector('input');
                        checkbox.checked = false;
                        // Dispara o evento para atualizar o visual
                        checkbox.dispatchEvent(new Event('change'));
                    }
                });
            }

            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    const selecionados = document.querySelectorAll('.habilidade-opcao input[type=checkbox]:checked');
                    
                    // --- LÓGICA ATUALIZADA ---
                    // Atualiza o visual (adiciona ou remove a classe 'selecionada')
                    const parentDiv = checkbox.closest('.habilidade-opcao');
                    parentDiv.classList.toggle('selecionada', checkbox.checked);

                    // Valida o limite de 2 habilidades
                    if (selecionados.length > 2) {
                        alert('Você só pode escolher 2 habilidades!');
                        checkbox.checked = false;
                        parentDiv.classList.remove('selecionada'); // Garante que o visual seja revertido
                    }

                    // Desabilita as outras opções quando 2 são selecionadas
                    const outrasOpcoes = document.querySelectorAll('.habilidade-opcao input[type=checkbox]:not(:checked)');
                    outrasOpcoes.forEach(op => {
                        op.disabled = (selecionados.length >= 2);
                    });
                });
            });

            racaSelect.addEventListener('change', atualizarAvatar);
            classeSelect.addEventListener('change', () => {
                atualizarAvatar();
                atualizarHabilidades();
            });
            
            // Inicialização
            atualizarAvatar();
            atualizarHabilidades();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_form, racas=RACAS, classes=CLASSES, habilidades_data=HABILIDADES_DATA)

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
        body {
            color: black;
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
        }
        h1 {
            text-shadow: 2px 2px 4px black;
            text-align: center;
        }
        img { display: block; margin: 0 auto; }
        a {
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
        img:hover {
            transform: scale(1.05);
            transition: transform 0.3s ease;
        }    
        button {
            font-size: 32px;
            padding: 10px 20px;
            cursor: pointer;
        }    
         .dado {
            display: inline-block;
            font-size: 40px;
            width: 60px;
            height: 60px;
            line-height: 60px;
            text-align: center;
            border: 2px solid black;
            border-radius: 10px;
            background: white;
            margin: 10px;
            transition: transform 0.3s;
        }
        .dado.rolando { animation: girar 0.6s infinite; }
        @keyframes girar {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(90deg); }
            50% { transform: rotate(180deg); }
            75% { transform: rotate(270deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
    </head>
    <body>
        <img src="/static/imagens/pag12.png" alt="Caverna Leste" style="width:450px;"><br>
        <h1>Teste de Habilidade: Derrubar a Porta</h1>
        <p>Ao tentar derrubar a porta com o ombro, você deve jogar <b>1 dado (d20)</b>.</p>

        <button type="button" onclick="testarHabilidade()">🎲 Testar Habilidade</button>

        <div id="dado" class="dado">?</div>
        <p id="mensagem"></p>
        <div id="imagem"></div>
        <div id="acao"></div>

        <br><a href="/">Voltar ao início</a>
        <br><br>

        <script>
        async function testarHabilidade() {
            const dadoDiv = document.getElementById("dado");
            const mensagemP = document.getElementById("mensagem");
            const imagemDiv = document.getElementById("imagem");
            const acaoDiv = document.getElementById("acao");

            // animação do dado rolando
            dadoDiv.classList.add("rolando");
            let interval = setInterval(() => {
                dadoDiv.textContent = Math.floor(Math.random() * 20) + 1;
            }, 100);

            // chamada AJAX
            let response = await fetch("/teste-habilidade-ajax", {method:"POST"});
            let data = await response.json();

            // parar a animação e mostrar resultado final
            setTimeout(() => {
                clearInterval(interval);
                dadoDiv.classList.remove("rolando");
                dadoDiv.textContent = data.resultado;

                mensagemP.textContent = data.mensagem;
                imagemDiv.innerHTML = data.imagem;
                acaoDiv.innerHTML = data.link;
            }, 1000);
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/teste-habilidade-ajax", methods=["POST"])
def teste_habilidade_ajax():
    resultado = random.randint(1, 20)  # rola d20
    if resultado > 10:
        mensagem = f"✅ Você rolou {resultado} e consegue arrombar a porta!"
        link = '<a href="/porta-arrombada">Continuar pela porta</a>'
        imagem = "<img src='/static/imagens/pag11.png' alt='Porta Arrombada' style='width:450px;'>"
    else:
        mensagem = f"💀 Você rolou {resultado}. A porta não cede. Você esfrega o ombro dolorido e retorna à encruzilhada."
        link = '<a href="/sair">Retornar à encruzilhada</a>'
        imagem = "<img src='/static/imagens/pag10.png' alt='Porta Não Cedeu' style='width:450px;'>"

    return jsonify({
        "resultado": resultado,
        "sucesso": resultado > 10,
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

@app.route("/oste", methods=["GET"])
def oste():
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
            text-align: center;
        }
        img { display: block; margin: 0 auto; }
        img:hover { 
            transform: scale(1.05);
            transition: transform 0.3s ease; 
        }
        a {
            padding: 10px 15px;
            background-color: #333;
            color: white;
            font-size: 28px;
            border-radius: 5px;
            text-align: center;
            text-decoration: none;
            margin: 10px;
            display: inline-block;
        }
        a:hover {
            background-color:#ffffff;
            color: black;
            transform: scale(1.05);
            transition: transform 0.3s ease;
        }
        button { 
            font-size: 28px; 
            padding: 10px 20px; 
            cursor: pointer;
        }
         .dado {
            display: inline-block;
            font-size: 40px;
            width: 60px;
            height: 60px;
            line-height: 60px;
            text-align: center;
            border: 2px solid black;
            border-radius: 10px;
            background: white;
            margin: 10px;
            transition: transform 0.3s;
        }
        .dado.rolando { animation: girar 0.6s infinite; }
        @keyframes girar {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(90deg); }
            50% { transform: rotate(180deg); }
            75% { transform: rotate(270deg); }
            100% { transform: rotate(360deg); }
        }
    </style>    
</head>
<body>
    <img src="/static/imagens/pag15.png" alt="Caverna Oeste" style="width:450px;"><br>
    <h1>Você virou para o oeste</h1>
    <p>Ao virar para o oeste, a passagem faz uma curva para o norte. Você se aproxima de um posto de sentinela e vê uma criatura parecida com um Goblin dormindo.
    Você deve então tentar passar na ponta dos pés, o que exige um <b>Teste de Sorte</b>.</p>
    
    <button type="button" onclick="testarSorte()">🎲 Testar Sorte</button>

    <div id="dado" class="dado">?</div>
    <p id="mensagem"></p>
    <p id="extra"></p>
    <div id="acao"></div>

    <a href="/sair">Dar meia volta e retornar à encruzilhada</a><br><br>
    <a href="/">Voltar ao início</a>

    <script>
    async function testarSorte() {
        const dadoDiv = document.getElementById("dado");
        const msg = document.getElementById("mensagem");
        const extra = document.getElementById("extra");
        const acaoDiv = document.getElementById("acao");

        // animação do dado rolando
        dadoDiv.classList.add("rolando");
        let interval = setInterval(() => {
            dadoDiv.textContent = Math.floor(Math.random() * 20) + 1;
        }, 100);

        // chamada AJAX
        let response = await fetch("/oste-sorte", {method:"POST"});
        let data = await response.json();

        // parar animação e mostrar resultado
        setTimeout(() => {
            clearInterval(interval);
            dadoDiv.classList.remove("rolando");
            dadoDiv.textContent = data.resultado;

            msg.textContent = data.mensagem;
            extra.textContent = data.extra_texto;
            acaoDiv.innerHTML = data.link;
        }, 1000);
    }
    </script>
</body>
</html>
    """
    return render_template_string(html)


@app.route("/oste-sorte", methods=["POST"])
def oste_sorte():
    resultado = random.randint(1, 20)
    if resultado > 10:
        mensagem = "✅ Você teve sorte! A criatura não acorda e você continua."
        extra_texto = "Você continua pela passagem e, à sua esquerda, vê uma abertura misteriosa iluminada por uma luz fraca."
        link = '<a href="/norte">Explorar a abertura à esquerda</a>'
    else:
        mensagem = "💀 Você não teve sorte! Você pisa em terreno mole, faz barulho e a criatura acorda instantaneamente."
        extra_texto = ""
        link = '<a href="/combate">Entrar em combate</a>'

    return jsonify({
        "resultado": resultado,
        "mensagem": mensagem,
        "extra_texto": extra_texto,
        "link": link
    })


@app.route("/combate", methods=["GET", "POST"])
def combate():
    fim = None

    # --- CORREÇÃO: Mova esta linha para cá, fora do bloco IF/ELSE ---
    # Isso garante que player_max_energia sempre tenha um valor para o template,
    # seja na primeira visita (GET) ou em um ataque (POST).
    player_max_energia = session.get("player_max_energia", 15)

    # Limpa a sessão e inicializa o combate na primeira vez
    if request.method == "GET":
        session["orc_energia"] = 10
        session["orc_habilidade"] = 4
        session["player_energia"] = player_max_energia
        
        # Assumindo que o jogador já tem esses valores da criação do personagem
        session["player_habilidade"] = session.get("player_habilidade", 5)
        session["player_habilidade_1"] = session.get("player_habilidade_1", "Ataque Rápido")
        session["player_habilidade_2"] = session.get("player_habilidade_2", "Corte Poderoso")
        session["player_nome"] = session.get("player_nome", "Herói")
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Lógica de combate (processa a rodada de ataque)
    if request.method == "POST":
        habilidade_usada = request.form.get("habilidade", "Ataque Normal")
        bonus_ataque = HABILIDADES_DATA.get(habilidade_usada, {}).get("bonus", 0)
        
        # Rolagem do Orc
        orc_dado1 = random.randint(1, 6)
        orc_dado2 = random.randint(1, 6)
        orc_roll_total = orc_dado1 + orc_dado2 + session["orc_habilidade"]

        # Rolagem do Jogador
        player_dado1 = random.randint(1, 6)
        player_dado2 = random.randint(1, 6)
        player_roll_total = player_dado1 + player_dado2 + session["player_habilidade"] + bonus_ataque

        if player_roll_total > orc_roll_total:
            session["orc_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}) e venceu a rodada!"
        elif orc_roll_total > player_roll_total:
            session["player_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}), mas o Orc venceu a rodada."
        else:
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}). Empate!"

        # Garante que a energia não fique negativa
        session["orc_energia"] = max(0, session["orc_energia"])
        session["player_energia"] = max(0, session["player_energia"])
        session.modified = True

        # Verifica se o combate terminou
        if session["orc_energia"] <= 0:
            session["player_xp"] = session.get("player_xp", 0) + 50
            fim = """
                <h2><img src='/static/imagens/continueaventura.png' alt='Vitória' style='width:450px;'><br>
                ✅ Você derrotou o Orc!</h2>
                <a href="/norte" class="btn">Continuar pela passagem</a>
            """
        elif session["player_energia"] <= 0:
            fim = """
                <h2><img src='/static/imagens/fimaventura.png' alt='Derrota' style='width:450px;'><br>
                💀 Você foi derrotado...</h2>
                <a href="/reset-combate" class="btn">Tentar Novamente</a>
            """

        return jsonify({
            "orc_dados": [orc_dado1, orc_dado2],
            "player_dados": [player_dado1, player_dado2],
            "player_total": player_roll_total,
            "orc_total": orc_roll_total,
            "player_energia": session["player_energia"],
            "orc_energia": session["orc_energia"],
            "player_xp": session.get("player_xp", 0),   # 🔥 novo
            "mensagem": mensagem,
            "fim": fim,
            "explicacao_player": (
                f"Habilidade Total de Ataque ⚔️: {player_roll_total} "
                f"({player_dado1} + {player_dado2} + {session['player_habilidade']} + {bonus_ataque})"
            ),
            "explicacao_orc": (
                f"Habilidade Total de Ataque ⚔️: {orc_roll_total} "
                f"({orc_dado1} + {orc_dado2} + {session['orc_habilidade']})"
            )
        })

    # Prepara as variáveis para o template HTML inicial
    hab1_nome = session.get('player_habilidade_1', 'Nenhuma')
    hab2_nome = session.get('player_habilidade_2', 'Nenhuma')
    hab1_bonus = HABILIDADES_DATA.get(hab1_nome, {}).get('bonus', 0)
    hab2_bonus = HABILIDADES_DATA.get(hab2_nome, {}).get('bonus', 0)
    
    html_template = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Combate com Orc</title>
        <style>
            #combate-container { text-align: center; max-width: 600px; margin: auto; }
            #status { display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 1.1em; }
            .barra-container { width: 200px; height: 25px; background: #ddd; border-radius: 5px; margin: 5px auto; }
            .barra { height: 100%; border-radius: 5px; transition: width 0.3s, background 0.3s; }
            #form-combate { background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; display: inline-block; }
            button { font-size: 24px; padding: 10px 20px; cursor: pointer; }
            #nomedado {font-size: 24px; font-weight: bolder; }
            .btn { text-decoration: none; color: white !important; font-weight: bold; padding: 8px 15px; border-radius: 5px; background-color: #3498db; margin-top: 5px; display: inline-block; }
            .dado {
                display: inline-block;
                font-size: 40px;
                width: 60px;
                height: 60px;
                line-height: 60px;
                text-align: center;
                border: 2px solid black;
                border-radius: 10px;
                background: white;
                margin: 10px;
                transition: transform 0.3s;
            }
            .dado.rolando {
                animation: girar 0.6s infinite;
            }
            @keyframes girar {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(90deg); }
                50% { transform: rotate(180deg); }
                75% { transform: rotate(270deg); }
                100% { transform: rotate(360deg); }
            }
             a {
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
        </style>
    </head>
    <body>
    <div id="combate-container">
        <h1>Combate Iniciado!</h1>
        <p>A criatura que acorda é um ORC. Ele se levanta rapidamente e tenta soar um alarme. Você precisa atacá-lo imediatamente!</p>
        <img src="/static/imagens/pag16.png" alt="Caverna Oeste" style="width:450px;"><br>

        <div id="status">
            <div>
                <h2><b>Orc</b></h2>
                <div class="barra-container">
                    <div id="barra-orc" class="barra" style="width:{{ orc_energia * 100 / 10 }}%; background:green;"></div>
                </div>
                <p>Energia: <span id="orc-energia">{{orc_energia}}</span></p>
                <p>Habilidade: {{orc_habilidade}}</p>
            </div>
            <div>
                <h2><b>{{ player_nome }}</b></h2>
                <div class="barra-container">
                    <div id="barra-jogador" class="barra" style="width:{{ player_energia * 100 / player_max_energia }}%; background:green;"></div>
                </div>
                <p>Energia: <span id="player-energia">{{player_energia}}</span></p>
                <p>Habilidade: {{player_habilidade}}</p>
            </div>
        </div>

        <form id="form-combate">
            <h3>Escolha sua Ação:</h3>
            <input type="radio" id="ataque-normal" name="habilidade" value="Ataque Normal" checked>
            <label for="ataque-normal">Ataque Normal (+0)</label><br>
            
            <input type="radio" id="hab1" name="habilidade" value="{{ hab1_nome }}">
            <label for="hab1">{{ hab1_nome }} (+{{ hab1_bonus }})</label><br>

            <input type="radio" id="hab2" name="habilidade" value="{{ hab2_nome }}">
            <label for="hab2">{{ hab2_nome }} (+{{ hab2_bonus }})</label><br>
        </form>
        <br>
        <p id="mensagem" style="font-weight: bold;">{mensagem}</p>
        <h3>Rolagens:</h3>
        <div>
            <span id="nomedado">Orc: </span>
                <div id="dado-orc1" class="dado">?</div>
                <div id="dado-orc2" class="dado">?</div>
                <p id="explicacao-orc"></p>

                <span id="nomedado">{{ player_nome }}:</span>
                <div id="dado-player1" class="dado">?</div>
                <div id="dado-player2" class="dado">?</div>
                <p id="explicacao-player"></p>
        </div>
        <br><br>

        <div id="acoes">
            {% if not fim %}
                <button type="button" onclick="atacar()">⚔️ Atacar!</button>
            {% else %}
                {{ fim | safe }}
            {% endif %}
        </div>
        <br><br>
        <div id="xp-container"></div>

        <br><br>
        <a href="/">Voltar ao início</a>
        <br><br>
    </div>

    <script>
        function atualizarBarra(id, valor, max_valor) {
            const barra = document.getElementById(id);
            if (!barra || !max_valor || max_valor === 0) return;
            const porcentagem = Math.max(0, valor) * 100 / max_valor;
            barra.style.width = porcentagem + "%";
            if (porcentagem > 60) barra.style.background = "green";
            else if (porcentagem > 30) barra.style.background = "orange";
            else barra.style.background = "red";
        }

        async function atacar() {
            const formCombate = document.getElementById('form-combate');
            const dadosForm = new FormData(formCombate);

            let dadoPlayer1 = document.getElementById("dado-player1");
            let dadoPlayer2 = document.getElementById("dado-player2");
            let dadoOrc1 = document.getElementById("dado-orc1");
            let dadoOrc2 = document.getElementById("dado-orc2");

            // Ativar animação
            [dadoPlayer1, dadoPlayer2, dadoOrc1, dadoOrc2].forEach(d => d.classList.add("rolando"));

            let response = await fetch("/combate", {
                method: "POST",
                body: dadosForm,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            
            let data = await response.json();

            // Simular rolagem visual por 1s
            let tempo = 1000; 
            let interval = setInterval(() => {
                dadoPlayer1.textContent = Math.floor(Math.random() * 6) + 1;
                dadoPlayer2.textContent = Math.floor(Math.random() * 6) + 1;
                dadoOrc1.textContent = Math.floor(Math.random() * 6) + 1;
                dadoOrc2.textContent = Math.floor(Math.random() * 6) + 1;
            }, 100);

            setTimeout(() => {
                clearInterval(interval);

                // Mostrar valores finais do servidor
                dadoPlayer1.textContent = data.player_dados[0];
                dadoPlayer2.textContent = data.player_dados[1];
                dadoOrc1.textContent = data.orc_dados[0];
                dadoOrc2.textContent = data.orc_dados[1];

                // Parar animação
                [dadoPlayer1, dadoPlayer2, dadoOrc1, dadoOrc2].forEach(d => d.classList.remove("rolando"));

                // Atualizar energias e mensagem
                document.getElementById("player-energia").textContent = data.player_energia;
                document.getElementById("orc-energia").textContent = data.orc_energia;
                document.getElementById("mensagem").textContent = data.mensagem;

                // Mostrar explicação das rolagens
                document.getElementById("explicacao-player").textContent = data.explicacao_player;
                document.getElementById("explicacao-orc").textContent = data.explicacao_orc;
                // 🔥 Atualizar XP se vier do servidor
                if (data.fim && data.player_xp !== undefined) {
                    document.getElementById("xp-container").innerHTML =
                        `<p>XP: <span id="player-xp">${data.player_xp}</span></p>`;
                }


                // Atualizar as barras de vida
                atualizarBarra("barra-jogador", data.player_energia, {{ player_max_energia }});
                atualizarBarra("barra-orc", data.orc_energia, 10);

                if (data.fim) {
                    document.getElementById("acoes").innerHTML = data.fim;
                }
            }, tempo);
        }
    </script>
    </body>
    </html>
    """
    
    return render_template_string(
    html_template,
    mensagem=mensagem,
    player_nome=session.get("player_nome", "Herói"),
    player_energia=session.get("player_energia", 15),
    player_max_energia=player_max_energia or 15,
    orc_energia=session.get("orc_energia", 10),
    orc_habilidade=session.get("orc_habilidade", 4),
    hab1_nome=hab1_nome,
    hab1_bonus=hab1_bonus,
    hab2_nome=hab2_nome,
    hab2_bonus=hab2_bonus,
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
    if request.method == "POST":
        resultado = random.randint(1, 20)
        if resultado > 10:
            mensagem = "✅ Você teve sorte! Os dardos não te acertaram e você consegue puxar a argola sem problemas."
            extra_texto = "Você sai do aposento e retorna à passagem."
        else:
            mensagem = "💀 Você não teve sorte! Dois dardos envenenados o atingem. Você perde 2 pontos de ENERGIA!"
            extra_texto = ""
            if "player_energia" in session:
                session["player_energia"] = max(session["player_energia"] - 2, 0)

        return jsonify({
            "resultado": resultado,
            "mensagem": mensagem,
            "extra_texto": extra_texto,
            "sucesso": resultado > 10
        })

    # GET → carrega a página
    html = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>Puxar Argola</title>
    <style>
        body { text-align:center; font-family: Arial, sans-serif; }
        .dado {
            display: inline-block;
            font-size: 40px;
            width: 60px;
            height: 60px;
            line-height: 60px;
            text-align: center;
            border: 2px solid black;
            border-radius: 10px;
            background: white;
            margin: 10px;
            transition: transform 0.3s;
        }
        .dado.rolando { animation: girar 0.6s infinite; }
        @keyframes girar {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(90deg); }
            50% { transform: rotate(180deg); }
            75% { transform: rotate(270deg); }
            100% { transform: rotate(360deg); }
        }
        button { font-size: 28px; padding: 10px 20px; cursor:pointer; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        a { font-size: 24px; text-decoration:none; margin-top:15px; display:inline-block; background:#333; color:white; padding:10px 15px; border-radius:5px; }
        a:hover { background:white; color:black; transform:scale(1.05); transition:0.3s; }
    </style>
    </head>
    <body>
        <img src="/static/imagens/pag6.png" style="width:450px;"><br>
        <h1>Você tenta puxar a argola</h1>
        <p>Enquanto você luta para puxar a argola do teto, ouve dois pequenos estalos e depois silvos, quando dois dardos minúsculos são disparados na sua direção. <b>Teste sua sorte!</b></p>
        
        <button id="btn-sorte" onclick="testarSorte()">🎲 Testar Sorte</button>
        <div id="dado-sorte" class="dado">?</div>
        <p id="mensagem"></p>
        <p id="extra"></p>

        <br><br>
        <a href="/">Voltar ao início</a>

        <script>
            async function testarSorte() {
                const dado = document.getElementById("dado-sorte");
                const msg = document.getElementById("mensagem");
                const extra = document.getElementById("extra");


                // animação
                dado.classList.add("rolando");
                let interval = setInterval(() => {
                    dado.textContent = Math.floor(Math.random() * 20) + 1;
                }, 100);

                let response = await fetch("/puxar-argola", {method:"POST"});
                let data = await response.json();

                setTimeout(() => {
                    clearInterval(interval);
                    dado.classList.remove("rolando");


                    dado.textContent = data.resultado;
                    msg.textContent = data.mensagem;
                    extra.textContent = data.extra_texto;

                    if (data.sucesso) {
                        extra.innerHTML += "<br><a href='/encruzilhada'>Retornar ao túnel</a>";
                    } else {
                        extra.innerHTML += "<br><a href='/encruzilhada'>Retornar ao túnel</a>";
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


    

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

@app.route("/norte2", methods=["GET", "POST"])
def norte2():
    session['player_pagina_atual'] = '/norte2'
    fim = None
    
    # Inicializa o combate na primeira vez que a rota é acessada
    if "barbaro_energia" not in session or request.method == "GET":
        session["barbaro_energia"] = 6
        session["barbaro_habilidade"] = 7
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Processa a rodada de ataque (quando o JS envia um POST)
    if request.method == "POST":
        habilidade_usada = request.form.get("habilidade", "Ataque Normal")
        bonus_ataque = HABILIDADES_DATA.get(habilidade_usada, {}).get("bonus", 0)

        barbaro_roll = random.randint(1, 6) + random.randint(1, 6) + session["barbaro_habilidade"]
        player_roll = random.randint(1, 6) + random.randint(1, 6) + session["player_habilidade"] + bonus_ataque

        if player_roll > barbaro_roll:
            session["barbaro_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}) e venceu a rodada!"
        elif barbaro_roll > player_roll:
            session["player_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}), mas o Bárbaro venceu a rodada."
        else:
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}). Empate!"

        # Garante que a energia não fique negativa
        session["barbaro_energia"] = max(0, session["barbaro_energia"])
        session["player_energia"] = max(0, session["player_energia"])
        session.modified = True

        # Verifica se o combate terminou
        if session["barbaro_energia"] <= 0:
            fim = """
                <h2><img src='/static/imagens/continueaventura.png' alt='Vitória' style='width:450px;'><br>
                ✅ Você derrotou o Bárbaro!</h2>
                <a href="/norte" class="btn">Continuar pela passagem</a>
            """
        elif session["player_energia"] <= 0:
            fim = """
                <h2><img src='/static/imagens/fimaventura.png' alt='Derrota' style='width:450px;'><br>
                💀 Você foi derrotado...</h2>
                <a href="/reset-combate" class="btn">Tentar Novamente</a>
            """

        return jsonify({
            "barbaro_roll": barbaro_roll, "player_roll": player_roll,
            "player_energia": session["player_energia"], "barbaro_energia": session["barbaro_energia"],
            "mensagem": mensagem, "fim": fim
        })

    # Prepara as variáveis para o template
    hab1_nome = session.get('player_habilidade_1', 'Nenhuma')
    hab2_nome = session.get('player_habilidade_2', 'Nenhuma')
    hab1_bonus = HABILIDADES_DATA.get(hab1_nome, {}).get('bonus', 0)
    hab2_bonus = HABILIDADES_DATA.get(hab2_nome, {}).get('bonus', 0)
    
    # Template HTML puro, sem f-string, para evitar erros
    html_template = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Combate com Bárbaro</title>
        <style>
            /* Seu CSS aqui... (sem alterações) */
            #combate-container { text-align: center; max-width: 600px; margin: auto; }
            #status { display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 1.1em; }
            .barra-container { width: 200px; height: 25px; background: #ddd; border-radius: 5px; margin: 5px auto; }
            .barra { height: 100%; border-radius: 5px; transition: width 0.3s, background 0.3s; }
            #form-combate { background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; display: inline-block; }
            button { font-size: 24px; padding: 10px 20px; cursor: pointer; }
            #nomedado {font-size: 24px;
            font-weight: bolder;
            }
            .btn { text-decoration: none; color: white !important; font-weight: bold; padding: 8px 15px; border-radius: 5px; background-color: #3498db; margin-top: 5px; display: inline-block; }
            .dado {
                display: inline-block;
                font-size: 40px;
                width: 60px;
                height: 60px;
                line-height: 60px;
                text-align: center;
                border: 2px solid black;
                border-radius: 10px;
                background: white;
                margin: 10px;
                transition: transform 0.3s;
            }
            .dado.rolando {
                animation: girar 0.6s infinite;
            }
            @keyframes girar {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(90deg); }
                50% { transform: rotate(180deg); }
                75% { transform: rotate(270deg); }
                100% { transform: rotate(360deg); }
            }
        </style>

    </head>
    <body>
    <div id="combate-container">
        <img src="/static/imagens/pag5.png" alt="Caverna Norte" style="width:450px;"><br>
        <h1>Continuar na direção norte</h1>
        <p>A passagem termina em uma porta sólida. Você não ouve nada ao escutar, então tenta a maçaneta, que gira, e você entra no aposento.</p>
        <br>
        <p>Assim que você olha em volta, ouve um grito de guerra atrás de você e, ao se virar, vê um homem selvagem pulando em sua direção com uma grande arma</p>

        <h1>Combate Iniciado!</h1>
        <img src="/static/imagens/pag4.png" alt="Caverna Norte" style="width:450px;"><br>

        <div id="status">
            <div>
                <h2><b>Bárbaro</b></h2>
                <div class="barra-container">
                    <div id="barra-barbaro" class="barra" style="width:{ session.get("barbaro_energia", 0) * 100 / barbaro_max_energia }%; background:green;"></div>
                </div>
                <p>Energia: <span id="barbaro-energia">{{barbaro_energia}}</span></p>
            </div>
            <div>
                <h2><b>{{ player_nome }}</b></h2>
                <div class="barra-container">
                    <div id="barra-jogador" class="barra" style="width:{ session.get("player_energia", 0) * 100 / player_max_energia }%; background:green;"></div>
                </div>
                <p>Energia: <span id="player-energia">{{player_energia}}</span></p>
            </div>
        </div>

        <form id="form-combate">
            <h3>Escolha sua Ação:</h3>
            <input type="radio" id="ataque-normal" name="habilidade" value="Ataque Normal" checked>
            <label for="ataque-normal">Ataque Normal (+0)</label><br>
            
            <input type="radio" id="hab1" name="habilidade" value="{{ hab1_nome }}">
            <label for="hab1">{{ hab1_nome }} (+{{ hab1_bonus }})</label><br>

            <input type="radio" id="hab2" name="habilidade" value="{{ hab2_nome }}">
            <label for="hab2">{{ hab2_nome }} (+{{ hab2_bonus }})</label><br>

        </form>
        <br>
        <p id="mensagem" style="font-weight: bold;">{mensagem}</p>
        <h3>Rolagens:</h3>
        <div>
            <span id="nomedado">Bárbaro: </span><div id="dado-barbaro" class="dado">?</div>
            <span id="nomedado">{{ player_nome }}:</span><div id="dado-player" class="dado">?</div>
        </div>

        <div id="acoes">
            {% if not fim %}
                <button type="button" onclick="atacar()">⚔️ Atacar!</button>
            {% else %}
                {{ fim | safe }}
            {% endif %}
        </div>
    </div>

    <script>
        function atualizarBarra(id, valor, max_valor) {
            const barra = document.getElementById(id);
            if (!barra || !max_valor || max_valor === 0) return;
            const porcentagem = Math.max(0, valor) * 100 / max_valor;
            barra.style.width = porcentagem + "%";
            if (porcentagem > 60) barra.style.background = "green";
            else if (porcentagem > 30) barra.style.background = "orange";
            else barra.style.background = "red";
        }

        async function atacar() {
            const formCombate = document.getElementById('form-combate');
            const dadosForm = new FormData(formCombate);

            let dadoPlayer = document.getElementById("dado-player");
            let dadoBarbaro = document.getElementById("dado-barbaro");

            // 🔹 Ativar animação
            dadoPlayer.classList.add("rolando");
            dadoBarbaro.classList.add("rolando");

            let response = await fetch("/norte2", {
                method: "POST",
                body: dadosForm,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            
            let data = await response.json();

            // 🔹 Simular rolagem visual por 1s
            let tempo = 1000; 
            let interval = setInterval(() => {
                dadoPlayer.textContent = Math.floor(Math.random() * 6) + 1;
                dadoBarbaro.textContent = Math.floor(Math.random() * 6) + 1;
            }, 100);

            setTimeout(() => {
                clearInterval(interval);

                // Mostrar valores finais do servidor
                dadoPlayer.textContent = data.player_roll;
                dadoBarbaro.textContent = data.barbaro_roll;

                // Parar animação
                dadoPlayer.classList.remove("rolando");
                dadoBarbaro.classList.remove("rolando");

                // Atualizar energias e mensagem
                document.getElementById("player-energia").textContent = data.player_energia;
                document.getElementById("barbaro-energia").textContent = data.barbaro_energia;
                document.getElementById("mensagem").textContent = data.mensagem;

                atualizarBarra("barra-jogador", data.player_energia, {{ player_max_energia }});
                atualizarBarra("barra-barbaro", data.barbaro_energia, {{ barbaro_max_energia }});

                if (data.fim) {
                    document.getElementById("acoes").innerHTML = data.fim;
                }
            }, tempo);
        }
    </script>
</body>

    </html>
    """
    
    return render_template_string(
        html_template,
        mensagem=mensagem,
        player_nome=session.get("player_nome"),
        player_energia=session.get("player_energia"),
        player_max_energia=session.get("player_max_energia", 1),
        barbaro_energia=session.get("barbaro_energia"),
        barbaro_max_energia=6,
        hab1_nome=hab1_nome,
        hab1_bonus=hab1_bonus,
        hab2_nome=hab2_nome,
        hab2_bonus=hab2_bonus,
        fim=fim
    )
@app.route("/reset3")
def reset3():
    session.pop("barbaro_energia", None)
    session.pop("barbaro_habilidade", None)
    session.pop("player_energia", None)
    session.pop("player_habilidade", None)
    return redirect("/norte2")

@app.route("/leste3")
def leste3():
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
    <img src="/static/imagens/pag3.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Indo para o Leste</h1>
    <p>A passagem termina em uma espessa porta de madeira. A partir daqui, você tem uma nova escolha:<br>
    <br>

    <a href="/porta2">Tentar abrir a porta</a>
    <a href="/leste2">Voltar para o cruzamento e tentar outro caminho</a>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)

@app.route("/porta2")
def porta2():
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
    <img src="/static/imagens/pag2.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Abriu a porta</h1>
    <p>A porta se abre e você entra em um pequeno compartimento. As paredes são cobertas por elaborados trabalhos em pedra, com mosaicos e baixo-relevos em mármore. Em um canto do aposento, há uma grande estátua de metal de uma criatura de um olho só, e nesse olho há uma joia cintilante.</p><br>
    <p>Não parece haver outra saída, então você terá que retornar à encruzilhada. No entanto, a joia é muito tentadora, e você tem uma nova escolha:</p>
    <br>

    <a href="/oeste2">Deixar a joia e retornar à encruzilhada</a>
    <a href="/pegar-joia2">Tentar levar a joia com você</a>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    <br>
    <br>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)


@app.route("/pegar-joia2")
def pegarjoia2():
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
    <img src="/static/imagens/pag1.png" alt="Caverna Norte" style="width:450px;"><br>
    <h1>Tentou pegar a joia</h1>
    <p>Você se aproxima da estátua e, após se assustar com uma ratazana, tenta puxar a joia, mas ela está solidamente presa. Você então tenta usar sua espada para retirá-la, mas ao fazer isso, ouve rangidos e, para seu horror, a estátua começa a se mexer.</p><br>
    

    <a href="/oeste2">Deixar a joia e retornar à encruzilhada</a>
    <a href="/pegar-joia3">Tentar levar a joia com você</a>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    <br>
    <br>
    </body>
    </html>
    """
       # Esta função processa os {{ }} e os substitui pelos valores corretos
    return render_template_string(html)


@app.route("/pegar-joia3", methods=["GET", "POST"])
def pegarjoia():
    session['player_pagina_atual'] = '/pegar-joia3'
    fim = None
    
    # Inicializa o combate na primeira vez que a rota é acessada
    if "ciclope_energia" not in session or request.method == "GET":
        session["ciclope_energia"] = 10
        session["ciclope_habilidade"] = 7
        mensagem = "O combate começou! Prepare-se!"
    else:
        mensagem = ""

    # Processa a rodada de ataque (quando o JS envia um POST)
    if request.method == "POST":
        habilidade_usada = request.form.get("habilidade", "Ataque Normal")
        bonus_ataque = HABILIDADES_DATA.get(habilidade_usada, {}).get("bonus", 0)

        ciclope_dado1 = random.randint(1, 6) 
        ciclope_dado2 = random.randint(1, 6)
        ciclope_roll_total = ciclope_dado1 + ciclope_dado2 + session["ciclope_habilidade"]

        player_dado1 = random.randint(1, 6) 
        player_dado2 = random.randint(1, 6)
        player_roll_total = player_dado1 + player_dado2 + session["player_habilidade"] + bonus_ataque

        if player_roll_total > ciclope_roll_total:
            session["ciclope_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}) e venceu a rodada!"
        elif ciclope_roll_total > player_roll_total:
            session["player_energia"] -= 2
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}), mas o Ciclope venceu a rodada."
        else:
            mensagem = f"Você usou {habilidade_usada} (+{bonus_ataque}). Empate!"

        # Garante que a energia não fique negativa
        session["ciclope_energia"] = max(0, session["ciclope_energia"])
        session["player_energia"] = max(0, session["player_energia"])
        session.modified = True

        # Verifica se o combate terminou
        if session["ciclope_energia"] <= 0:
             # --- ADICIONE ESTA LINHA ---
            # Recompensa o jogador com 75 XP pela vitória
            session["player_xp"] = session.get("player_xp", 0) + 75
            fim = """
                <h2><img src='/static/imagens/continueaventura.png' alt='Vitória' style='width:450px;'><br>
                ✅ Você derrotou o Ciclope!</h2>
                <a href="/norte" class="btn">Continuar pela passagem</a>
            """
        elif session["player_energia"] <= 0:
            fim = """
                <h2><img src='/static/imagens/fimaventura.png' alt='Derrota' style='width:450px;'><br>
                💀 Você foi derrotado...</h2>
                <a href="/reset-combate" class="btn">Tentar Novamente</a>
            """

        return jsonify({
    "ciclope_dados": [ciclope_dado1, ciclope_dado2],
    "player_dados": [player_dado1, player_dado2],
    "player_total": player_roll_total,
    "ciclope_total": ciclope_roll_total,
    "player_energia": session["player_energia"], 
    "ciclope_energia": session["ciclope_energia"],
    "mensagem": mensagem, 
    "fim": fim,
   "explicacao_player": (
    f"Habilidade Total de Ataque ⚔️: {player_roll_total} "
    f"({player_dado1} + {player_dado2} + {session['player_habilidade']} + {bonus_ataque})"
),
"explicacao_ciclope": (
    f"Habilidade Total de Ataque ⚔️: {ciclope_roll_total} "
    f"({ciclope_dado1} + {ciclope_dado2} + {session['ciclope_habilidade']})"
)

})

    # Prepara as variáveis para o template
    hab1_nome = session.get('player_habilidade_1', 'Nenhuma')
    hab2_nome = session.get('player_habilidade_2', 'Nenhuma')
    hab1_bonus = HABILIDADES_DATA.get(hab1_nome, {}).get('bonus', 0)
    hab2_bonus = HABILIDADES_DATA.get(hab2_nome, {}).get('bonus', 0)
    
    # Template HTML puro, sem f-string, para evitar erros
    html_template = STATUS_HTML + """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Combate com Ciclope</title>
        <style>
            /* Seu CSS aqui... (sem alterações) */
            #combate-container { text-align: center; max-width: 600px; margin: auto; }
            #status { display: flex; gap: 50px; justify-content: center; margin-bottom: 20px; font-size: 1.1em; }
            .barra-container { width: 200px; height: 25px; background: #ddd; border-radius: 5px; margin: 5px auto; }
            .barra { height: 100%; border-radius: 5px; transition: width 0.3s, background 0.3s; }
            #form-combate { background-color: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; display: inline-block; }
            button { font-size: 24px; padding: 10px 20px; cursor: pointer; }
            #nomedado {font-size: 24px;
            font-weight: bolder;
            }
            .btn { text-decoration: none; color: white !important; font-weight: bold; padding: 8px 15px; border-radius: 5px; background-color: #3498db; margin-top: 5px; display: inline-block; }
            .dado {
                display: inline-block;
                font-size: 40px;
                width: 60px;
                height: 60px;
                line-height: 60px;
                text-align: center;
                border: 2px solid black;
                border-radius: 10px;
                background: white;
                margin: 10px;
                transition: transform 0.3s;
            }
            .dado.rolando {
                animation: girar 0.6s infinite;
            }
            @keyframes girar {
                0% { transform: rotate(0deg); }
                25% { transform: rotate(90deg); }
                50% { transform: rotate(180deg); }
                75% { transform: rotate(270deg); }
                100% { transform: rotate(360deg); }
            }
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
        </style>

    </head>
    <body>
    <div id="combate-container">

        <h1>Combate Iniciado!</h1>
        <img src="/static/imagens/pag0.png" alt="Caverna Norte" style="width:450px;"><br>

        <div id="status">
            <div>
                <h2><b>Ciclope</b></h2>
                <div class="barra-container">
                    <div id="barra-ciclope" class="barra" style="width:{{ session.get("ciclope_energia", 0) * 100 / ciclope_max_energia }}%; background:green;"></div>
                </div>
                <p>Energia: <span id="ciclope-energia">{{ciclope_energia}}</span></p>
            </div>
            <div>
                <h2><b>{{ player_nome }}</b></h2>
                <div class="barra-container">
                    <div id="barra-jogador" class="barra" style="width:{{ session.get("player_energia", 0) * 100 / player_max_energia }}%; background:green;"></div>
                </div>
                <p>Energia: <span id="player-energia">{{player_energia}}</span></p>
            </div>
        </div>

        <form id="form-combate">
            <h3>Escolha sua Ação:</h3>
            <input type="radio" id="ataque-normal" name="habilidade" value="Ataque Normal" checked>
            <label for="ataque-normal">Ataque Normal (+0)</label><br>
            
            <input type="radio" id="hab1" name="habilidade" value="{{ hab1_nome }}">
            <label for="hab1">{{ hab1_nome }} (+{{ hab1_bonus }})</label><br>

            <input type="radio" id="hab2" name="habilidade" value="{{ hab2_nome }}">
            <label for="hab2">{{ hab2_nome }} (+{{ hab2_bonus }})</label><br>

        </form>
        <br>
        <p id="mensagem" style="font-weight: bold;">{mensagem}</p>
        <h3>Rolagens:</h3>
        <div>
            <span id="nomedado">Ciclope: </span>
                <div id="dado-ciclope1" class="dado">?</div>
                <div id="dado-ciclope2" class="dado">?</div>
                <p id="explicacao-ciclope"></p>

                <span id="nomedado">{{ player_nome }}:</span>
                <div id="dado-player1" class="dado">?</div>
                <div id="dado-player2" class="dado">?</div>
                <p id="explicacao-player"></p>
        </div>
        <br>
    <br>

        <div id="acoes">
            {% if not fim %}
                <button type="button" onclick="atacar()">⚔️ Atacar!</button>
            {% else %}
                {{ fim | safe }}
            {% endif %}
        </div>
        <br>
    <br>
    <a href="/oeste2">Deixar a joia e retornar à encruzilhada</a>
    <br>
    <br>
    <br>
    <a href="/">Voltar ao início</a>
    <br>
    <br>
    </div>

    <script>
        function atualizarBarra(id, valor, max_valor) {
            const barra = document.getElementById(id);
            if (!barra || !max_valor || max_valor === 0) return;
            const porcentagem = Math.max(0, valor) * 100 / max_valor;
            barra.style.width = porcentagem + "%";
            if (porcentagem > 60) barra.style.background = "green";
            else if (porcentagem > 30) barra.style.background = "orange";
            else barra.style.background = "red";
        }

        async function atacar() {
            const formCombate = document.getElementById('form-combate');
            const dadosForm = new FormData(formCombate);

            let dadoPlayer1 = document.getElementById("dado-player1");
            let dadoPlayer2 = document.getElementById("dado-player2");
            let dadoCiclope1 = document.getElementById("dado-ciclope1");
            let dadoCiclope2 = document.getElementById("dado-ciclope2");

            // Ativar animação
            [dadoPlayer1, dadoPlayer2, dadoCiclope1, dadoCiclope2].forEach(d => d.classList.add("rolando"));

            let response = await fetch("/pegar-joia3", {
                method: "POST",
                body: dadosForm,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            
            let data = await response.json();

            // 🔹 Simular rolagem visual por 1s
            let tempo = 1000; 
            let interval = setInterval(() => {
                dadoPlayer1.textContent = Math.floor(Math.random() * 6) + 1;
                dadoPlayer2.textContent = Math.floor(Math.random() * 6) + 1;
                dadoCiclope1.textContent = Math.floor(Math.random() * 6) + 1;
                dadoCiclope2.textContent = Math.floor(Math.random() * 6) + 1;
            }, 100);

            setTimeout(() => {
                clearInterval(interval);

                // Mostrar valores finais do servidor
                dadoPlayer1.textContent = data.player_dados[0];
                dadoPlayer2.textContent = data.player_dados[1];
                dadoCiclope1.textContent = data.ciclope_dados[0];
                dadoCiclope2.textContent = data.ciclope_dados[1];

                // Parar animação
                [dadoPlayer1, dadoPlayer2, dadoCiclope1, dadoCiclope2].forEach(d => d.classList.remove("rolando"));

                // Atualizar energias e mensagem
                document.getElementById("player-energia").textContent = data.player_energia;
                document.getElementById("ciclope-energia").textContent = data.ciclope_energia;
                document.getElementById("mensagem").textContent = data.mensagem;

                    // Mostrar explicação das rolagens
                document.getElementById("explicacao-player").textContent = data.explicacao_player;
                document.getElementById("explicacao-ciclope").textContent = data.explicacao_ciclope;

                atualizarBarra("barra-jogador", data.player_energia, {{ player_max_energia }});
                atualizarBarra("barra-ciclope", data.ciclope_energia, {{ ciclope_max_energia }});

                if (data.fim) {
                    document.getElementById("acoes").innerHTML = data.fim;
                }
            }, tempo);
        }
    </script>
</body>

    </html>
    """
    
    return render_template_string(
        html_template,
        mensagem=mensagem,
        player_nome=session.get("player_nome"),
        player_energia=session.get("player_energia"),
        player_max_energia=session.get("player_max_energia", 1),
        ciclope_energia=session.get("ciclope_energia"),
        ciclope_max_energia=10,
        hab1_nome=hab1_nome,
        hab1_bonus=hab1_bonus,
        hab2_nome=hab2_nome,
        hab2_bonus=hab2_bonus,
        fim=fim
    )

if __name__ == "__main__":
    app.run(debug=True)