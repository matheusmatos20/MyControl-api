const api_base = "http://127.0.0.1:8000";

let colaboradores = [];
let cargosColaborador = [];
let colaboradorSelecionado = null;

// Inicialização
window.onload = async () => {
  await obterToken();
  // garantia: carregar cargos primeiro para o select já estar preenchido quando usuário clicar na grid
  await carregarCargos();
  await carregarColaboradores();

  document.getElementById("btnSalvar").onclick = salvarColaboradorCargo;
  document.getElementById("btnNovo").onclick = novoColaborador;
  document.getElementById("closeHistorico").onclick = () => {
    document.getElementById("historicoModal").style.display = "none";
  };
};

// Obter token
async function obterToken() {
  try {
    const resp = await fetch(`${api_base}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: "usuario",   // <<< ajuste para o user correto
        password: "1234"       // <<< ajuste para a senha correta
      })
    });

    if (!resp.ok) throw new Error("Falha ao autenticar");
    const data = await resp.json();
    localStorage.setItem("token", data.access_token);
  } catch (err) {
    console.error("Erro ao obter token:", err);
    alert("Erro ao autenticar no backend");
  }
}

// Buscar cargos do backend
async function carregarCargos() {
  const token = localStorage.getItem("token");
  try {
    const resp = await fetch(`${api_base}/Cargos`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await resp.json();
    const select = document.getElementById("id_cargo");
    cargosColaborador = data;
    select.innerHTML = data
      .map(c => `<option value="${c.ID}">${c.Cargo}</option>`)
      .join("");
  } catch (err) {
    console.error("Erro ao carregar cargos:", err);
  }
}

// Buscar colaboradores
async function carregarColaboradores() {
  const token = localStorage.getItem("token");
  try {
    const resp = await fetch(`${api_base}/Colaboradores`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    colaboradores = await resp.json();
    renderGridColaboradores();
  } catch (err) {
    console.error("Erro ao carregar colaboradores:", err);
  }
}

function renderGridColaboradores() {
  const tbody = document.getElementById("tbodyColaboradores");
  tbody.innerHTML = "";
  colaboradores.forEach(colab => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${colab.Id}</td>
      <td>${colab.NomeColaborador}</td>
      <td>${colab.DtNascimento}</td>
      <td>${colab.Cpf}</td>
      <td>${colab.Rg}</td>
      <td>${colab.StatusColaborador}</td>
      <td>${colab.Cargo || "-"}</td>
      <td><button onclick="abrirHistorico(${colab.Id})">Histórico</button></td>
    `;
    tr.onclick = (e) => {
      if (e.target.tagName !== "BUTTON") carregarFormulario(colab);
    };
    tbody.appendChild(tr);
  });
}

// Helper: tenta extrair id do cargo a partir do objeto retornado pelo backend
function extractCargoIdFromColab(colab) {
  // tenta várias formas comuns de nome de propriedade
  const possibilities = [
    colab.IdCargo,
    colab.Id_Cargo,
    colab.id_cargo,
    colab.ID_CARGO,
    colab.Id_Cargo,
    colab.idCargo,
    colab.idCargoAtual,
    colab.IdCargoAtual
  ];
  for (const v of possibilities) {
    if (v !== undefined && v !== null && v !== "") return v;
  }
  return null;
}

// Preencher form ao selecionar colaborador
function carregarFormulario(colab) {
  colaboradorSelecionado = colab;

  // seta o ID (hidden) para controlar insert vs update
  const idHidden = document.getElementById("id_funcionario");
  idHidden.value = colab.Id || "";

  document.getElementById("nm_funcionario").value = colab.NomeColaborador || "";
  document.getElementById("dt_nascimento").value = colab.DtNascimento || "";
  document.getElementById("cd_cpf").value = colab.Cpf || "";
  document.getElementById("cd_rg").value = colab.Rg || "";
  document.getElementById("dt_cargo").value = colab.DtAdmissao || "";
  document.getElementById("vl_salario").value = colab.Salario || "";
  document.getElementById("vl_refeicao").value = colab.Refeicao || "";
  document.getElementById("vl_alimentacao").value = colab.Alimentacao || "";
  document.getElementById("vl_inss").value = colab.Inss || "";
  document.getElementById("vl_fgts").value = colab.Fgts || "";
  document.getElementById("vl_plano_saude").value = colab.PlanoSaude || "";
  document.getElementById("vl_transporte").value = colab.ValeTransporte || "";

  // Selecionar cargo no combobox — tenta por id primeiro, se não encontrar tenta casar pelo texto
  const selectCargo = document.getElementById("id_cargo");
  const cargoId = extractCargoIdFromColab(colab);

  if (cargoId) {
    // tenta achar option com value == cargoId
    const opt = Array.from(selectCargo.options).find(o => String(o.value) === String(cargoId));
    if (opt) {
      selectCargo.value = opt.value;
    } else {
      // fallback: tenta casar pelo texto de exibição (colab.Cargo)
      if (colab.Cargo) {
        const byText = Array.from(selectCargo.options).find(o => o.text === colab.Cargo || o.text.toLowerCase() === String(colab.Cargo).toLowerCase());
        if (byText) selectCargo.value = byText.value;
        else selectCargo.selectedIndex = 0;
      } else {
        selectCargo.selectedIndex = 0;
      }
    }
  } else if (colab.Cargo) {
    // se não tem id, tenta casar pelo texto
    const byText = Array.from(selectCargo.options).find(o => o.text === colab.Cargo || o.text.toLowerCase() === String(colab.Cargo).toLowerCase());
    if (byText) selectCargo.value = byText.value;
    else selectCargo.selectedIndex = 0;
  } else {
    selectCargo.selectedIndex = 0;
  }
}

