console.log("Dashboard carregado com sucesso!");

// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = localStorage.getItem("token");
let dashboardResumo = null;

const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
const buildApiUrl = window.buildApiUrl || (path => `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`);

const areaExpansivel = document.getElementById("areaExpansivel");

function setCardMessage(cardId, message) {
    const card = document.getElementById(cardId);
    if (!card) return;
    const paragraph = card.querySelector("p");
    if (paragraph) {
        paragraph.textContent = message;
    }
}

function mostrarMensagemArea(chave, mensagem) {
    if (!areaExpansivel) return;
    areaExpansivel.innerHTML = `<p class="mensagem-vazia">${mensagem}</p>`;
    areaExpansivel.dataset.activeSection = chave || "";
    areaExpansivel.classList.add("mostrar");
}

function atualizarCabecalho() {
    const tituloEmpresa = document.getElementById("empresaNome");
    const saudacao = document.getElementById("boasVindas");
    const nomeEmpresa = localStorage.getItem("empresa");
    const nomeUsuario = localStorage.getItem("usuario") || localStorage.getItem("username");

    if (tituloEmpresa && nomeEmpresa) {
        tituloEmpresa.textContent = nomeEmpresa;
    }

    if (saudacao) {
        saudacao.textContent = nomeUsuario ? `Bem-vindo, ${nomeUsuario}` : "Bem-vindo, usuário";
    }
}

function formatCurrency(valor) {
    return `R$ ${Number(valor || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
}

async function carregarResumoDashboard() {
    const token = localStorage.getItem("token");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE}/dashboard/resumo`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) {
            throw new Error(`Status ${response.status}`);
        }
        dashboardResumo = await response.json();
        atualizarCardAlertas(dashboardResumo);
        atualizarCardEntradas(dashboardResumo?.contas_receber_semana);
    } catch (err) {
        console.error("Erro ao carregar resumo do dashboard:", err);
        setCardMessage("cardAlertas", "Nenhum alerta disponível.");
        setCardMessage("cardContasReceber", "Sem entradas previstas.");
    }
}

function atualizarCardEntradas(resumo) {
    const card = document.getElementById("cardContasReceber");
    if (!card) return;
    if (!resumo) {
        card.querySelector("p").textContent = "Sem previsão de entradas na semana.";
        return;
    }
    card.querySelector("p").innerHTML = `Previsto: <strong>${formatCurrency(resumo.total_previsto)}</strong><br>` +
        `Recebido: ${formatCurrency(resumo.total_recebido)}<br>` +
        `Em aberto: ${formatCurrency(resumo.saldo_em_aberto)}`;
}

function atualizarCardAlertas(resumo) {
    const card = document.getElementById("cardAlertas");
    if (!card) return;
    const despesasResumo = resumo?.despesas_fixas?.resumo;
    const parcelasResumo = resumo?.parcelas_semana?.resumo;
    const qtdDespesas = despesasResumo?.quantidade ?? 0;
    const valorDespesas = despesasResumo ? formatCurrency(despesasResumo.valor_previsto) : formatCurrency(0);
    const qtdParcelas = parcelasResumo?.quantidade ?? 0;
    const valorParcelas = parcelasResumo ? formatCurrency(parcelasResumo.valor_total) : formatCurrency(0);
    card.querySelector("p").innerHTML = 
        `Despesas a confirmar: <strong>${qtdDespesas}</strong> (${valorDespesas}).<br>` +
        `Parcelas da semana: <strong>${qtdParcelas}</strong> (${valorParcelas}).`;
}

