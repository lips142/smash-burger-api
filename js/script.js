/* ============================================
   PAINEL DE PEDIDOS — SMASH BURGUER
   Lógica do painel (KDS)
   ============================================ */

const API_BASE = "http://127.0.0.1:8000";
const LIMITE_MAX_MIN = 60; // prazo máximo de preparo + entrega

let todosOsPedidos = [];
let filtroStatus = "novos";

const els = {
  lista: document.getElementById("lista-pedidos"),
  filtroData: document.getElementById("filtro-data-container"),
  inputData: document.getElementById("input-data"),
  tabs: document.querySelectorAll(".tab-btn"),
};

// Data inicial do filtro = hoje (horário local)
els.inputData.value = new Date().toLocaleDateString("en-CA");

/* ---------- CARREGAMENTO ---------- */

async function carregarPedidos() {
  try {
    const resp = await fetch(`${API_BASE}/pedidos`);
    if (!resp.ok) throw new Error("Falha na resposta da API");
    todosOsPedidos = await resp.json();
    renderPedidos();
  } catch (e) {
    els.lista.innerHTML = `<p class="empty-state">Erro na conexão com o servidor.</p>`;
  }
}

async function carregarItensParaCard(pedidoId) {
  const container = document.getElementById(`itens-${pedidoId}`);
  if (!container) return;
  try {
    const resp = await fetch(`${API_BASE}/pedidos/${pedidoId}/itens`);
    const itens = await resp.json();
    container.innerHTML = itens
      .map((item) => {
        const ingredientes = Array.isArray(item.ingredientes) ? item.ingredientes.join(", ") : "";
        return `
        <div class="item-row">
          <img src="${API_BASE}/static/images/${item.imagem?.split("/").pop() || ""}"
               onerror="this.src='https://via.placeholder.com/42?text=%20';" alt="">
          <span class="item-qty">${item.quantidade}×</span>
          <div class="item-info">
            <span class="item-nome">${item.nome}</span>
            ${ingredientes ? `<span class="item-ingredientes">${ingredientes}</span>` : ""}
          </div>
        </div>`;
      })
      .join("");
  } catch (e) {
    container.innerHTML = `<p class="itens-loading">Erro ao carregar itens</p>`;
  }
}

/* ---------- FILTROS / ABAS ---------- */

function filtrarPedidos(aba, event) {
  filtroStatus = aba;
  els.tabs.forEach((btn) => btn.classList.remove("active"));
  event.target.closest(".tab-btn").classList.add("active");
  els.filtroData.style.display = aba === "finalizado" ? "flex" : "none";
  renderPedidos();
}

function normalizarStatus(status) {
  const s = (status || "").trim().toLowerCase();
  if (s === "em andamento" || s === "novo pedido" || s === "pendente") return "novos";
  if (s === "preparando") return "preparando";
  if (s === "pedido a caminho" || s === "enviado") return "entrega";
  if (s === "finalizado") return "finalizado";
  return "outro";
}

function statusDisplayDe(status) {
  const s = (status || "").trim().toLowerCase();
  if (s === "em andamento" || s === "pendente") return "Novo pedido";
  if (s === "pedido a caminho") return "Enviado";
  if (!status) return "—";
  return status.trim();
}

/* ---------- TEMPO DECORRIDO ---------- */

// Faz o parsing manual da data vinda do backend (formato "YYYY-MM-DDTHH:mm:ss[.ssssss]").
// Evita depender do parser nativo `new Date(string)`, que se confunde quando o Python
// envia microssegundos (6 dígitos) em vez dos milissegundos (3 dígitos) que o padrão
// ISO/JS espera — isso fazia o timer calcular datas completamente erradas.
function parseDataBackend(dataStr) {
  if (!dataStr) return null;
  const match = dataStr.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/);
  if (!match) return null;
  const [year, month, day, hour, minute, second] = match.slice(1).map(Number);
  return new Date(year, month - 1, day, hour, minute, second);
}

function minutosDecorridos(dataISO) {
  const data = parseDataBackend(dataISO);
  if (!data || isNaN(data.getTime())) return null;
  const ms = Date.now() - data.getTime();
  if (isNaN(ms) || ms < 0) return null;
  return Math.floor(ms / 60000);
}

