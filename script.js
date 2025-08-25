
  // 🎲 Dicionário de modificadores de Raça + Classe
  const MODIFICADORES = {
    "Humano": {
      "Guerreiro": { HABILIDADE: 2, ENERGIA: 1, SORTE: 0 },
      "Mago":      { HABILIDADE: 0, ENERGIA: 0, SORTE: 1 },
      "Arqueiro":  { HABILIDADE: 2, ENERGIA: 0, SORTE: 1 },
      "Ladino":    { HABILIDADE: 2, ENERGIA: 0, SORTE: 1 }
    },
    "Elfo": {
      "Guerreiro": { HABILIDADE: 4, ENERGIA: 0, SORTE: 1 },
      "Mago":      { HABILIDADE: 2, ENERGIA: -1, SORTE: 3 },
      "Arqueiro":  { HABILIDADE: 4, ENERGIA: -1, SORTE: 3 },
      "Ladino":    { HABILIDADE: 4, ENERGIA: -1, SORTE: 2 }
    },
    "Anão": {
      "Guerreiro": { HABILIDADE: 3, ENERGIA: 3, SORTE: -1 },
      "Mago":      { HABILIDADE: 1, ENERGIA: 2, SORTE: 0 },
      "Arqueiro":  { HABILIDADE: 3, ENERGIA: 2, SORTE: 0 },
      "Ladino":    { HABILIDADE: 3, ENERGIA: 2, SORTE: 0 }
    },
    "Meio-Orc": {
      "Guerreiro": { HABILIDADE: 4, ENERGIA: 2, SORTE: -1 },
      "Mago":      { HABILIDADE: 2, ENERGIA: 1, SORTE: 0 },
      "Arqueiro":  { HABILIDADE: 4, ENERGIA: 1, SORTE: 0 },
      "Ladino":    { HABILIDADE: 4, ENERGIA: 1, SORTE: 0 }
    },
    "Halfling": {
      "Guerreiro": { HABILIDADE: 1, ENERGIA: 1, SORTE: 1 },
      "Mago":      { HABILIDADE: -1, ENERGIA: 0, SORTE: 2 },
      "Arqueiro":  { HABILIDADE: 1, ENERGIA: 0, SORTE: 2 },
      "Ladino":    { HABILIDADE: 1, ENERGIA: 0, SORTE: 2 }
    },
    "Gnomo": {
      "Guerreiro": { HABILIDADE: 1, ENERGIA: 1, SORTE: 1 },
      "Mago":      { HABILIDADE: -1, ENERGIA: 0, SORTE: 3 },
      "Arqueiro":  { HABILIDADE: 1, ENERGIA: 0, SORTE: 3 },
      "Ladino":    { HABILIDADE: 1, ENERGIA: 0, SORTE: 2 }
    },
    "Meio-Elfo": {
      "Guerreiro": { HABILIDADE: 2, ENERGIA: 0, SORTE: 3 },
      "Mago":      { HABILIDADE: 0, ENERGIA: -1, SORTE: 5 },
      "Arqueiro":  { HABILIDADE: 2, ENERGIA: -1, SORTE: 5 },
      "Ladino":    { HABILIDADE: 2, ENERGIA: -1, SORTE: 4 }
    }
  };

  // 📜 Objeto do personagem
  let ficha = null;

  // 🎲 Função genérica de rolagem de dado
  function rolarDado(lados = 6) {
    return Math.floor(Math.random() * lados) + 1;
  }

  // 🧙‍♂️ Criação do personagem ao submeter o formulário
  document.getElementById("formPersonagem").addEventListener("submit", function (e) {
    e.preventDefault();

    const nome = document.getElementById("nome").value;
    const raca = document.getElementById("raca").value;
    const classe = document.getElementById("classe").value;

    // Aplica modificadores da raça + classe
    const mods = MODIFICADORES[raca][classe];

    ficha = {
      nome,
      raca,
      classe,
      habilidade: mods.HABILIDADE + rolarDado(6),        // Habilidade base + d6
      energia: mods.ENERGIA + rolarDado(6) + rolarDado(6), // Energia base + 2d6
      sorte: mods.SORTE + rolarDado(6),                  // Sorte base + d6
      energiaMax: 0,
      provisoes: 10, // cada provisão recupera 4 ENERGIA
      avatar: `static/avatares/${raca.toLowerCase()}_${classe.toLowerCase()}.png`
    };

    ficha.energiaMax = ficha.energia;

    mostrarFicha();
  });

  // 📝 Mostra a ficha na tela
  function mostrarFicha() {
    document.getElementById("ficha").innerHTML = `
      <div class="character-sheet">
        <img src="${ficha.avatar}" class="character-avatar">
        <h3>${ficha.nome}</h3>
        <ul>
          <li><b>HABILIDADE:</b> ${ficha.habilidade}</li>
          <li><b>ENERGIA:</b> <span id="energia">${ficha.energia}</span> / ${ficha.energiaMax}</li>
          <li><b>SORTE:</b> ${ficha.sorte}</li>
          <li>
            <b>PROVISÕES:</b> <span id="provisoes">${ficha.provisoes}</span>
            <button class="provision-button" onclick="usarProvisao()" id="btnProvisao">Usar</button>
          </li>
        </ul>
      </div>
    `;
  }

  // 🍗 Função para consumir uma provisão
  function usarProvisao() {
    if (ficha.provisoes > 0) {
      ficha.provisoes--;
      ficha.energia = Math.min(ficha.energia + 4, ficha.energiaMax);

      // Atualiza HUD da ficha
      document.getElementById("energia").textContent = ficha.energia;
      document.getElementById("provisoes").textContent = ficha.provisoes;

      // Desabilita botão se acabou
      if (ficha.provisoes <= 0) {
        document.getElementById("btnProvisao").disabled = true;
      }
    }
  }

