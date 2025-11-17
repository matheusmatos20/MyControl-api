const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
let fornecedores = [];
let fornecedorSelecionado = null;
let tokenGlobal = null;

function renderTabelaFornecedoresMensagem(mensagem) {
  const tbody = document.querySelector("#grid tbody");
  if (!tbody) {
    return;
  }
  tbody.innerHTML = `<tr><td colspan="6" class="mensagem-vazia">${mensagem}</td></tr>`;
}

async function carregarFornecedores() {
  if (!await validarToken()) {
    return;
  }

  tokenGlobal = localStorage.getItem("token");
  if (!tokenGlobal) {
    console.error("Token não localizado no armazenamento.");
    alert("Sessão expirada. Faça login novamente.");
    return;
  }

  try {
    const resp = await fetch(`${API_BASE}/RetornaFornecedores`, {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });

    if (!resp.ok) {
      throw new Error(await resp.text());
    }

    fornecedores = await resp.json();
    if (!fornecedores.length) {
      renderTabelaFornecedoresMensagem("Nenhum fornecedor cadastrado.");
    } else {
      renderGrid();
    }
  } catch (err) {
    console.error("Erro ao carregar fornecedores:", err);
    renderTabelaFornecedoresMensagem("Não foi possível carregar os fornecedores agora.");
  }
}

function renderGrid() {
  const tbody = document.querySelector("#grid tbody");
  if (!tbody) {
    return;
  }

  tbody.innerHTML = "";
  fornecedores.forEach((fornecedor) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${fornecedor.id_fornecedor}</td>
      <td>${fornecedor.nm_razao_social ?? ""}</td>
      <td>${fornecedor.nm_fantasia ?? ""}</td>
      <td>${fornecedor.cd_cnpj ?? ""}</td>
      <td>${fornecedor.nu_telefone ?? ""}</td>
      <td>${fornecedor.ds_endereco ?? ""}</td>
    `;
    tr.addEventListener("click", () => selecionarFornecedor(fornecedor, tr));
    tbody.appendChild(tr);
  });
}

function selecionarFornecedor(fornecedor, linha) {
  document.querySelectorAll("#grid tbody tr").forEach((tr) => tr.classList.remove("selected"));
  linha.classList.add("selected");
  fornecedorSelecionado = fornecedor;
  preencherForm(fornecedor);
  document.getElementById("btnSalvar").textContent = "Atualizar";
}

function preencherForm(fornecedor) {
  document.getElementById("razaosocial").value = fornecedor.nm_razao_social || "";
  document.getElementById("nomefantasia").value = fornecedor.nm_fantasia || "";
  document.getElementById("cnpj").value = fornecedor.cd_cnpj || "";
  document.getElementById("telefone").value = fornecedor.nu_telefone || "";
  document.getElementById("endereco").value = fornecedor.ds_endereco || "";
}

async function salvarFornecedor(event) {
  event.preventDefault();

  if (!await validarToken()) {
    return;
  }

  tokenGlobal = localStorage.getItem("token");
  if (!tokenGlobal) {
    alert("Sessão expirada. Faça login novamente.");
    return;
  }

  const fornecedor = {
    id_fornecedor: fornecedorSelecionado ? Number(fornecedorSelecionado.id_fornecedor) : 0,
    nm_razao_social: document.getElementById("razaosocial").value.trim(),
    nm_fantasia: document.getElementById("nomefantasia").value.trim(),
    cd_cnpj: document.getElementById("cnpj").value.trim(),
    nu_telefone: document.getElementById("telefone").value.trim(),
    ds_endereco: document.getElementById("endereco").value.trim()
  };

  const estaEditando = Boolean(fornecedorSelecionado);
  const endpoint = estaEditando ? `${API_BASE}/AlterarFornecedor` : `${API_BASE}/InserirFornecedor`;
  const mensagemSucesso = estaEditando ? "Fornecedor alterado com sucesso!" : "Fornecedor salvo com sucesso!";

  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${tokenGlobal}`
      },
      body: JSON.stringify(fornecedor)
    });

    if (!resp.ok) {
      throw new Error(await resp.text());
    }

    alert(mensagemSucesso);
    fornecedorSelecionado = null;
    limparForm();
    await carregarFornecedores();
    document.getElementById("btnSalvar").textContent = "Salvar";
  } catch (err) {
    console.error("Erro ao salvar fornecedor:", err);
    alert("Erro ao salvar fornecedor");
  }
}

function novoFornecedor() {
  fornecedorSelecionado = null;
  limparForm();
  document.querySelectorAll("#grid tbody tr").forEach((tr) => tr.classList.remove("selected"));
  document.getElementById("btnSalvar").textContent = "Salvar";
}

function limparForm() {
  const form = document.getElementById("formFornecedor");
  if (form) {
    form.reset();
  }
}

window.addEventListener("load", () => {
  carregarFornecedores();
  const form = document.getElementById("formFornecedor");
  const btnNovo = document.getElementById("btnNovo");

  if (form) {
    form.addEventListener("submit", salvarFornecedor);
  }

  if (btnNovo) {
    btnNovo.addEventListener("click", novoFornecedor);
  }
});
