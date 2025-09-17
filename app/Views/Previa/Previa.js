(() => {
  const API_BASE = "http://127.0.0.1:8000"; // ajuste se necessário
  let tokenGlobal = null;
  let selectedPagamentoId = null;
  let selectedCreditoId = null;

  // -------------------------
 

  // -------------------------
  function formatCurrency(value) {
    return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function clearSelection(tableBody) {
    [...tableBody.querySelectorAll('tr')].forEach(tr => tr.classList.remove('selected'));
  }

  // -------------------------
  function createRowDebito(pagamento, tableDebitoBody, btnBaixar, btnExcluirPag) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${pagamento.Id}</td>
      <td>${pagamento.Descricao}</td>
      <td>${pagamento.Fornecedor}</td>
      <td>${pagamento.DtVencimento}</td>
      <td>${pagamento.FormaPagamento}</td>
      <td>${formatCurrency(pagamento.Valor)}</td>
      <td>${pagamento.Status}</td>
    `;
    tr.addEventListener('click', () => {
      clearSelection(tableDebitoBody);
      tr.classList.add('selected');
      selectedPagamentoId = pagamento.Id;
      console.log("Pagamento selecionado:", selectedPagamentoId);

      btnBaixar.hidden = pagamento.Status !== "Pendente";
      btnExcluirPag.hidden = false;
    });
    return tr;
  }

  function createRowCredito(credito, tableCreditoBody, btnExcluirCred) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${credito.Id}</td>
      <td>${credito.DtVencimento}</td>
      <td>${credito.Cliente}</td>
      <td>${credito.Servico}</td>
      <td>${formatCurrency(credito.Valor)}</td>
      <td>${formatCurrency(credito.Desconto)}</td>
      <td>${formatCurrency(credito.VlLiquido)}</td>
    `;
    tr.addEventListener('click', () => {
      clearSelection(tableCreditoBody);
      tr.classList.add('selected');
      selectedCreditoId = credito.Id;
      console.log("Crédito selecionado:", selectedCreditoId);
      btnExcluirCred.hidden = false;
    });
    return tr;
  }

  // -------------------------
  async function carregarPagamentos(tableDebitoBody, btnBaixar, btnExcluirPag) {
    if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");

    try {
      const resp = await fetch(`${API_BASE}/RetornaDebito`, {
        headers: { 'Authorization': `Bearer ${tokenGlobal}` }
      });

      if (!resp.ok) {
        console.error("Erro ao carregar pagamentos", await resp.text());
        return;
      }

      const pagamentos = await resp.json();
      console.log("Pagamentos recebidos:", pagamentos);

      tableDebitoBody.innerHTML = '';
      pagamentos.forEach(p => tableDebitoBody.appendChild(createRowDebito(p, tableDebitoBody, btnBaixar, btnExcluirPag)));

      selectedPagamentoId = null;
      btnBaixar.hidden = true;
      btnExcluirPag.hidden = true;
    } catch (err) {
      console.error("Falha ao carregar pagamentos:", err);
    }
  }

  async function carregarCreditos(tableCreditoBody, btnExcluirCred) {
if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");
    try {
      const resp = await fetch(`${API_BASE}/RetornaCredito`, {
        headers: { 'Authorization': `Bearer ${tokenGlobal}` }
      });

      if (!resp.ok) {
        console.error("Erro ao carregar créditos", await resp.text());
        return;
      }

      const creditos = await resp.json();
      console.log("Créditos recebidos:", creditos);

      tableCreditoBody.innerHTML = '';
      creditos.forEach(c => tableCreditoBody.appendChild(createRowCredito(c, tableCreditoBody, btnExcluirCred)));

      selectedCreditoId = null;
      btnExcluirCred.hidden = true;
    } catch (err) {
      console.error("Falha ao carregar créditos:", err);
    }
  }

  async function carregarIndicadores(lblValorTicket, lblValorBruto, lblTotalDescont, lblTotalLiq, lblPerc) {
if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");
    try {
      const resp = await fetch(`${API_BASE}/RetornaCredito`, {
        headers: { 'Authorization': `Bearer ${tokenGlobal}` }
      });

      if (!resp.ok) {
        console.error("Erro ao carregar indicadores", await resp.text());
        return;
      }

      const creditos = await resp.json();
      console.log("Indicadores dos créditos:", creditos);

      if (creditos.length) {
        const valorBruto = creditos.reduce((acc, c) => acc + c.Valor, 0);
        const totalDescontos = creditos.reduce((acc, c) => acc + c.Desconto, 0);
        const totalLiquido = creditos.reduce((acc, c) => acc + c.VlLiquido, 0);
        const ticketMedio = totalLiquido / creditos.length;
        const percentual = valorBruto > 0 ? ((totalLiquido - valorBruto) / valorBruto) * 100 : 0;

        lblValorTicket.textContent = formatCurrency(ticketMedio);
        lblValorBruto.textContent = formatCurrency(valorBruto);
        lblTotalDescont.textContent = formatCurrency(totalDescontos);
        lblTotalLiq.textContent = formatCurrency(totalLiquido);
        lblPerc.textContent = percentual.toFixed(2) + "%";
      }
    } catch (err) {
      console.error("Falha ao carregar indicadores:", err);
    }
  }

  // -------------------------
  async function init() {
    console.log("Inicializando aplicativo Prévia Mensal...");
    const tableDebitoBody = document.querySelector("#dgvDebito tbody");
    const tableCreditoBody = document.querySelector("#dgvCredito tbody");
    const btnBaixar = document.getElementById("btnBaixarPagamento");
    const btnExcluirPag = document.getElementById("btnExcluirPagamento");
    const btnExcluirCred = document.getElementById("btnExcluirCredito");
    const lblValorTicket = document.getElementById("lblValorTicket");
    const lblValorBruto = document.getElementById("lblValorBruto");
    const lblTotalDescont = document.getElementById("lblTotalDescont");
    const lblTotalLiq = document.getElementById("lblTotalLiq");
    const lblPerc = document.getElementById("lblPerc");

    // Garantir que os elementos existem
    if (!tableDebitoBody || !tableCreditoBody || !btnBaixar || !btnExcluirPag || !btnExcluirCred) {
      console.error("Algum elemento não foi encontrado no DOM.");
      return;
    }

    // Botões ocultos por padrão
    btnBaixar.hidden = true;
    btnExcluirPag.hidden = true;
    btnExcluirCred.hidden = true;

    btnBaixar.addEventListener('click', async () => {
      if (!selectedPagamentoId) return;
      if (confirm("Deseja realizar a baixa desse pagamento?")) {
        await fetch(`${API_BASE}/BaixarDebito/${selectedPagamentoId}`, {
          method: "POST",
          headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });
        await carregarPagamentos(tableDebitoBody, btnBaixar, btnExcluirPag);
      }
    });

    btnExcluirPag.addEventListener('click', async () => {
      if (!selectedPagamentoId) return;
      if (confirm("Deseja excluir esse pagamento?")) {
        await fetch(`${API_BASE}/ExcluirDebito/${selectedPagamentoId}`, {
          method: "DELETE",
          headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });
        await carregarPagamentos(tableDebitoBody, btnBaixar, btnExcluirPag);
      }
    });

    btnExcluirCred.addEventListener('click', async () => {
      if (!selectedCreditoId) return;
      if (confirm("Deseja excluir esse crédito?")) {
        await fetch(`${API_BASE}/ExcluirCredito/${selectedCreditoId}`, {
          method: "DELETE",
          headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });
        await carregarCreditos(tableCreditoBody, btnExcluirCred);
        await carregarIndicadores(lblValorTicket, lblValorBruto, lblTotalDescont, lblTotalLiq, lblPerc);
      }
    });

    await carregarCreditos(tableCreditoBody, btnExcluirCred);
    await carregarPagamentos(tableDebitoBody, btnBaixar, btnExcluirPag);
    await carregarIndicadores(lblValorTicket, lblValorBruto, lblTotalDescont, lblTotalLiq, lblPerc);
  }

  window.addEventListener('DOMContentLoaded', init);

})();
