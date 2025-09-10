console.log("Dashboard carregado com sucesso!");

// 🔹 Dados mockados (pendências)
const dadosMock = [
  { descricao: "Conta de Luz", categoria: "Contas Fixas", valor: 450, vencimento: "2025-08-30", status: "Pendente" },
  { descricao: "Pagamento Funcionário João", categoria: "RH", valor: 2500, vencimento: "2025-08-25", status: "Pago" },
  { descricao: "Compra de medicamentos", categoria: "Saúde", valor: 1200, vencimento: "2025-08-20", status: "Atrasado" },
];

// 🔹 Função para carregar a tabela
function carregarPendencias(lista) {
  const area = document.getElementById("areaExpansivel");
  area.innerHTML = `
    <div class="card">
      <div class="filtros">
        <input type="text" id="busca" placeholder="Buscar pendência...">
        <select id="filtroStatus">
          <option value="">Todos</option>
          <option value="Pendente">Pendente</option>
          <option value="Pago">Pago</option>
          <option value="Atrasado">Atrasado</option>
        </select>
      </div>

      <table id="tabelaPendencias">
        <thead>
          <tr>
            <th>Descrição</th>
            <th>Categoria</th>
            <th>Valor</th>
            <th>Vencimento</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${lista.map(p => `
            <tr>
              <td>${p.descricao}</td>
              <td>${p.categoria}</td>
              <td>R$ ${parseFloat(p.valor).toFixed(2)}</td>
              <td>${new Date(p.vencimento).toLocaleDateString("pt-BR")}</td>
              <td><span class="status ${p.status.toLowerCase()}">${p.status}</span></td>
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

// 🔹 Clique no card Pendências
document.getElementById("cardPendencias").addEventListener("click", () => {
  const area = document.getElementById("areaExpansivel");
  if (area.classList.contains("mostrar")) {
    area.classList.remove("mostrar");
    area.innerHTML = "";
  } else {
    carregarPendencias(dadosMock);
    area.classList.add("mostrar");
  }
});