function renderizarContasReceber(lista) {
    if (!lista || !lista.length) {
        return '<p class="mensagem-vazia">Sem contas a receber nos próximos 7 dias.</p>';
    }
    const linhas = lista.map(item => `
        <tr>
            <td>${item.descricao}</td>
            <td>${item.data_prevista ? new Date(item.data_prevista).toLocaleDateString('pt-BR') : '-'}</td>
            <td>${formatCurrency(item.valor_previsto)}</td>
            <td>${formatCurrency(item.valor_recebido)}</td>
            <td>${item.status || '-'}</td>
        </tr>
    `).join('');
    return `
        <div class="card">
            <h4>Contas a Receber nesta Semana</h4>
            <div class="table-section">
              <table class="tabela-resumo">
                  <thead>
                      <tr>
                          <th>Descrição</th>
                          <th>Vencimento</th>
                          <th>Previsto</th>
                          <th>Recebido</th>
                          <th>Status</th>
                      </tr>
                  </thead>
                  <tbody>${linhas}</tbody>
              </table>
            </div>
        </div>
    `;
}


function renderizarAlertas(resumo) {
    const partes = [];
    partes.push('<div class="card"><h4>Alertas financeiros</h4><p>Confirme os valores das despesas fixas e acompanhe parcelas programadas para esta semana.</p></div>');
    const despesasHtml = renderizarDespesasPendentes(resumo?.despesas_fixas?.pendencias || []);
    if (despesasHtml) {
        partes.push(despesasHtml);
    }
    const parcelasHtml = renderizarParcelasSemana(resumo?.parcelas_semana?.parcelas || []);
    if (parcelasHtml) {
        partes.push(parcelasHtml);
    }
    return partes.join('');
}
function renderizarDespesasPendentes(lista) {
    if (!lista || !lista.length) {
        return '<p class="mensagem-vazia">Todas as despesas fixas estão confirmadas.</p>';
    }
    const linhas = lista.map(item => `
        <tr>
            <td>${item.descricao}</td>
            <td>${item.data_vencimento ? new Date(item.data_vencimento).toLocaleDateString('pt-BR') : '-'}</td>
            <td>${formatCurrency(item.valor_previsto)}</td>
            <td>${item.status}</td>
        </tr>
    `).join('');
    return `
        <div class="card">
            <h4>Despesas Fixas a Confirmar</h4>
            <div class="table-section">
              <table class="tabela-resumo">
                  <thead>
                      <tr>
                          <th>Descrição</th>
                          <th>Vencimento</th>
                          <th>Valor</th>
                          <th>Status</th>
                      </tr>
                  </thead>
                  <tbody>${linhas}</tbody>
              </table>
            </div>
        </div>
    `;
}

function renderizarParcelasSemana(lista) {
    if (!lista || !lista.length) {
        return '<p class="mensagem-vazia">Nenhuma parcela vence nesta semana.</p>';
    }
    const linhas = lista.map(item => `
        <tr>
            <td>${item.descricao}</td>
            <td>${item.data_vencimento ? new Date(item.data_vencimento).toLocaleDateString('pt-BR') : '-'}</td>
            <td>${item.numero_parcela}/${item.total_parcelas}</td>
            <td>${formatCurrency(item.valor)}</td>
        </tr>
    `).join('');
    return `
        <div class="card">
            <h4>Parcelas da Semana</h4>
            <div class="table-section">
              <table class="tabela-resumo">
                  <thead>
                      <tr>
                          <th>Descrição</th>
                          <th>Vencimento</th>
                          <th>Parcela</th>
                          <th>Valor</th>
                      </tr>
                  </thead>
                  <tbody>${linhas}</tbody>
              </table>
            </div>
        </div>
    `;
}

function limparAreaExpansivel() {
    if (!areaExpansivel) return;
    areaExpansivel.classList.remove("mostrar");
    areaExpansivel.dataset.activeSection = "";
    areaExpansivel.innerHTML = "";
}

function mostrarAreaExpansivel(chave, builder) {
    if (!areaExpansivel) return;
    const ativo = areaExpansivel.dataset.activeSection;
    if (ativo === chave && areaExpansivel.classList.contains("mostrar")) {
        limparAreaExpansivel();
        return;
    }
    areaExpansivel.innerHTML = builder();
    areaExpansivel.dataset.activeSection = chave;
    areaExpansivel.classList.add("mostrar");
}

