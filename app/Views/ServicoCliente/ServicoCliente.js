// Simulação de API (mock)
const api = {
  getClientes: async () => {
    return [
      { id: 1, nome: "João Silva" },
      { id: 2, nome: "Maria Souza" },
      { id: 3, nome: "Pedro Oliveira" }
    ];
  },
  getServicos: async () => {
    return [
      { id: 1, nome: "Banho assistido" },
      { id: 2, nome: "Acompanhamento médico" },
      { id: 3, nome: "Fisioterapia" }
    ];
  },
  getServicosCliente: async () => {
    return [
      { id: 101, cliente: "João Silva", servico: "Banho assistido", valor: 1200, desconto: 100 },
      { id: 102, cliente: "Maria Souza", servico: "Fisioterapia", valor: 1500, desconto: 200 }
    ];
  }
};

let editRow = null;

// Inicialização da tela
window.onload = async () => {
  await carregarCombos();
  await carregarGrid();
};

// Carregar opções de cliente e serviço
async function carregarCombos() {
  const clientes = await api.getClientes();
  const servicos = await api.getServicos();

  const cmbCliente = document.getElementById("cliente");
  const cmbServico = document.getElementById("servico");

  cmbCliente.innerHTML = clientes.map(c => `<option value="${c.id}">${c.id} - ${c.nome}</option>`).join("");
  cmbServico.innerHTML = servicos.map(s => `<option value="${s.id}">${s.id} - ${s.nome}</option>`).join("");
}

// Carregar serviços contratados
async function carregarGrid() {
  const dados = await api.getServicosCliente();
  const tbody = document.querySelector("#grid tbody");
  tbody.innerHTML = "";

  dados.forEach(d => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${d.id}</td>
      <td>${d.cliente}</td>
      <td>${d.servico}</td>
      <td>${d.valor}</td>
      <td>${d.desconto}</td>
    `;
    row.onclick = () => preencherCampos(row);
    tbody.appendChild(row);
  });
}

// Preencher os campos ao clicar no grid
function preencherCampos(row) {
  editRow = row;
  const cells = row.cells;

  document.getElementById("cliente").value = [...document.getElementById("cliente").options]
    .find(opt => opt.text.includes(cells[1].innerText)).value;

  document.getElementById("servico").value = [...document.getElementById("servico").options]
    .find(opt => opt.text.includes(cells[2].innerText)).value;

  document.getElementById("valor").value = cells[3].innerText;
  document.getElementById("desconto").value = cells[4].innerText;
}

// Salvar serviço (novo ou edição)
function salvarServico() {
  const clienteSel = document.getElementById("cliente");
  const servicoSel = document.getElementById("servico");
  const valor = document.getElementById("valor").value;
  const desconto = document.getElementById("desconto").value;

  if (!valor || !desconto) {
    alert("Preencha todos os campos!");
    return;
  }

  if (editRow) {
    // Atualiza registro existente
    editRow.cells[1].innerText = clienteSel.options[clienteSel.selectedIndex].text.split(" - ")[1];
    editRow.cells[2].innerText = servicoSel.options[servicoSel.selectedIndex].text.split(" - ")[1];
    editRow.cells[3].innerText = valor;
    editRow.cells[4].innerText = desconto;
    editRow = null;
    alert("Serviço atualizado com sucesso!");
  } else {
    // Insere novo registro
    const tbody = document.querySelector("#grid tbody");
    const newRow = tbody.insertRow();
    newRow.innerHTML = `
      <td>${Math.floor(Math.random() * 1000) + 200}</td>
      <td>${clienteSel.options[clienteSel.selectedIndex].text.split(" - ")[1]}</td>
      <td>${servicoSel.options[servicoSel.selectedIndex].text.split(" - ")[1]}</td>
      <td>${valor}</td>
      <td>${desconto}</td>
    `;
    newRow.onclick = () => preencherCampos(newRow);
    alert("Serviço inserido com sucesso!");
  }

  // Limpa campos
  document.getElementById("valor").value = "";
  document.getElementById("desconto").value = "";
}
