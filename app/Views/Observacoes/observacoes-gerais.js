// ================================
// Função para buscar pendências
// ================================
async function buscarPendencias() {
  try {
    // 🔗 QUANDO SUA API ESTIVER PRONTA, DESCOMENTE ESSA PARTE:
    /*
    const response = await fetch("http://localhost:8000/pendencias"); 
    if (!response.ok) throw new Error("Erro ao consultar API");

    const data = await response.json();
    carregarPendencias(data);
    */

    // 🔧 DADOS MOCKADOS PARA TESTE ENQUANTO A API NÃO ESTÁ DISPONÍVEL
    const dadosMock = [
      { descricao: "Conta de Luz", categoria: "Contas Fixas", valor: 450, vencimento: "2025-08-30", status: "Pendente" },
      { descricao: "Pagamento Funcionário João", categoria: "RH", valor: 2500, vencimento: "2025-08-25", status: "Pago" },
      { descricao: "Compra de medicamentos", categoria: "Saúde", valor: 1200, vencimento: "2025-08-20", status: "Atrasado" },
    ];
    carregarPendencias(dadosMock);

  } catch (error) {
    console.error("Erro:", error);
    alert("Não foi possível carregar as pendências.");
  }
}

// ================================
// Renderizar tabela
// ================================
function carregarPendencias(lista) {
  const tbody = document.querySelector("#tabelaPendencias tbody");
  tbody.innerHTML = "";

  if (!lista || lista.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5">Nenhuma pendência encontrada.</td></tr>`;
    return;
  }

  lista.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.descricao}</td>
      <td>${p.categoria}</td>
      <td>R$ ${parseFloat(p.valor).toFixed(2)}</td>
      <td>${new Date(p.vencimento).toLocaleDateString("pt-BR")}</td>
      <td><span class="status ${p.status.toLowerCase()}">${p.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// ================================
// Filtro por busca
// ================================
document.querySelector("#busca").addEventListener("input", async (e) => {
  const termo = e.target.value.toLowerCase();

  // 🔗 QUANDO SUA API ESTIVER PRONTA, DESCOMENTE E USE QUERY PARAMS:
  /*
  const response = await fetch(`http://localhost:8000/pendencias?busca=${termo}`);
  const pendencias = await response.json();
  carregarPendencias(pendencias);
  */

  // 🔧 FILTRO LOCAL (usando os dados já carregados da API)
  const rows = document.querySelectorAll("#tabelaPendencias tbody tr");
  rows.forEach(row => {
    const texto = row.innerText.toLowerCase();
    row.style.display = texto.includes(termo) ? "" : "none";
  });
});

// ================================
// Filtro por status
// ================================
document.querySelector("#filtroStatus").addEventListener("change", async (e) => {
  const status = e.target.value.toLowerCase();

  // 🔗 QUANDO SUA API ESTIVER PRONTA, DESCOMENTE E USE QUERY PARAMS:
  /*
  const response = await fetch(`http://localhost:8000/pendencias?status=${status}`);
  const pendencias = await response.json();
  carregarPendencias(pendencias);
  */

  // 🔧 FILTRO LOCAL (usando os dados já carregados da API)
  const rows = document.querySelectorAll("#tabelaPendencias tbody tr");
  rows.forEach(row => {
    const cell = row.querySelector("td:last-child .status");
    if (!status || cell.classList.contains(status)) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
});

// ================================
// Inicialização
// ================================
buscarPendencias();