// -------------------------
// Função para carregar pendências da API
// -------------------------
async function carregarPendenciasAPI() {
    if (!await validarToken()) {
        return;
    }
    const token = localStorage.getItem("token");
    const url = buildApiUrl('/ListarDebitosEmAberto');

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar pendências: ${erro}`);
        }

        const pendencias = await response.json();
        atualizarCards(pendencias);
        renderizarPendencias(pendencias);
        areaExpansivel.dataset.activeSection = "pendencias";
        areaExpansivel.classList.add("mostrar");

    } catch (err) {
        console.error(err);
        console.warn("Falha ao carregar pendências.", err);
        mostrarMensagemArea("pendencias", "Nenhuma pendência registrada no momento.");
    }
}

function atualizarCards(pendencias) {
    const totalPendencias = pendencias.filter(p => p.StatusPagamento === "Pendente" || p.StatusPagamento === "Atraso").length;
    const totalAtrasos = pendencias.filter(p => p.StatusPagamento === "Atrasado").length;

    document.querySelector("#cardPendencias p").textContent = 
        `${totalAtrasos} pendência${totalAtrasos !== 1 ? 's' : ''} em atraso`;

}

function renderizarPendencias(lista) {
    if (!lista || !lista.length) {
        return '<p class="mensagem-vazia">Nenhuma pendência registrada.</p>';
    }
    const area = document.getElementById("areaExpansivel");
    area.innerHTML = `
    <div class="card">
      <div class="filtros">
        <input type="text" id="busca" placeholder="Buscar pendência...">
        <select id="filtroStatus">
          <option value="">Todos</option>
          <option value="Pendente">Pendente</option>
          <option value="Atrasado">Atrasado</option>
        </select>
      </div>

      <div class="table-section">
        <table id="tabelaPendencias">
          <thead>
            <tr>
              <th>ID</th>
              <th>Fornecedor</th>
              <th>Descrição</th>
              <th>Forma de Pagamento</th>
              <th>Valor</th>
              <th>Vencimento</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${lista.map(p => `
              <tr>
                <td>${p.ID ?? "-"}</td>
                <td>${p.Fornecedor}</td>
                <td>${p.Descricao}</td>
                <td>${p.FormaPagamento}</td>
                <td>${formatCurrency(p.Valor)}</td>
                <td>${new Date(p.Vencimento).toLocaleDateString("pt-BR")}</td>
                <td><span class="status ${p.StatusPagamento.toLowerCase()}">${p.StatusPagamento}</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

    document.querySelector("#busca").addEventListener("input", (e) => {
        const termo = e.target.value.toLowerCase();
        document.querySelectorAll("#tabelaPendencias tbody tr").forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(termo) ? "" : "none";
        });
    });

    document.querySelector("#filtroStatus").addEventListener("change", (e) => {
        const status = e.target.value.toLowerCase();
        document.querySelectorAll("#tabelaPendencias tbody tr").forEach(row => {
            const cell = row.querySelector("td:last-child .status");
            row.style.display = !status || cell.classList.contains(status) ? "" : "none";
        });
    });
}

// -------------------------
// Clique nos cards
// -------------------------
document.getElementById("cardPendencias").addEventListener("click", async () => {
    if (areaExpansivel.dataset.activeSection === "pendencias" && areaExpansivel.classList.contains("mostrar")) {
        limparAreaExpansivel();
    } else {
        await carregarPendenciasAPI();
    }
});

document.getElementById("cardAlertas").addEventListener("click", () => {
    if (!dashboardResumo) {
        return;
    }
    mostrarAreaExpansivel("alertas", () => renderizarAlertas(dashboardResumo));
});

document.getElementById("cardContasReceber").addEventListener("click", () => {
    if (!dashboardResumo) {
        return;
    }
    mostrarAreaExpansivel("entradas_semana", () => renderizarContasReceber(dashboardResumo.contas_receber_lista));
});


// -------------------------
// Ao carregar a home
// -------------------------
window.addEventListener("DOMContentLoaded", async () => {
    if (!await (window.validarToken ? window.validarToken() : Promise.resolve(true))) {
        return;
    }
    atualizarCabecalho();
    await carregarResumoDashboard();
    await carregarPendenciasAPI();
});
