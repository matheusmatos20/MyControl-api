// ServicoCliente.js
let tokenGlobal = null;

const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
const AUTH_BASE = window.AUTH_BASE_URL || API_BASE;
const buildApiUrl = window.buildApiUrl || (path => `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`);
const buildAuthUrl = window.buildAuthUrl || (path => `${AUTH_BASE}${path.startsWith('/') ? path : `/${path}`}`);
const COLUNAS_SERVICO_CLIENTE = ["ID", "Cliente", "Serviço", "Valor", "Desconto"];

function setComboState(combo, placeholder, disabled = false) {
  if (!combo) return;
  combo.innerHTML = `<option value="">${placeholder}</option>`;
  combo.disabled = !!disabled;
}

function renderGridMensagem(mensagem) {
  const tbody = document.querySelector("#grid tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="5" class="mensagem-vazia">${mensagem}</td></tr>`;
}

// -----------------------------
// Helpers
// -----------------------------
function extrairId(valor) {
  // Recebe "1", "1 - Nome" ou  " 1 - Nome" e retorna 1 (number) ou null
  if (valor === null || valor === undefined) return null;
  const s = String(valor).trim();
  if (!s) return null;
  const m = s.match(/^(\d+)/);
  return m ? parseInt(m[1], 10) : null;
}

function hojeISO() {
  const hoje = new Date();
  return hoje.toISOString().split("T")[0]; // yyyy-mm-dd
}

async function obterToken() {
  // ajusta conforme seu endpoint de auth
  const url = buildAuthUrl('/token');
  const formData = new URLSearchParams();
  formData.append("username", "usuario");
  formData.append("password", "1234");
  formData.append("grant_type", "password");

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData
    });
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    tokenGlobal = data.access_token;
    return tokenGlobal;
  } catch (err) {
    console.error("Erro ao obter token:", err);
    alert("Falha na autenticação (verifique backend).");
    return null;
  }
}

// -----------------------------
// Carregar combos (Clientes e Serviços)
// -----------------------------
async function carregarCombos() {
  // if (!tokenGlobal) await obterToken();
  // if (!tokenGlobal) return;
  if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");
  try {
    // Clientes
    const respClientes = await fetch(buildApiUrl('/Clientes'), {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });
    if (!respClientes.ok) throw new Error("Erro ao buscar clientes");
    const clientes = await respClientes.json();

    const cmbCliente = document.getElementById("cliente");
    if (!clientes.length) {
      setComboState(cmbCliente, "Cadastre um cliente antes.", true);
    } else {
      cmbCliente.disabled = false;
      cmbCliente.innerHTML = `<option value="">Selecione...</option>`;
      clientes.forEach(c => {
        const id = c.id_cliente ?? c.id ?? c.Id ?? c.IdCliente;
        const nome = c.Nome ?? c.nome ?? c.nome_cliente ?? "";
        const opt = document.createElement("option");
        opt.value = String(id);
        opt.textContent = `${id} - ${nome}`;
        cmbCliente.appendChild(opt);
      });
    }

    const respServ = await fetch(buildApiUrl('/Servicos'), {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });
    if (!respServ.ok) throw new Error("Erro ao buscar serviços");
    const servicos = await respServ.json();

    const cmbServico = document.getElementById("servico");
    if (!servicos.length) {
      setComboState(cmbServico, "Cadastre um serviço antes.", true);
    } else {
      cmbServico.disabled = false;
      cmbServico.innerHTML = `<option value="">Selecione...</option>`;
      servicos.forEach(s => {
        const id = s.ID;
        const nome = s.Servico;
        const opt = document.createElement("option");
        opt.value = String(id);
        opt.textContent = `${id} - ${nome}`;
        cmbServico.appendChild(opt);
      });
    }

    //   const cmbServico = document.getElementById("servico");
    // cmbServico.innerHTML = `<option value="">Selecione...</option>`;
    // servicos.forEach(s => {
    //   const opt = document.createElement("option");
    //   opt.value = s.ID;
    //   opt.textContent = `${s.ID} - ${s.Servico}`;
    //   cmbServico.appendChild(opt);
    // });


  } catch (err) {
    console.error(err);
    setComboState(document.getElementById("cliente"), "Não foi possível carregar clientes.", true);
    setComboState(document.getElementById("servico"), "Não foi possível carregar serviços.", true);
  }
}

