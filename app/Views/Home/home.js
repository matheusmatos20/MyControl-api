console.log("Dashboard carregado com sucesso!");

// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = localStorage.getItem("token");

const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
const buildApiUrl = window.buildApiUrl || (path => `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`);

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


// -------------------------
// Função para obter o token
// -------------------------
// async function obterToken() {
    
//     const url = 'http://localhost:8000/token';
//     const formData = new URLSearchParams();
//     formData.append('username', 'usuario');
//     formData.append('password', '1234');
//     formData.append('grant_type', 'password');

//     try {
//         const response = await fetch(url, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//             body: formData
//         });

//         if (!response.ok) {
//             const erro = await response.text();
//             throw new Error(`Erro ao obter token: ${erro}`);
//         }

//         const data = await response.json();
//         tokenGlobal = data.access_token;
//         return tokenGlobal;

//     } catch (err) {
//         console.error('Erro ao obter token:', err);
//         alert("Falha ao autenticar. Verifique o backend e abra via localhost:5501.");
//         return null;
//     }
// }

// -------------------------
// Função para carregar pendências da API
// -------------------------
async function carregarPendenciasAPI() {
    // if (!tokenGlobal) {
    //     await obterToken();
    //     if (!tokenGlobal) return;
    // }

    
    if (!await validarToken()) {
        return
    }
    const tokenGlobal =localStorage.getItem("token");
    
    const url = buildApiUrl('/ListarDebitosEmAberto');

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar pendências: ${erro}`);
        }

        const pendencias = await response.json();

        // Atualiza os cards
        atualizarCards(pendencias);

        // Renderiza a grid
        renderizarPendencias(pendencias);

    } catch (err) {
        console.error(err);
        alert("Falha ao carregar pendências. Veja o console para detalhes.");
    }
}

// -------------------------
// Atualizar os cards dinâmicos
// -------------------------
function atualizarCards(pendencias) {
    const totalPendencias = pendencias.filter(p => p.StatusPagamento === "Pendente" || p.StatusPagamento === "Atraso").length;
    const totalAtrasos = pendencias.filter(p => p.StatusPagamento === "Atrasado").length;

    document.querySelector("#cardPendencias p").textContent = 
        `${totalAtrasos} pendência${totalAtrasos !== 1 ? 's' : ''} em atraso`;

    document.querySelector("#cardAlertas p").textContent = 
        `${totalPendencias} pagamento${totalPendencias !== 1 ? 's' : ''} em aberto${totalPendencias !== 1 ? 's' : ''}`;
}

// -------------------------
// Função para renderizar a grid
// -------------------------
function renderizarPendencias(lista) {
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
              <td>R$ ${Number(p.Valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}</td>
              <td>${new Date(p.Vencimento).toLocaleDateString("pt-BR")}</td>
              <td><span class="status ${p.StatusPagamento.toLowerCase()}">${p.StatusPagamento}</span></td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

    // Filtro por busca
    document.querySelector("#busca").addEventListener("input", (e) => {
        const termo = e.target.value.toLowerCase();
        document.querySelectorAll("#tabelaPendencias tbody tr").forEach(row => {
            row.style.display = row.innerText.toLowerCase().includes(termo) ? "" : "none";
        });
    });

    // Filtro por status
    document.querySelector("#filtroStatus").addEventListener("change", (e) => {
        const status = e.target.value.toLowerCase();
        document.querySelectorAll("#tabelaPendencias tbody tr").forEach(row => {
            const cell = row.querySelector("td:last-child .status");
            row.style.display = !status || cell.classList.contains(status) ? "" : "none";
        });
    });
}

// -------------------------
// Clique no card Pendências
// -------------------------
document.getElementById("cardPendencias").addEventListener("click", async () => {
    const area = document.getElementById("areaExpansivel");
    if (area.classList.contains("mostrar")) {
        area.classList.remove("mostrar");
        area.innerHTML = "";
    } else {
        await carregarPendenciasAPI();
        area.classList.add("mostrar");
    }
});

document.getElementById("cardAlertas").addEventListener("click", async () => {
    const area = document.getElementById("areaExpansivel");
    if (area.classList.contains("mostrar")) {
        area.classList.remove("mostrar");
        area.innerHTML = "";
    } else {
        await carregarPendenciasAPI();
        area.classList.add("mostrar");
    }
});

// -------------------------
// Ao carregar a home já atualiza os cards
// -------------------------
window.addEventListener("DOMContentLoaded", async () => {
    await validarToken();
    atualizarCabecalho();
    await carregarPendenciasAPI(); // já puxa os números reais
});

