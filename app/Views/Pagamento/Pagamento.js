document.addEventListener('DOMContentLoaded', () => {
  const chkPago = document.getElementById('chkPago');
  const groupDtPagamento = document.getElementById('groupDtPagamento');
  const txtValor = document.getElementById('txtValor');
  const form = document.getElementById('formPagamento');
  const cmbFornecedores = document.getElementById('cmbFornecedores');
  const cmbFormaPagamento = document.getElementById('cmbFormaPagamento');
  const tabelaBody = document.querySelector('#dgvPagamentos tbody');

  const cmbTipoPagamento = document.getElementById('cmbTipoPagamento');
  const parceladoFields = document.getElementById('parceladoFields');
  const lblValor = document.getElementById('lblValor');
  const txtParcelas = document.getElementById('txtParcelas');
  const txtJuros = document.getElementById('txtJuros');
  const dtPrimeiraParcela = document.getElementById('dtPrimeiraParcela');
  const grupoPago = chkPago ? chkPago.closest('.form-group') : null;

  const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
  let token = null;

  function getTipoPagamento() {
    if (!cmbTipoPagamento) {
      return 'avista';
    }
    return cmbTipoPagamento.value || 'avista';
  }

  function atualizarModoPagamento() {
    const tipo = getTipoPagamento();
    const isParcelado = tipo === 'parcelado';

    if (parceladoFields) {
      parceladoFields.classList.toggle('hidden', !isParcelado);
    }

    if (grupoPago) {
      grupoPago.classList.toggle('hidden', isParcelado);
    }

    if (isParcelado) {
      chkPago.checked = false;
      if (groupDtPagamento) {
        groupDtPagamento.classList.add('hidden');
      }
      if (lblValor) {
        lblValor.textContent = 'Valor Total';
      }
    } else {
      if (lblValor) {
        lblValor.textContent = 'Valor';
      }
      if (groupDtPagamento) {
        groupDtPagamento.classList.toggle('hidden', !chkPago.checked);
      }
    }
  }

  function normalizarValorMonetario(valor) {
    if (typeof valor !== 'string') {
      return Number.NaN;
    }
    const somenteNumeros = valor.replace(/\./g, '').replace(',', '.');
    const parsed = parseFloat(somenteNumeros);
    return Number.isFinite(parsed) ? parsed : Number.NaN;
  }

  chkPago.addEventListener('change', () => {
    if (getTipoPagamento() === 'parcelado') {
      chkPago.checked = false;
      return;
    }
    groupDtPagamento.classList.toggle('hidden', !chkPago.checked);
  });

  txtValor.addEventListener('keypress', (e) => {
    const char = String.fromCharCode(e.which || e.keyCode);
    if (!/[0-9,]/.test(char) && !e.ctrlKey && !e.metaKey && e.key !== 'Backspace') {
      e.preventDefault();
    }
  });

  if (cmbTipoPagamento) {
    cmbTipoPagamento.addEventListener('change', atualizarModoPagamento);
  }

  async function carregarSelects() {
    try {
      cmbFornecedores.innerHTML = '<option value="">Selecione</option>';
      const respFornecedores = await fetch(`${API_BASE}/RetornaFornecedores`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const fornecedores = await respFornecedores.json();

      fornecedores.forEach(f => {
        const option = document.createElement('option');
        let value = null;
        let text = '';

        if (f.id_fornecedor != null) {
          value = f.id_fornecedor;
          text = `${f.id_fornecedor} - ${f.nm_fantasia ?? f.NM_FANTASIA ?? ''}`.trim();
        } else if (f.ID_FORNECEDOR != null) {
          value = f.ID_FORNECEDOR;
          text = `${f.ID_FORNECEDOR} - ${f.NM_FANTASIA ?? f.nm_fantasia ?? ''}`.trim();
        } else if (f.Fornecedor) {
          const partes = String(f.Fornecedor).split(' - ');
          value = partes[0];
          text = f.Fornecedor;
        }

        if (!value) {
          return;
        }

        option.value = value;
        option.textContent = text || String(value);
        cmbFornecedores.appendChild(option);
      });

      cmbFormaPagamento.innerHTML = '<option value="">Selecione</option>';
      const formasPagamento = [
        { id: 1, descricao: 'Boleto' },
        { id: 2, descricao: 'Cart?o de Cr?dito' },
        { id: 3, descricao: 'Cart?o de D?bito' },
        { id: 4, descricao: 'Pix' },
        { id: 5, descricao: 'Transfer?ncia Entre Contas' }
      ];

      formasPagamento.forEach(fp => {
        const option = document.createElement('option');
        option.value = fp.id;
        option.textContent = `${fp.id} - ${fp.descricao}`;
        cmbFormaPagamento.appendChild(option);
      });
    } catch (error) {
      alert('Erro ao carregar fornecedores: ' + error.message);
    }
  }

  async function carregarGrid() {
    tabelaBody.innerHTML = '';
    try {
      const response = await fetch(`${API_BASE}/ListarDebitos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const pagamentos = await response.json();

      pagamentos.forEach(pg => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${pg.ID}</td>
          <td>${pg.Descricao}</td>
          <td>${pg.Fornecedor}</td>
          <td>${pg.Vencimento}</td>
          <td>${pg.Valor}</td>
          <td>${pg.FormaPagamento}</td>
          <td>${pg.StatusPagamento}</td>
          <td>
            <button class="btn-delete" data-id="${pg.ID}">Excluir</button>
            ${pg.StatusPagamento !== 'Pago'
              ? `<button class="btn-primary" data-id="${pg.ID}">Baixar</button>`
              : ''}
          </td>
        `;
        tabelaBody.appendChild(tr);
      });

      document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.dataset.id;
          if (!confirm('Deseja realmente excluir este pagamento?')) {
            return;
          }
          try {
            const resp = await fetch(`${API_BASE}/ExcluirDebito/${id}`, {
              method: 'DELETE',
              headers: { Authorization: `Bearer ${token}` }
            });

            if (!resp.ok) {
              const err = await resp.json().catch(() => ({}));
              throw new Error(err.detail || 'Erro ao excluir pagamento');
            }

            alert('Pagamento exclu?do com sucesso!');
            await carregarGrid();
          } catch (error) {
            alert('Erro ao excluir: ' + error.message);
          }
        });
      });

      document.querySelectorAll('#dgvPagamentos .btn-primary').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id = btn.dataset.id;
          if (!confirm('Deseja realmente baixar este pagamento?')) {
            return;
          }
          try {
            const resp = await fetch(`${API_BASE}/BaixarDebito?id_pagamento=${id}&id_usuario=3`, {
              method: 'POST',
              headers: { Authorization: `Bearer ${token}` }
            });

            if (!resp.ok) {
              const err = await resp.json().catch(() => ({}));
              throw new Error(err.detail || 'Erro ao baixar pagamento');
            }

            alert('Pagamento baixado com sucesso!');
            carregarGrid();
          } catch (error) {
            alert('Erro ao baixar: ' + error.message);
          }
        });
      });
    } catch (error) {
      alert('Erro ao carregar pagamentos: ' + error.message);
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const tipoPagamento = getTipoPagamento();

    if (tipoPagamento === 'parcelado') {
      const numeroParcelas = parseInt(txtParcelas.value, 10);
      const valorTotal = normalizarValorMonetario(txtValor.value);
      const jurosPercentual = txtJuros.value ? parseFloat(String(txtJuros.value).replace(',', '.')) : 0;
      const primeiraParcela = dtPrimeiraParcela.value;
      const idFormaPagamento = parseInt(cmbFormaPagamento.value, 10);
      const idFornecedor = parseInt(cmbFornecedores.value, 10);

      if (!valorTotal || Number.isNaN(valorTotal) || valorTotal <= 0) {
        alert('Informe um valor total v?lido para o parcelamento.');
        txtValor.focus();
        return;
      }

      if (!numeroParcelas || numeroParcelas < 2) {
        alert('Informe o n?mero de parcelas (m?nimo 2).');
        txtParcelas.focus();
        return;
      }

      if (!primeiraParcela) {
        alert('Informe a data da primeira parcela.');
        dtPrimeiraParcela.focus();
        return;
      }

      if (!idFormaPagamento) {
        alert('Selecione a forma de pagamento que ser? utilizada nas parcelas.');
        cmbFormaPagamento.focus();
        return;
      }

      try {
        const payload = {
          descricao: document.getElementById('txtPagamento').value,
          id_fornecedor: Number.isNaN(idFornecedor) ? null : idFornecedor,
          id_usuario: 3,
          valor_total: valorTotal,
          numero_parcelas: numeroParcelas,
          juros_percentual: Number.isNaN(jurosPercentual) ? 0 : jurosPercentual,
          data_primeira_parcela: primeiraParcela,
          id_forma_pagamento: idFormaPagamento
        };

        const response = await fetch(`${API_BASE}/pagamentos/parcelado`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.detail || 'Erro ao criar parcelamento');
        }

        alert('Parcelamento criado com sucesso!');
        form.reset();
        atualizarModoPagamento();
        carregarGrid();
      } catch (error) {
        alert('Erro ao salvar parcelamento: ' + error.message);
      }
      return;
    }

    const pagamento = {
      ds_pagamento: document.getElementById('txtPagamento').value,
      dt_pagamento: chkPago.checked ? document.getElementById('dtpPagamento').value : null,
      dt_vencimento: document.getElementById('dtpVencimento').value,
      id_fornecedor: parseInt(cmbFornecedores.value, 10),
      vl_pagamento: txtValor.value,
      id_forma_pagamento: parseInt(cmbFormaPagamento.value, 10),
      id_usuario: 3
    };

    try {
      const response = await fetch(`${API_BASE}/InserirDebito`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(pagamento)
      });

      if (response.ok) {
        alert('Pagamento lan?ado com sucesso!');
        form.reset();
        groupDtPagamento.classList.add('hidden');
        atualizarModoPagamento();
        carregarGrid();
      } else {
        const err = await response.json().catch(() => ({}));
        alert('Erro ao salvar pagamento: ' + (err.detail || response.status));
      }
    } catch (error) {
      alert('Erro ao enviar: ' + error.message);
    }
  });

  (async () => {
    if (!await validarToken()) {
      return;
    }
    token = localStorage.getItem('token');
    if (!token) {
      return;
    }
    atualizarModoPagamento();
    await carregarSelects();
    await carregarGrid();
  })();
});