function formatarTempo(min) {
  if (min === null) return "";
  if (min < 1) return "agora";
  if (min < 60) return `${min} min`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}h${m.toString().padStart(2, "0")}`;
}

function formatarHora(date) {
  if (!date || isNaN(date.getTime())) return null;
  return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

/* ---------- RENDER ---------- */

function contarPorAba() {
  const contagem = { novos: 0, preparando: 0, entrega: 0 };
  todosOsPedidos.forEach((p) => {
    const grupo = normalizarStatus(p.status);
    if (grupo in contagem) contagem[grupo]++;
  });
  return contagem;
}

function atualizarContadoresAbas() {
  const c = contarPorAba();
  document.querySelector('[data-tab="novos"] .tab-count').textContent = c.novos;
  document.querySelector('[data-tab="preparando"] .tab-count').textContent = c.preparando;
  document.querySelector('[data-tab="entrega"] .tab-count').textContent = c.entrega;
}

function renderPedidos() {
  atualizarContadoresAbas();

  const dataSelecionada = els.inputData.value;

  if (!todosOsPedidos || todosOsPedidos.length === 0) {
    els.lista.innerHTML = `<p class="empty-state">Nenhum pedido no banco.</p>`;
    return;
  }

  const pedidosFiltrados = todosOsPedidos.filter((p) => {
    const grupo = normalizarStatus(p.status);

    if (filtroStatus === "novos") return grupo === "novos";
    if (filtroStatus === "preparando") return grupo === "preparando";
    if (filtroStatus === "entrega") return grupo === "entrega";

    if (filtroStatus === "finalizado") {
      if (grupo === "finalizado" && p.data) {
        const d = parseDataBackend(p.data);
        if (!d) return false;
        const dataFormatada = d.toLocaleDateString("en-CA");
        return dataFormatada === dataSelecionada;
      }
      return false;
    }
    return false;
  });

  if (pedidosFiltrados.length === 0) {
    els.lista.innerHTML = `<p class="empty-state">Nenhum pedido encontrado.</p>`;
    return;
  }

  els.lista.innerHTML = "";

  for (const p of pedidosFiltrados) {
    const statusDisplay = statusDisplayDe(p.status);
    const classeStatus = statusDisplay.toLowerCase().replace(/\s/g, "");
    const dataPedido = parseDataBackend(p.data);
    const minutos = minutosDecorridos(p.data);
    const atrasado = minutos !== null && minutos >= LIMITE_MAX_MIN && filtroStatus !== "finalizado";

    const horaPedido = formatarHora(dataPedido);
    const horaPrazo = dataPedido
      ? formatarHora(new Date(dataPedido.getTime() + LIMITE_MAX_MIN * 60000))
      : null;

    const card = document.createElement("div");
    card.className = `pedido-card${atrasado ? " urgente" : ""}`;
    card.innerHTML = `
      <div class="ticket-perf"></div>
      <div class="pedido-header">
        <div class="row-top">
          <div>
            <div class="ticket-id"><span>#</span>${p.id}</div>
            <div class="cliente-nome">${p.usuario_nome || "Cliente"}</div>
          </div>
          ${minutos !== null ? `<div class="timer-chip${atrasado ? " alerta" : ""}">${formatarTempo(minutos)}</div>` : ""}
        </div>
        ${
          horaPedido
            ? `<div class="horario-info">
                 <span>Pedido <strong>${horaPedido}</strong></span>
                 <span class="separador">·</span>
                 <span class="${atrasado ? "prazo-estourado" : ""}">Prazo <strong>${horaPrazo}</strong></span>
               </div>`
            : ""
        }
        <div class="status-stamp ${classeStatus}">${statusDisplay}</div>
      </div>

      <div class="itens-lista" id="itens-${p.id}">
        <p class="itens-loading">Carregando itens…</p>
      </div>

      <div class="pedido-footer">
        <div class="total-row">
          <span class="label">Total</span>
          <span class="valor">R$ ${parseFloat(p.total || 0).toFixed(2)}</span>
        </div>
        ${botaoAcao(p.id, statusDisplay)}
      </div>
    `;
    els.lista.appendChild(card);
    carregarItensParaCard(p.id);
  }
}

function botaoAcao(id, statusDisplay) {
  if (statusDisplay === "Novo pedido") {
    return `<button class="btn btn-preparar" onclick="atualizarStatus(${id}, 'Preparando')">Preparar</button>`;
  }
  if (statusDisplay === "Preparando") {
    return `<button class="btn btn-enviar" onclick="atualizarStatus(${id}, 'Pedido a caminho')">Enviar</button>`;
  }
  if (statusDisplay === "Enviado") {
    return `<button class="btn btn-finalizar" onclick="atualizarStatus(${id}, 'Finalizado')">Finalizar</button>`;
  }
  return "";
}

/* ---------- AÇÕES ---------- */

async function atualizarStatus(pedidoId, novoStatus) {
  try {
    const resp = await fetch(
      `${API_BASE}/pedidos/${pedidoId}/status?status=${encodeURIComponent(novoStatus)}`,
      { method: "PUT" }
    );
    if (resp.ok) carregarPedidos();
  } catch (e) {
    alert("Erro ao atualizar status.");
  }
}

/* ---------- INICIALIZAÇÃO ---------- */

els.inputData.addEventListener("change", renderPedidos);

carregarPedidos();
setInterval(carregarPedidos, 10000); // recarrega dados a cada 10s
setInterval(() => {
  if (filtroStatus !== "finalizado") renderPedidos(); // atualiza os timers a cada minuto
}, 60000);