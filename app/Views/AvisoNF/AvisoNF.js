(() => {
  const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
  const form = document.getElementById("formAvisoNF");
  const resultado = document.getElementById("resultado");
  const inputValor = document.getElementById("valorNF");

  const onlyDigits = (value) => (value || "").replace(/\D/g, "");

  const formatCurrency = (value) => {
    const number = Number(value);
    if (Number.isNaN(number)) {
      return value;
    }
    return number.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  inputValor.addEventListener('blur', () => {
    const raw = inputValor.value.trim();
    if (!raw) return;
    const normalized = raw.replace(/\./g, '').replace(',', '.');
    const number = Number(normalized);
    if (!Number.isNaN(number)) {
      inputValor.value = number.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    }
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const payload = {
      cnpj_fornecedor: document.getElementById('cnpjFornecedor').value.trim(),
      cnpj_empresa: document.getElementById('cnpjEmpresa').value.trim(),
      numero_nf: document.getElementById('numeroNF').value.trim(),
      serie_nf: document.getElementById('serieNF').value.trim(),
      chave_nf: document.getElementById('chaveNF').value.trim() || null,
      data_emissao: document.getElementById('dataEmissao').value,
      data_vencimento: document.getElementById('dataVencimento').value,
      observacao: document.getElementById('observacao').value.trim() || null,
    };

    const valorBruto = inputValor.value.trim();
    if (!valorBruto) {
      alert('Informe o valor da nota fiscal.');
      return;
    }
    payload.valor = valorBruto.replace(/\./g, '').replace(',', '.');
    const valorNumerico = Number(payload.valor);
    if (Number.isNaN(valorNumerico) || valorNumerico <= 0) {
      alert('Valor da nota fiscal inválido.');
      return;
    }

    const fornecedorDigits = onlyDigits(payload.cnpj_fornecedor);
    if (fornecedorDigits.length !== 14) {
      alert('CNPJ do fornecedor deve conter 14 dígitos.');
      return;
    }

    const empresaDigits = onlyDigits(payload.cnpj_empresa);
    if (empresaDigits.length !== 14) {
      alert('CNPJ da empresa deve conter 14 dígitos.');
      return;
    }

    if (!payload.numero_nf) {
      alert('Informe o número da nota fiscal.');
      return;
    }

    if (!payload.serie_nf) {
      alert('Informe a série da nota fiscal.');
      return;
    }

    if (!payload.data_emissao) {
      alert('Informe a data de emissão.');
      return;
    }

    if (!payload.data_vencimento) {
      alert('Informe a data de vencimento.');
      return;
    }

    if (payload.chave_nf) {
      const chaveDigits = onlyDigits(payload.chave_nf);
      if (chaveDigits.length !== 44) {
        alert('A chave de acesso deve conter 44 dígitos.');
        return;
      }
      payload.chave_nf = chaveDigits;
    }

    try {
      const response = await fetch(`${API_BASE}/AvisoNotaFiscal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || 'Falha ao registrar o aviso.');
      }

      form.reset();
      resultado.classList.remove('hidden', 'sucesso', 'alerta', 'erro');
      const emailSucesso = Boolean(data.email_enviado);
      resultado.classList.add(emailSucesso ? 'sucesso' : 'alerta');

      const emailStatus = emailSucesso
        ? '<p class=\"status-message success\">Notificação enviada por e-mail.</p>'
        : '<p class=\"status-message warning\">Não foi possível enviar o e-mail de notificação.</p>';
      resultado.innerHTML = `
        <strong>${data.mensagem}</strong>
        <ul>
          <li>Fornecedor: ${data.dados?.fornecedor ?? '--'}</li>
          <li>Empresa: ${data.dados?.empresa ?? '--'}</li>
          <li>Valor: ${formatCurrency(data.dados?.valor ?? valorNumerico)}</li>
          <li>Data de emissão: ${data.dados?.data_emissao ?? payload.data_emissao}</li>
          <li>Vencimento: ${data.dados?.data_vencimento ?? payload.data_vencimento}</li>
          <li>Número: ${data.dados?.numero_nf ?? payload.numero_nf}</li>
          <li>Série: ${data.dados?.serie_nf ?? payload.serie_nf}</li>
          ${data.dados?.chave_nf ? `<li>Chave: ${data.dados.chave_nf}</li>` : payload.chave_nf ? `<li>Chave: ${payload.chave_nf}</li>` : ''}
        </ul>
        ${emailStatus}
      `;

      alert(emailSucesso
        ? '✅ Aviso registrado e e-mail enviado com sucesso.'
        : '⚠ Aviso registrado, mas houve falha ao enviar o e-mail.');
    } catch (error) {
      alert(error.message);
      resultado.classList.remove('hidden', 'sucesso', 'alerta');
      resultado.classList.add('erro');
      resultado.innerHTML = `
        <strong>Erro ao registrar aviso.</strong>
        <p class="status-message warning">${error.message}</p>
      `;
    }
  });
})();