// -----------------------------
// Carregar grid de serviços contratados
// -----------------------------
async function carregarGrid() {
  // if (!tokenGlobal) await obterToken();
  // if (!tokenGlobal) return;
  if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");
  try {
    const resp = await fetch(buildApiUrl('/ServicosCliente'), {
      headers: { Authorization: `Bearer ${tokenGlobal}` }
    });
    if (!resp.ok) throw new Error("Erro ao buscar serviços contratados");
    const dados = await resp.json();

    const tbody = document.querySelector("#grid tbody");
    tbody.innerHTML = "";
    if (!dados.length) {
      renderGridMensagem("Nenhum serviço vendido até o momento.");
      return;
    }

    dados.forEach(d => {
      const row = document.createElement("tr");
      // campos esperados: id_servico_cliente, Cliente, Servico, vl_servico, vl_desconto
      row.innerHTML = `
        <td>${d.Id ?? d.id ?? ""}</td>
        <td>${d.Cliente ?? d.cliente ?? ""}</td>
        <td>${d.Servico ?? d.servico ?? ""}</td>
        <td>${d.Valor ?? d.valor ?? ""}</td>
        <td>${d.Desconto ?? d.desconto ?? ""}</td>
      `;
      row.addEventListener("click", () => preencherCampos(row));
      tbody.appendChild(row);
    });

  } catch (err) {
    console.error(err);
    renderGridMensagem("Não foi possível carregar a lista agora.");
  }
}

// -----------------------------
// Preencher campos ao clicar no grid
// -----------------------------
function preencherCampos(row) {
  const cells = row.cells;
  // cells[1] = paciente nome, cells[2] = serviço nome
  const pacienteNome = cells[1]?.innerText?.trim() ?? "";
  const servicoNome = cells[2]?.innerText?.trim() ?? "";

  // Seleciona cliente procurando pelo texto da option
  const clienteOpt = Array.from(document.getElementById("cliente").options)
    .find(o => o.textContent.includes(pacienteNome));
  if (clienteOpt) document.getElementById("cliente").value = clienteOpt.value;

  const servicoOpt = Array.from(document.getElementById("servico").options)
    .find(o => o.textContent.includes(servicoNome));
  if (servicoOpt) document.getElementById("servico").value = servicoOpt.value;

  document.getElementById("valor").value = cells[3]?.innerText ?? "";
  document.getElementById("desconto").value = cells[4]?.innerText ?? "";
}

// -----------------------------
// Salvar serviço contratado
// -----------------------------
async function salvarServico() {
  // if (!tokenGlobal) await obterToken();
  // if (!tokenGlobal) return;

  if (!await validarToken()) {
        return
    }
  tokenGlobal =localStorage.getItem("token");

  const selectCliente = document.getElementById("cliente");
  const selectServico = document.getElementById("servico");
  if (selectCliente?.disabled || selectServico?.disabled) {
    alert("Cadastre clientes e serviços antes de registrar vendas.");
    return;
  }

  const clienteRaw = selectCliente.value;
  const servicoRaw = selectServico.value;
  const valorRaw = document.getElementById("valor").value;
  const descontoRaw = document.getElementById("desconto").value;

  const id_cliente = extrairId(clienteRaw);
  const id_servico = extrairId(servicoRaw);

  // aceitar vírgula como separador decimal
  const valor = valorRaw ? parseFloat(String(valorRaw).replace(",", ".")) : NaN;
  const desconto = descontoRaw ? parseFloat(String(descontoRaw).replace(",", ".")) : 0;

  if (!id_cliente || !id_servico || isNaN(valor)) {
    alert("Preencha Cliente, Serviço e Valor corretamente!");
    return;
  }

  const payload = {
    id_servico: Number(id_servico),
    id_cliente: Number(id_cliente),
    vl_servico: Number(valor),
    vl_desconto: Number(isNaN(desconto) ? 0 : desconto),
    dt_servico: hojeISO(),
    id_usuario: 3 // temporário conforme combinado
  };

  try {
    const resp = await fetch(buildApiUrl('/InserirServicoCliente'), {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${tokenGlobal}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error(txt || "Erro ao salvar serviço");
    }

    alert("Serviço salvo com sucesso!");
    document.getElementById("form-servico").reset();
    carregarGrid();

  } catch (err) {
    console.error(err);
    alert("Erro ao salvar serviço: " + (err.message || err));
  }
}

// -----------------------------
// Inicialização
// -----------------------------
document.addEventListener("DOMContentLoaded", async () => {
  // Se o HTML usa onclick="salvarServico()" você pode manter — 
  // aqui também adiciono listener só por garantia
  const btnSalvar = document.querySelector(".btn-primary");
  // if (btnSalvar) btnSalvar.addEventListener("click", salvarServico);

  await carregarCombos();
  await carregarGrid();
});

