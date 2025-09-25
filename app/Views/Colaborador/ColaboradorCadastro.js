const api_base = "http://127.0.0.1:8000";

let colaboradores = [];
let cargosColaborador = [];
let colaboradorSelecionado = null;
let json = null;
// Inicialização
window.onload = async () => {
  if (!await validarToken()) {
    return;
  }

  // garantia: carregar cargos primeiro para o select já estar preenchido quando usuário clicar na grid
  await carregarCargos();
  await carregarColaboradores();

  document.getElementById("btnSalvar").onclick = salvarColaboradorCargo;
  document.getElementById("btnNovo").onclick = novoColaborador;
  document.getElementById("closeHistorico").onclick = () => {
    document.getElementById("historicoModal").style.display = "none";
  };
};

// Validação simples de token (ajuste conforme sua lógica real)
async function validarToken() {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Token não encontrado. Faça login.");
    return false;
  }
  // aqui você pode verificar validade do token chamando o backend se quiser
  return true;
}

// Buscar cargos do backend
async function carregarCargos() {
  const token = localStorage.getItem("token");
  try {
    const resp = await fetch(`${api_base}/Cargos`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    const data = await resp.json();
    const select = document.getElementById("id_cargo");
    cargosColaborador = data || [];
    select.innerHTML = (data || [])
      .map(c => `<option value="${c.ID}">${c.ID} - ${c.Cargo}</option>`)
      .join("");
  } catch (err) {
    console.error("Erro ao carregar cargos:", err);
    // deixa o select vazio mas não trava a aplicação
    const select = document.getElementById("id_cargo");
    if (select) select.innerHTML = "<option value=''>-- nenhum cargo --</option>";
  }
}

// Buscar colaboradores
async function carregarColaboradores() {
  const token = localStorage.getItem("token");
  try {
    const resp = await fetch(`${api_base}/Colaboradores`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    colaboradores = await resp.json();
    renderGridColaboradores();
  } catch (err) {
    console.error("Erro ao carregar colaboradores:", err);
    colaboradores = [];
    renderGridColaboradores();
  }
}

function renderGridColaboradores() {
  const tbody = document.getElementById("tbodyColaboradores");
  if (!tbody) return;
  tbody.innerHTML = "";
  colaboradores.forEach(colab => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${colab.Id}</td>
      <td>${colab.NomeColaborador}</td>
      <td>${colab.DtNascimento || "-"}</td>
      <td>${colab.Cpf || "-"}</td>
      <td>${colab.Rg || "-"}</td>
      <td>${colab.StatusColaborador || "-"}</td>
      <td>${colab.Cargo || "-"}</td>
      <td><button type="button" onclick="abrirHistorico(${colab.Id})">Histórico</button></td>
    `;
    tr.onclick = (e) => {
      if (e.target.tagName !== "BUTTON") carregarFormulario(colab);
    };
    tbody.appendChild(tr);
  });
}

// Helper: tenta extrair id do cargo a partir do objeto retornado pelo backend
function extractCargoIdFromColab(colab) {
  if (!colab) return null;
  // tenta várias formas comuns de nome de propriedade
  const possibilities = [
    colab.IdCargo,
    colab.Id_Cargo,
    colab.id_cargo,
    colab.ID_CARGO,
    colab.Id_Cargo,
    colab.idCargo,
    colab.idCargoAtual,
    colab.IdCargoAtual,
    // às vezes o backend retorna o próprio objeto cargo
    colab.CargoId,
    colab.CargoID,
    colab.Cargo,
    colab.cargo
  ];
  for (const v of possibilities) {
    if (v !== undefined && v !== null && String(v).trim() !== "") return v;
  }
  return null;
}

// Preencher form ao selecionar colaborador
function carregarFormulario(colab) {
  colaboradorSelecionado = colab;

  // seta o ID (hidden) para controlar insert vs update
  const idHidden = document.getElementById("id_funcionario");
  if (idHidden) idHidden.value = colab.Id || "";

  setIfExists("nm_funcionario", colab.NomeColaborador);
  setIfExists("dt_nascimento", colab.DtNascimento);
  setIfExists("cd_cpf", colab.Cpf);
  setIfExists("cd_rg", colab.Rg);
  setIfExists("dt_cargo", colab.DtAdmissao);
  setIfExists("vl_salario", colab.Salario);
  setIfExists("vl_refeicao", colab.Refeicao);
  setIfExists("vl_alimentacao", colab.Alimentacao);
  setIfExists("vl_inss", colab.Inss);
  setIfExists("vl_fgts", colab.Fgts);
  setIfExists("vl_plano_saude", colab.PlanoSaude);
  setIfExists("vl_transporte", colab.ValeTransporte);

  // Selecionar cargo no combobox — tenta por id primeiro, se não encontrar tenta casar pelo texto
  const selectCargo = document.getElementById("id_cargo");
  if (!selectCargo) return;

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

function setIfExists(elementId, value) {
  const el = document.getElementById(elementId);
  if (el) el.value = (value !== undefined && value !== null) ? value : "";
}

// Limpar form para novo
function novoColaborador() {
  colaboradorSelecionado = null;
  const form = document.getElementById("formColaborador");
  if (form) form.reset();
  const idHidden = document.getElementById("id_funcionario");
  if (idHidden) idHidden.value = ""; // limpa hidden id também
}

// Salvar colaborador + cargo (com verificação de mudança de cargo)
async function salvarColaboradorCargo() {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Token inválido. Faça login novamente.");
    return;
  }

  const idFuncionario = document.getElementById("id_funcionario") ? document.getElementById("id_funcionario").value : "";

  // monta objeto colaborador (incluir id_funcionario quando houver)
  const colaborador = {
    id_funcionario: idFuncionario ? parseInt(idFuncionario) : 0,
    nm_funcionario: document.getElementById("nm_funcionario") ? document.getElementById("nm_funcionario").value : "",
    dt_nascimento: document.getElementById("dt_nascimento") ? document.getElementById("dt_nascimento").value : "",
    cd_cpf: document.getElementById("cd_cpf") ? document.getElementById("cd_cpf").value : "",
    cd_rg: document.getElementById("cd_rg") ? document.getElementById("cd_rg").value : "",
    id_usuario: 3
  };

  const colaborador_cargo = {
    id_funcionario: idFuncionario ? parseInt(idFuncionario) : 0,
    dt_cargo: document.getElementById("dt_cargo") ? document.getElementById("dt_cargo").value : "",
    vl_salario: parseOrNull(document.getElementById("vl_salario") ? document.getElementById("vl_salario").value : null),
    id_usuario: 3,
    vl_transporte: parseOrNull(document.getElementById("vl_transporte") ? document.getElementById("vl_transporte").value : null),
    vl_alimentacao: parseOrNull(document.getElementById("vl_alimentacao") ? document.getElementById("vl_alimentacao").value : null),
    vl_plano_saude: parseOrNull(document.getElementById("vl_plano_saude") ? document.getElementById("vl_plano_saude").value : null),
    vl_refeicao: parseOrNull(document.getElementById("vl_refeicao") ? document.getElementById("vl_refeicao").value : null),
    vl_inss: parseOrNull(document.getElementById("vl_inss") ? document.getElementById("vl_inss").value : null),
    vl_fgts: parseOrNull(document.getElementById("vl_fgts") ? document.getElementById("vl_fgts").value : null),
    dt_desligamento: null,
    id_cargo: parseInt(document.getElementById("id_cargo") ? document.getElementById("id_cargo").value : 0)
  };

  try {
    // Decide endpoint + method conforme idFuncionario e mudança de cargo
    let url = `${api_base}/InserirColaboradorComCargo/`;
    let method = "POST";

    if (idFuncionario && String(idFuncionario).trim() !== "") {
      // já é um update — verifica se houve mudança de cargo
      const cargoAtual = extractCargoIdFromColab(colaboradorSelecionado);
      const cargoSelecionado = colaborador_cargo.id_cargo;

      // Se cargoAtual for nulo/indefinido, assumimos que não há dado para comparar e prosseguimos sem popup
      const houveMudanca = (cargoAtual !== null && cargoAtual !== undefined) && (String(cargoAtual) !== String(cargoSelecionado));

      if (houveMudanca) {
        // mostra popup avisando que ocorrerá mudança de cargo
        const confirme = confirm("Detectamos que o colaborador mudará de cargo. Deseja confirmar a alteração de cargo?");
        if (!confirme) {
          // usuário cancelou → não procede
          return;
        }

        // se mudar de cargo → chama endpoint específico
        url = `${api_base}/InserirColaboradorCargo/`;
          method = "POST";
        json = JSON.stringify(colaborador_cargo );
        // opcionalmente envie o cargo anterior junto ao payload para auditoria
        colaborador_cargo.cargo_anterior_id = cargoAtual;
      } else {
        // alteração normal sem troca de cargo
        url = `${api_base}/AlterarColaboradorComCargo/`;
        method = "POST";
        json = JSON.stringify({ colaborador, colaborador_cargo });
      }
    } else {
      // INSERT
      url = `${api_base}/InserirColaboradorComCargo/`;
      method = "POST";
      json = JSON.stringify({ colaborador, colaborador_cargo });
    }

    const resp = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: json // JSON.stringify({ colaborador, colaborador_cargo })
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
      const form = document.getElementById("formColaborador");
      if (form) form.reset();
      const idHidden = document.getElementById("id_funcionario");
      if (idHidden) idHidden.value = "";
    } else {
      // opcional: atualizar colaboradorSelecionado com novos valores retornados pelo backend (se retornar)
      if (result && result.colaborador) {
        colaboradorSelecionado = result.colaborador;
      }
    }

    // Recarrega grid
    await carregarColaboradores();
  } catch (err) {
    console.error("Erro ao salvar colaborador:", err);
    alert("Erro ao salvar colaborador");
  }
}

function parseOrNull(value) {
  if (value === null || value === undefined || String(value).trim() === "") return null;
  const n = Number(value);
  return isNaN(n) ? null : n;
}

// Histórico de cargos
async function abrirHistorico(idColaborador) {
  const token = localStorage.getItem("token");
  const modal = document.getElementById("historicoModal");
  const tbody = document.getElementById("tbodyHistorico");
  if (!modal || !tbody) return;
  modal.style.display = "block";
  tbody.innerHTML = "<tr><td colspan='4'>Carregando...</td></tr>";

  try {
    const resp = await fetch(`${api_base}/CargosColaborador?id_funcionario=${idColaborador}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!resp.ok) throw new Error(`Status ${resp.status}`);
    const historico = await resp.json();

    tbody.innerHTML = "";
    (historico || []).forEach(cargo => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${cargo.DataCargo || "-"}</td>
        <td>${cargo.Salario != null ? cargo.Salario : "-"}</td>
        <td>${cargo.Cargo || "-"}</td>
        <td>${cargo.DataDesligamento || "-"}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Erro ao carregar histórico:", err);
    tbody.innerHTML = "<tr><td colspan='4'>Erro ao carregar histórico</td></tr>";
  }
}
