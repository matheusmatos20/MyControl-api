// ================================
// Dados de teste (mockados)
// ================================
const dashboardData = {
  clientes: 25,
  pendencias: 5,
  servicos: 12,
  colaboradores: 8,
  ultimasPendencias: [
    { descricao: "Conta de Luz", categoria: "Contas Fixas", valor: 450, vencimento: "2025-08-30", status: "Pendente" },
    { descricao: "Pagamento Funcionário João", categoria: "RH", valor: 2500, vencimento: "2025-08-25", status: "Pago" },
    { descricao: "Compra de medicamentos", categoria: "Saúde", valor: 1200, vencimento: "2025-08-20", status: "Atrasado" },
  ]
};

// ================================
// Inicializar dashboard
// ================================
function initDashboard() {
  // Atualizar cards
  document.getElementById("clientes-count").innerText = dashboardData.clientes;
  document.getElementById("pendencias-count").innerText = dashboardData.pendencias;
  document.getElementById("servicos-count").innerText = dashboardData.servicos;
  document.getElementById("colaboradores-count").innerText = dashboardData.colaboradores;

  // Popular tabela de últimas pendências
  const tbody = document.querySelector("#tabelaResumo tbody");
  dashboardData.ultimasPendencias.forEach(p => {
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
// Simular consumo de API
// ================================
async function fetchDashboardData() {
  // 🔗 Quando a API estiver pronta, descomente:
  /*
  const response = await fetch("http://localhost:8000/dashboard");
  const data = await response.json();
  dashboardData = data;
  */

  initDashboard();
}

// ================================
// Inicialização
// ================================
fetchDashboardData();