// Limpar form para novo
function novoColaborador() {
  colaboradorSelecionado = null;
  document.getElementById("formColaborador").reset();
  document.getElementById("id_funcionario").value = ""; // limpa hidden id também
}

// Salvar colaborador + cargo
async function salvarColaboradorCargo() {
  const token = localStorage.getItem("token");
  const idFuncionario = document.getElementById("id_funcionario").value;

  // monta objeto colaborador (incluir id_funcionario quando houver)
  const colaborador = {
    id_funcionario: idFuncionario ? parseInt(idFuncionario) : 0,
    nm_funcionario: document.getElementById("nm_funcionario").value,
    dt_nascimento: document.getElementById("dt_nascimento").value,
    cd_cpf: document.getElementById("cd_cpf").value,
    cd_rg: document.getElementById("cd_rg").value,
    id_usuario: 3
  };

  const colaborador_cargo = {
    id_funcionario: idFuncionario ? parseInt(idFuncionario) : 0,
    dt_cargo: document.getElementById("dt_cargo").value,
    vl_salario: parseFloat(document.getElementById("vl_salario").value),
    id_usuario: 3,
    vl_transporte: parseFloat(document.getElementById("vl_transporte").value) || null,
    vl_alimentacao: parseFloat(document.getElementById("vl_alimentacao").value) || null,
    vl_plano_saude: parseFloat(document.getElementById("vl_plano_saude").value) || null,
    vl_refeicao: parseFloat(document.getElementById("vl_refeicao").value) || null,
    vl_inss: parseFloat(document.getElementById("vl_inss").value) || null,
    vl_fgts: parseFloat(document.getElementById("vl_fgts").value) || null,
    dt_desligamento: null,
    id_cargo: parseInt(document.getElementById("id_cargo").value)
  };

  try {
    // Decide endpoint + method conforme idFuncionario
    let url = `${api_base}/InserirColaboradorComCargo/`;
    let method = "POST";
    if (idFuncionario && String(idFuncionario).trim() !== "") {
      url = `${api_base}/AlterarColaboradorComCargo/`;
      method = "POST";
    }

    const resp = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ colaborador, colaborador_cargo })
    });

    // tenta parse do JSON (mesmo erro do backend será mostrado)
    const result = await resp.json().catch(() => null);

    if (!resp.ok) {
      // mostra mensagem detalhada quando possível
      const errMsg = (result && (result.mensagem || result.detail || JSON.stringify(result))) || `Status ${resp.status}`;
      alert("Erro ao salvar colaborador: " + errMsg);
      console.error("Erro salvar:", resp.status, result);
      return;
    }

    // Success
    alert((result && (result.mensagem || "Colaborador salvo!")) || "Colaborador salvo!");

    // se era insert, limpa o formulário; se update, mantém o form com dados (você pode querer limpar ou não)
    if (!idFuncionario) {
      // tenta obter novo id retornado pelo backend e setar no hidden (se for retornado)
      const newId = (result && (result.id_funcionario || result.Id || result.id)) || null;
      if (newId) document.getElementById("id_funcionario").value = newId;
      // limpa form para novo cadastro
      document.getElementById("formColaborador").reset();
      document.getElementById("id_funcionario").value = "";
    }

    // Recarrega grid
    await carregarColaboradores();
  } catch (err) {
    console.error("Erro ao salvar colaborador:", err);
    alert("Erro ao salvar colaborador");
  }
}

// Histórico de cargos
async function abrirHistorico(idColaborador) {
  const token = localStorage.getItem("token");
  const modal = document.getElementById("historicoModal");
  const tbody = document.getElementById("tbodyHistorico");
  modal.style.display = "block";
  tbody.innerHTML = "<tr><td colspan='4'>Carregando...</td></tr>";

  try {
    const resp = await fetch(`${api_base}/ColaboradoresCargos?id_funcionario=${idColaborador}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const historico = await resp.json();

    tbody.innerHTML = "";
    historico.forEach(cargo => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${cargo.DT_CARGO}</td>
        <td>${cargo.VL_SALARIO}</td>
        <td>${cargo.CARGO}</td>
        <td>${cargo.DT_DESLIGAMENTO || "-"}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Erro ao carregar histórico:", err);
    tbody.innerHTML = "<tr><td colspan='4'>Erro ao carregar histórico</td></tr>";
  }
}
