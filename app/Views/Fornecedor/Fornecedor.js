let fornecedores = [];
let fornecedorSelecionado = null;
let tokenGlobal = null;

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

//     if (!response.ok) throw new Error(await response.text());

//     const data = await response.json();
//     tokenGlobal = data.access_token;
//     return tokenGlobal;

//   } catch (err) {
//     console.error("Erro ao obter token:", err);
//     alert("Falha ao autenticar. Verifique o backend.");
//     return null;
//   }
// }

async function carregarFornecedores() {
  
  if (!await validarToken()) {
        return
    }
    const token =localStorage.getItem("token");

  try {
    const resp = await fetch("http://localhost:8000/RetornaFornecedores", {
      headers: { "Authorization": "Bearer " + token }
    });
    fornecedores = await resp.json();
    renderGrid();
  } catch (err) {
    console.error("Erro ao carregar fornecedores:", err);
    alert("Erro ao carregar fornecedores");
  }
}

function renderGrid() {
  const tbody = document.querySelector("#grid tbody");
  tbody.innerHTML = "";
  fornecedores.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${f.id_fornecedor}</td>
      <td>${f.nm_razao_social}</td>
      <td>${f.nm_fantasia}</td>
      <td>${f.cd_cnpj}</td>
      <td>${f.nu_telefone}</td>
      <td>${f.ds_endereco}</td>
    `;
    tr.onclick = () => selecionarFornecedor(f, tr);
    tbody.appendChild(tr);
  });
}

function selecionarFornecedor(f, row) {
  document.querySelectorAll("#grid tbody tr").forEach(tr => tr.classList.remove("selected"));
  row.classList.add("selected");

  fornecedorSelecionado = f;
  preencherForm(f);
  document.getElementById("btnSalvar").textContent = "Atualizar";
}

function preencherForm(f) {
  document.getElementById("razaosocial").value = f.nm_razao_social || "";
  document.getElementById("nomefantasia").value = f.nm_fantasia || "";
  document.getElementById("cnpj").value = f.cd_cnpj || "";
  document.getElementById("telefone").value = f.nu_telefone || "";
  document.getElementById("endereco").value = f.ds_endereco || "";
}

async function salvarFornecedor(e) {
  e.preventDefault();
  
  if (!token) return;

  if (!await validarToken()) {
        return
    }
    const token = localStorage.getItem("token");

  const fornecedor = {
    id_fornecedor: fornecedorSelecionado ? fornecedorSelecionado.id_fornecedor : 0,
    nm_razao_social: document.getElementById("razaosocial").value,
    nm_fantasia: document.getElementById("nomefantasia").value,
    cd_cnpj: document.getElementById("cnpj").value,
    nu_telefone: document.getElementById("nutelefone").value,
    ds_endereco: document.getElementById("endereco").value
  };

  try {
    const resp = await fetch("http://localhost:8000/InserirFornecedor", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(fornecedor)
    });

    if (!resp.ok) throw new Error(await resp.text());

    alert("Fornecedor salvo com sucesso!");
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
  document.querySelectorAll("#grid tbody tr").forEach(tr => tr.classList.remove("selected"));
  document.getElementById("btnSalvar").textContent = "Salvar";
}

function limparForm() {
  document.getElementById("formFornecedor").reset();
}

// Inicializar
window.onload = () => {
  carregarFornecedores();
  document.getElementById("formFornecedor").addEventListener("submit", salvarFornecedor);
  document.getElementById("btnNovo").addEventListener("click", novoFornecedor);
};
