document.addEventListener('DOMContentLoaded', () => {
  const chkPago = document.getElementById('chkPago');
  const groupDtPagamento = document.getElementById('groupDtPagamento');
  const txtValor = document.getElementById('txtValor');
  const form = document.getElementById('formPagamento');
  const cmbFornecedores = document.getElementById('cmbFornecedores');
  const cmbFormaPagamento = document.getElementById('cmbFormaPagamento');

  const API_BASE = 'http://localhost:3000';

  console.log("Script carregado");

  chkPago.addEventListener('change', () => {
    groupDtPagamento.classList.toggle('hidden', !chkPago.checked);
  });

  txtValor.addEventListener('keypress', (e) => {
    const char = String.fromCharCode(e.which);
    if (!/[0-9,]/.test(char) && !e.ctrlKey && !e.metaKey && e.key !== 'Backspace') {
      e.preventDefault();
    }
  });

  async function carregarSelects() {
    try {
      const [respFornecedores, respFormas] = await Promise.all([
        fetch(`${API_BASE}/fornecedores`),
        fetch(`${API_BASE}/formasPagamento`)
      ]);

      const fornecedores = await respFornecedores.json();
      const formasPagamento = await respFormas.json();

      console.log("Fornecedores recebidos:", fornecedores);

      if (!Array.isArray(fornecedores) || fornecedores.length === 0) {
        alert("Nenhum fornecedor retornado da API");
        return;
      }

      fornecedores.forEach(f => {
        const option = document.createElement('option');
        option.value = f.id;
        option.textContent = f.nome;
        cmbFornecedores.appendChild(option);
      });

      formasPagamento.forEach(fp => {
        const option = document.createElement('option');
        option.value = fp.id;
        option.textContent = fp.descricao;
        cmbFormaPagamento.appendChild(option);
      });

    } catch (error) {
      alert('Erro ao carregar dados: ' + error.message);
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const pagamento = {
      descricao: document.getElementById('txtPagamento').value,
      dataVencimento: document.getElementById('dtpVencimento').value,
      pago: chkPago.checked,
      dataPagamento: chkPago.checked ? document.getElementById('dtpPagamento').value : null,
      fornecedorId: cmbFornecedores.value,
      formaPagamentoId: cmbFormaPagamento.value,
      valor: parseFloat(txtValor.value.replace(',', '.'))
    };

    try {
      const response = await fetch(`${API_BASE}/pagamentos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pagamento)
      });

      if (response.ok) {
        alert('Pagamento lançado com sucesso!');
        form.reset();
        groupDtPagamento.classList.add('hidden');
      } else {
        alert('Erro ao salvar pagamento.');
      }
    } catch (error) {
      alert('Erro ao enviar: ' + error.message);
    }
  });

  carregarSelects();
});
