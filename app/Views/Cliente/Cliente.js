let editando = null;
let tokenGlobal = null;

// -----------------------------
// Funções auxiliares
// -----------------------------
function formatarDataParaAPI(dateStr) {
  if (!dateStr) return "";
  const [ano, mes, dia] = dateStr.split("-");
  return `${dia}/${mes}/${ano}`;
}

function formatarDataParaInput(dateStr) {
  if (!dateStr) return "";
  const [dia, mes, ano] = dateStr.split("/");
  return `${ano}-${mes}-${dia}`;
}

function limparFormulario() {
  document.getElementById("cliente-form").reset();
  editando = null;
  document.getElementById("btnSalvar").textContent = "Salvar";
  [...document.querySelector("#clientes-table tbody").children].forEach(tr =>
    tr.classList.remove("selected")
  );
}

// -----------------------------
// Autenticação
// -----------------------------
// async function obterToken() {
//   const url = "http://localhost:8000/token";
//   const formData = new URLSearchParams();
//   formData.append("username", "usuario");
//   formData.append("password", "1234");
//   formData.append("grant_type", "password");

//   try {
//     const response = await fetch(url, {
//       method: "POST",
//       headers: { "Content-Type": "application/x-www-form-urlencoded" },
//       body: formData
//     });

//     if (!response.ok) {
//       const erro = await response.text();
//       throw new Error(`Erro ao obter token: ${erro}`);
//     }

//     const data = await response.json();
//     tokenGlobal = data.access_token;
//     return tokenGlobal;

//   } catch (err) {
//     console.error("Erro ao obter token:", err);
//     alert("Falha ao autenticar. Verifique o backend.");
//     return null;
//   }
// }

// -----------------------------
// Carregar representantes
// -----------------------------
async function carregarRepresentantes() {
  
  if (!await validarToken()) {
        return
    }
    const tokenGlobal =localStorage.getItem("token");

  try {
    const response = await fetch("http://127.0.0.1:8000/RepresentantesComboBox", {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });
    if (!response.ok) throw new Error("Erro ao carregar representantes");

    const lista = await response.json();
    const combo = document.getElementById("representante");
    combo.innerHTML = `<option value="">Selecione...</option>`;

    lista.forEach(item => {
      const [id, nome] = item.Representante.split(" - ");
      const option = document.createElement("option");
      option.value = id.trim();
      option.textContent = `${id} - ${nome}`;
      combo.appendChild(option);
    });

  } catch (err) {
    console.error(err);
    alert("Falha ao carregar representantes.");
  }
}

// -----------------------------
// Carregar clientes
// -----------------------------
async function carregarClientes() {
  if (!await validarToken()) {
        return
    }
    const tokenGlobal =localStorage.getItem("token");

  try {
    const response = await fetch("http://127.0.0.1:8000/Clientes", {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });
    if (!response.ok) throw new Error("Erro ao carregar clientes");

    const lista = await response.json();
    const tbody = document.querySelector("#clientes-table tbody");
    tbody.innerHTML = "";

    lista.forEach(c => {
      const tr = document.createElement("tr");
      // tr.dataset.id = c.id_cliente;
      tr.dataset.id = c.Id;

      tr.innerHTML = `
        <td>${c.Id || ""}</td>
        <td>${c.Nome || ""}</td>
        <td>${c.Cpf || ""}</td>
        <td>${c.Rg || ""}</td>
        <td>${c.DtNascimento || ""}</td>
        <td>${c.Telefone || ""}</td>
        <td>${c.Representante || ""}</td>
      `;

      // Ao clicar na linha, seleciona e preenche o formulário
      tr.addEventListener("click", () => {
        carregarFormulario(c, tr);
      });

      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error(err);
    alert("Falha ao carregar clientes.");
  }
}

// -----------------------------
// Preencher formulário para edição
// -----------------------------
function carregarFormulario(cliente, linha) {
  const form = document.getElementById("cliente-form");

  form.nome.value = cliente.Nome || "";
  form.cpf.value = cliente.Cpf || "";
  form.rg.value = cliente.Rg || "";

  if (cliente.DtNascimento) {
    form.dataNasc.value = formatarDataParaInput(cliente.DtNascimento);
  }
     if (cliente.DtNascimento && cliente.DtNascimento !== "None") {
        const [ano, mes, dia] = cliente.DtNascimento.split("-");
        form.dataNasc.value = `${ano}-${mes}-${dia}`;
    } else {
        form.dataNasc.value = '';
    }

  form.telefone.value = cliente.Telefone || "";

  const combo = form.representante;
  let selecionado = false;

  if (cliente.id_representante) {
    const optByValue = Array.from(combo.options).find(
      o => o.value === String(cliente.id_representante)
    );
    if (optByValue) {
      combo.value = optByValue.value;
      selecionado = true;
    }
  }

  if (!selecionado && cliente.Representante) {
    const optByText = Array.from(combo.options).find(
      o => o.textContent.trim() === String(cliente.Representante).trim()
    );
    if (optByText) {
      combo.value = optByText.value;
      selecionado = true;
    }
  }

  if (!selecionado) {
    combo.value = "";
  }

  // Marca a linha como selecionada
  editando = linha;
  document.getElementById("btnSalvar").textContent = "Atualizar";

  [...document.querySelector("#clientes-table tbody").children].forEach(tr =>
    tr.classList.remove("selected")
  );

  linha.classList.add("selected");
}

// -----------------------------
// Salvar ou alterar cliente
// -----------------------------
async function salvarCliente(e) {
  e.preventDefault();

  const form = document.getElementById("cliente-form");

  // Agora usamos a classe correta: 'selected'
  const linhaSelecionada = document.querySelector("#clientes-table tbody tr.selected");
  const idCliente = linhaSelecionada ? parseInt(linhaSelecionada.dataset.id) : 0;

  const cliente = {
    id_cliente: idCliente,
    id_representante: parseInt(form.representante.value),
    nm_cliente: form.nome.value.trim(),
    dt_nascimento: formatarDataParaAPI(form.dataNasc.value),
    cpf: form.cpf.value.trim(),
    rg: form.rg.value.trim(),
    telefone: form.telefone.value.trim()
  };

  if (!cliente.id_representante) {
    alert("Selecione um representante!");
    return;
  }

  const url = editando
    ? "http://127.0.0.1:8000/AlterarCliente"
    : "http://127.0.0.1:8000/InserirCliente";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${tokenGlobal}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(cliente)
    });

    if (!response.ok) throw new Error("Erro ao salvar cliente");

    alert(editando ? "Cliente atualizado!" : "Cliente cadastrado!");
    limparFormulario();
    carregarClientes();

  } catch (err) {
    console.error(err);
    alert("Falha ao salvar cliente.");
  }
}

// -----------------------------
// Inicialização
// -----------------------------
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnNovo").addEventListener("click", limparFormulario);
  document.getElementById("cliente-form").addEventListener("submit", salvarCliente);
  carregarRepresentantes().then(() => carregarClientes());
});
