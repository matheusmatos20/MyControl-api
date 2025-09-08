// Mock simples (você pode depois ligar com API real)
let colaboradores = [
  { id: 1, nome: "Carlos Mendes", cpf: "12345678901", cargo: "Enfermeiro" },
  { id: 2, nome: "Ana Paula", cpf: "98765432100", cargo: "Fisioterapeuta" }
];

let cargos = ["Cuidador", "Enfermeiro", "Fisioterapeuta"];
let colaboradorSelecionado = null;

// Inicializar
window.onload = () => {
  carregarCargos();
  renderGrid();
  document.getElementById("formColaborador").addEventListener("submit", salvarColaborador);
  document.getElementById("btnNovo").addEventListener("click", novoColaborador);
};

function carregarCargos() {
  document.getElementById("cargo").innerHTML =
    cargos.map(c => `<option value="${c}">${c}</option>`).join("");
}

function renderGrid() {
  const tbody = document.querySelector("#grid tbody");
  tbody.innerHTML = "";
  colaboradores.forEach(c => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.id}</td>
      <td>${c.nome}</td>
      <td>${c.cpf}</td>
      <td>${c.cargo}</td>
    `;
    tr.onclick = () => selecionarColaborador(c, tr);
    tbody.appendChild(tr);
  });
}

function selecionarColaborador(c, row) {
  // limpar seleção antiga
  document.querySelectorAll("#grid tbody tr").forEach(tr => tr.classList.remove("selected"));
  row.classList.add("selected");

  colaboradorSelecionado = c;
  preencherForm(c);
  document.getElementById("btnSalvar").textContent = "Atualizar";
}

function preencherForm(c) {
  document.getElementById("nome").value = c.nome;
  document.getElementById("cpf").value = c.cpf;
  document.getElementById("rg").value = c.rg || "";
  document.getElementById("nascimento").value = c.nascimento || "";
  document.getElementById("admissao").value = c.admissao || "";
  document.getElementById("salario").value = c.salario || "";
  document.getElementById("va").value = c.va || "";
  document.getElementById("vr").value = c.vr || "";
  document.getElementById("vt").value = c.vt || "";
  document.getElementById("cargo").value = c.cargo;
}

function salvarColaborador(e) {
  e.preventDefault();

  const novo = {
    id: colaboradorSelecionado ? colaboradorSelecionado.id : colaboradores.length + 1,
    nome: document.getElementById("nome").value,
    cpf: document.getElementById("cpf").value,
    rg: document.getElementById("rg").value,
    nascimento: document.getElementById("nascimento").value,
    admissao: document.getElementById("admissao").value,
    salario: document.getElementById("salario").value,
    va: document.getElementById("va").value,
    vr: document.getElementById("vr").value,
    vt: document.getElementById("vt").value,
    cargo: document.getElementById("cargo").value
  };

  if (colaboradorSelecionado) {
    // atualizar
    const idx = colaboradores.findIndex(c => c.id === colaboradorSelecionado.id);
    colaboradores[idx] = novo;
    alert("Colaborador atualizado!");
  } else {
    // novo
    colaboradores.push(novo);
    alert("Colaborador adicionado!");
  }

  colaboradorSelecionado = null;
  limparForm();
  renderGrid();
  document.getElementById("btnSalvar").textContent = "Salvar";
}

function novoColaborador() {
  colaboradorSelecionado = null;
  limparForm();
  document.querySelectorAll("#grid tbody tr").forEach(tr => tr.classList.remove("selected"));
  document.getElementById("btnSalvar").textContent = "Salvar";
}

function limparForm() {
  document.getElementById("formColaborador").reset();
}
