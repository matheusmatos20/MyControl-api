// Mock da API simulada
const apiColaborador = {
  getColaboradores: async () => {
    return [
      { id: 1, nome: "Carlos Mendes" },
      { id: 2, nome: "Ana Paula" },
      { id: 3, nome: "Ricardo Gomes" }
    ];
  },
  getCargos: async () => {
    return [
      { id: 1, nome: "Cuidador" },
      { id: 2, nome: "Enfermeiro" },
      { id: 3, nome: "Fisioterapeuta" }
    ];
  },
  getHistorico: async (id) => {
    if (id == 1) {
      return [
        { data: "2022-01-01", cargo: "Cuidador", salario: 1800 },
        { data: "2023-01-01", cargo: "Enfermeiro", salario: 2500 }
      ];
    } else if (id == 2) {
      return [
        { data: "2021-03-01", cargo: "Fisioterapeuta", salario: 3000 }
      ];
    }
    return [];
  },
  getColaboradorById: async (id) => {
    if (id == 1) {
      return {
        nome: "Carlos Mendes", cpf: "12345678901", rg: "11223344",
        nascimento: "1985-05-10", admissao: "2021-02-15",
        cargo: 2, salario: 2500, vr: 300, vt: 200
      };
    } else if (id == 2) {
      return {
        nome: "Ana Paula", cpf: "98765432100", rg: "55667788",
        nascimento: "1990-09-20", admissao: "2022-06-01",
        cargo: 3, salario: 3000, vr: 400, vt: 250
      };
    }
    return {
      nome: "", cpf: "", rg: "", nascimento: "", admissao: "",
      cargo: 1, salario: "", vr: "", vt: ""
    };
  }
};

let colaboradorAtual = null;

// Inicialização
window.onload = async () => {
  await carregarCombos();
};

async function carregarCombos() {
  const colaboradores = await apiColaborador.getColaboradores();
  const cargos = await apiColaborador.getCargos();

  document.getElementById("colaboradores").innerHTML =
    colaboradores.map(c => `<option value="${c.id}">${c.id} - ${c.nome}</option>`).join("");

  document.getElementById("cargo").innerHTML =
    cargos.map(c => `<option value="${c.id}">${c.id} - ${c.nome}</option>`).join("");
}

// Carregar colaborador selecionado
async function carregarColaborador() {
  const id = document.getElementById("colaboradores").value;
  colaboradorAtual = await apiColaborador.getColaboradorById(id);

  document.getElementById("nome").value = colaboradorAtual.nome;
  document.getElementById("cpf").value = colaboradorAtual.cpf;
  document.getElementById("rg").value = colaboradorAtual.rg;
  document.getElementById("nascimento").value = colaboradorAtual.nascimento;
  document.getElementById("admissao").value = colaboradorAtual.admissao;
  document.getElementById("cargo").value = colaboradorAtual.cargo;
  document.getElementById("salario").value = colaboradorAtual.salario;
  document.getElementById("vr").value = colaboradorAtual.vr;
  document.getElementById("vt").value = colaboradorAtual.vt;

  carregarHistorico(id);
}

// Carregar histórico (grid)
async function carregarHistorico(id) {
  const dados = await apiColaborador.getHistorico(id);
  const tbody = document.querySelector("#grid tbody");
  tbody.innerHTML = "";

  dados.forEach(h => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${h.data}</td>
      <td>${h.cargo}</td>
      <td>${h.salario}</td>
    `;
    tbody.appendChild(row);
  });
}

// Salvar alterações
function salvarColaborador() {
  if (!colaboradorAtual) {
    alert("Selecione um colaborador!");
    return;
  }

  colaboradorAtual.nome = document.getElementById("nome").value;
  colaboradorAtual.cpf = document.getElementById("cpf").value;
  colaboradorAtual.rg = document.getElementById("rg").value;
  colaboradorAtual.nascimento = document.getElementById("nascimento").value;
  colaboradorAtual.admissao = document.getElementById("admissao").value;
  colaboradorAtual.cargo = document.getElementById("cargo").value;
  colaboradorAtual.salario = document.getElementById("salario").value;
  colaboradorAtual.vr = document.getElementById("vr").value;
  colaboradorAtual.vt = document.getElementById("vt").value;

  alert("Colaborador atualizado com sucesso!");
}

// Apenas números
function somenteNumero(e) {
  const charCode = e.which ? e.which : e.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57)) {
    return false;
  }
  return true;
}
