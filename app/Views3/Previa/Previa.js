(() => {
  // Simulação dos dados e funções para testes - substituir pelas reais APIs/funções
  const previa = {
    previaPagamentosMesAtual: async () => {
      return [
        {id: 1, descricao: "Pagamento aluguel", fornecedor: "Fornecedor A", vencimento: "2025-08-25", dtPagamento: "", valor: 2500.00},
        {id: 2, descricao: "Compra material", fornecedor: "Fornecedor B", vencimento: "2025-08-10", dtPagamento: "2025-08-12", valor: 1500.00},
        {id: 3, descricao: "Serviços gerais", fornecedor: "Fornecedor C", vencimento: "2025-08-20", dtPagamento: "", valor: 500.00},
      ];
    },
    previaServicosMesAtual: async () => {
      return [
        {id: 1, descricao: "Venda serviço 1", cliente: "Cliente X", data: "2025-08-05", valor: 3500.00, desconto: 100.00},
        {id: 2, descricao: "Venda serviço 2", cliente: "Cliente Y", data: "2025-08-12", valor: 4200.00, desconto: 0},
        {id: 3, descricao: "Venda serviço 3", cliente: "Cliente Z", data: "2025-08-18", valor: 2800.00, desconto: 200.00},
      ];
    },
    previasMedidas: async () => {
      return [{
        ticketMedio: 3500.00,
        valorBruto: 10500.00,
        totalDescontos: 300.00,
        totalLiquido: 10200.00,
        percentual: 2.85
      }];
    },
    baixarPagamento: async (id) => {
      alert(`Pagamento ${id} baixado (simulado).`);
      return true;
    },
    excluirPagamento: async (id) => {
      alert(`Pagamento ${id} excluído (simulado).`);
      return true;
    },
    excluirCredito: async (id) => {
      alert(`Crédito ${id} excluído (simulado).`);
      return true;
    }
  };

  // DOM refs
  const tableDebitoBody = document.querySelector("#tableDebito tbody");
  const tableCreditoBody = document.querySelector("#tableCredito tbody");

  const btnBaixar = document.getElementById("btnBaixarPagamento");
  const btnExcluirPag = document.getElementById("btnExcluirPagamento");
  const btnExcluirCred = document.getElementById("btnExcluirCredito");

  const valorTicket = document.getElementById("valorTicket").querySelector("strong");
  const valorBruto = document.getElementById("valorBruto").querySelector("strong");
  const totalDescontos = document.getElementById("totalDescontos").querySelector("strong");
  const totalLiquido = document.getElementById("totalLiquido").querySelector("strong");
  const percentual = document.getElementById("percentual").querySelector("strong");

  let selectedPagamentoId = null;
  let selectedCreditoId = null;

  function formatCurrency(value) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function clearSelection(tableBody) {
    [...tableBody.querySelectorAll('tr')].forEach(tr => tr.classList.remove('selected'));
  }

  function createRowPagamento(pagamento) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${pagamento.id}</td>
      <td>${pagamento.descricao}</td>
      <td>${pagamento.fornecedor}</td>
      <td>${pagamento.vencimento}</td>
      <td>${pagamento.dtPagamento || '-'}</td>
      <td>${formatCurrency(pagamento.valor)}</td>
    `;
    tr.addEventListener('click', () => {
      clearSelection(tableDebitoBody);
      tr.classList.add('selected');
      selectedPagamentoId = pagamento.id;

      // Mostrar/ocultar botões conforme pagamento baixado ou não
      if (!pagamento.dtPagamento) {
        btnBaixar.disabled = false;
        btnExcluirPag.disabled = false;
      } else {
        btnBaixar.disabled = true;
        btnExcluirPag.disabled = true;
      }
    });
    return tr;
  }

  function createRowCredito(credito) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${credito.id}</td>
      <td>${credito.descricao}</td>
      <td>${credito.cliente}</td>
      <td>${credito.data}</td>
      <td>${formatCurrency(credito.valor)}</td>
      <td>${formatCurrency(credito.desconto)}</td>
    `;
    tr.addEventListener('click', () => {
      clearSelection(tableCreditoBody);
      tr.classList.add('selected');
      selectedCreditoId = credito.id;
      btnExcluirCred.disabled = false;
    });
    return tr;
  }

  async function carregarPagamentos() {
    const pagamentos = await previa.previaPagamentosMesAtual();
    tableDebitoBody.innerHTML = '';
    pagamentos.forEach(p => tableDebitoBody.appendChild(createRowPagamento(p)));
    selectedPagamentoId = null;
    btnBaixar.disabled = true;
    btnExcluirPag.disabled = true;
  }

  async function carregarCreditos() {
    const creditos = await previa.previaServicosMesAtual();
    tableCreditoBody.innerHTML = '';
    creditos.forEach(c => tableCreditoBody.appendChild(createRowCredito(c)));
    selectedCreditoId = null;
    btnExcluirCred.disabled = true;
  }

  async function carregarMedidas() {
    const medidas = await previa.previasMedidas();
    if(medidas.length) {
      const m = medidas[0];
      valorTicket.textContent = formatCurrency(m.ticketMedio);
      valorBruto.textContent = formatCurrency(m.valorBruto);
      totalDescontos.textContent = formatCurrency(m.totalDescontos);
      totalLiquido.textContent = formatCurrency(m.totalLiquido);
      percentual.textContent = m.percentual.toFixed(2) + '%';
    }
  }

  btnBaixar.addEventListener('click', async () => {
    if (!selectedPagamentoId) return;
    const pagamentoRow = [...tableDebitoBody.children].find(tr => tr.classList.contains('selected'));
    const descricao = pagamentoRow.children[1].textContent;
    const valor = pagamentoRow.children[5].textContent;
    const vencimento = pagamentoRow.children[3].textContent;
    if (confirm(`Deseja Realizar a Baixa Desse Pagamento?\n${descricao} - ${valor}\nVencimento: ${vencimento}`)) {
      const sucesso = await previa.baixarPagamento(selectedPagamentoId);
      if (sucesso) {
        alert('Pagamento baixado com sucesso!');
        await carregarPagamentos();
      }
    }
  });

  btnExcluirPag.addEventListener('click', async () => {
    if (!selectedPagamentoId) return;
    const pagamentoRow = [...tableDebitoBody.children].find(tr => tr.classList.contains('selected'));
    const descricao = pagamentoRow.children[1].textContent;
    const valor = pagamentoRow.children[5].textContent;
    const vencimento = pagamentoRow.children[3].textContent;
    if (confirm(`Deseja Excluir esse Pagamento?\n${descricao} - ${valor}\nVencimento: ${vencimento}`)) {
      const sucesso = await previa.excluirPagamento(selectedPagamentoId);
      if (sucesso) {
        alert('Pagamento excluído com sucesso!');
        await carregarPagamentos();
      }
    }
  });

  btnExcluirCred.addEventListener('click', async () => {
    if (!selectedCreditoId) return;
    const creditoRow = [...tableCreditoBody.children].find(tr => tr.classList.contains('selected'));
    const descricao = creditoRow.children[1].textContent;
    const valor = creditoRow.children[4].textContent;
    const desconto = creditoRow.children[5].textContent;
    if (confirm(`Deseja Excluir esse Crédito?\n${descricao} - ${valor}\nDesconto: ${desconto}`)) {
      const sucesso = await previa.excluirCredito(selectedCreditoId);
      if (sucesso) {
        alert('Crédito excluído com sucesso!');
        await carregarCreditos();
      }
    }
  });

  async function init() {
    await carregarPagamentos();
    await carregarCreditos();
    await carregarMedidas();
  }

  window.addEventListener('DOMContentLoaded', init);

})();
