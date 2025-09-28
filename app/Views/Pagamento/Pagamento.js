document.addEventListener('DOMContentLoaded', () => {
  const chkPago = document.getElementById('chkPago');
  const groupDtPagamento = document.getElementById('groupDtPagamento');
  const txtValor = document.getElementById('txtValor');
  const form = document.getElementById('formPagamento');
  const cmbFornecedores = document.getElementById('cmbFornecedores');
  const cmbFormaPagamento = document.getElementById('cmbFormaPagamento');
  const tabelaBody = document.querySelector("#dgvPagamentos tbody");

  const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';

  let token = null;

  // 🔹 Obter token igual tela de serviços
  // async function obterToken() {
  //   try {
  //     if (token) return token; // já temos token

  //     const resp = await fetch(`${API_BASE}/token`, {
  //       method: "POST",
  //       headers: { "Content-Type": "application/x-www-form-urlencoded" },
  //       body: new URLSearchParams({
  //         username: "usuario", // ajuste conforme seu backend
  //         password: "1234"      // ajuste conforme seu backend
  //       })
  //     });

  //     if (!resp.ok) throw new Error("Erro ao autenticar");
  //     const data = await resp.json();
  //     token = data.access_token;
  //     return token;
  //   } catch (err) {
  //     alert("Erro ao obter token: " + err.message);
  //   }
  // }

  
  chkPago.addEventListener('change', () => {
    groupDtPagamento.classList.toggle('hidden', !chkPago.checked);
  });

  txtValor.addEventListener('keypress', (e) => {
    const char = String.fromCharCode(e.which);
    if (!/[0-9,]/.test(char) && !e.ctrlKey && !e.metaKey && e.key !== 'Backspace') {
      e.preventDefault();
    }
  });

  // 🔹 Carregar fornecedores e formas de pagamento
  async function carregarSelects() {
    try {
      const respFornecedores = await fetch(`${API_BASE}/RetornaFornecedores`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const fornecedores = await respFornecedores.json();

      fornecedores.forEach(f => {
        const option = document.createElement('option');
        option.value = f.id_fornecedor;
        option.textContent = `${f.id_fornecedor} - ${f.nm_fantasia}`;
        cmbFornecedores.appendChild(option);
      });

      // Formas de Pagamento (fixas)
      const formasPagamento = [
        { id: 1, descricao: "Boleto" },
        { id: 2, descricao: "Cartão de Crédito" },
        { id: 3, descricao: "Cartão de Débito" },
        { id: 4, descricao: "Pix" },
        { id: 5, descricao: "Transferência Entre Contas" }
      ];

      formasPagamento.forEach(fp => {
        const option = document.createElement('option');
        option.value = fp.id;
        option.textContent = `${fp.id} - ${fp.descricao}`;
        cmbFormaPagamento.appendChild(option);
      });

    } catch (error) {
      alert('Erro ao carregar selects: ' + error.message);
    }
  }

  // 🔹 Carregar grid de pagamentos
  async function carregarGrid() {
    tabelaBody.innerHTML = "";
    try {
      const response = await fetch(`${API_BASE}/ListarDebitos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const pagamentos = await response.json();

      pagamentos.forEach(pg => {
        const tr = document.createElement("tr");
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
          ${pg.StatusPagamento !== "Pago" 
          ? `<button class="btn-primary" data-id="${pg.ID}">Baixar</button>` 
          : ""}
    </td>
        `;
        tabelaBody.appendChild(tr);
      });

      // Botão Excluir
      document.querySelectorAll(".btn-delete").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.dataset.id;
          if (confirm("Deseja realmente excluir este pagamento?")) {
            try {
              const resp = await fetch(`${API_BASE}/ExcluirDebito/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${token}` }
              });

              if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                throw new Error(err.detail || "Erro ao excluir pagamento");
              }

              alert("Pagamento excluído com sucesso!");
              await carregarGrid();
            } catch (error) {
              alert("Erro ao excluir: " + error.message);
            }
          }
        });
      });

      // Botão Baixar
      document.querySelectorAll(".btn-primary").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.dataset.id;
          if (confirm("Deseja realmente baixar este pagamento?")) {
            try {
              const resp = await fetch(`${API_BASE}/BaixarDebito?id_pagamento=${id}&id_usuario=3`, {
                method: "POST",
                headers: {
                  Authorization: `Bearer ${token}`
                }
              });

              if (!resp.ok) {
                const err = await resp.json();
                throw new Error(err.detail || "Erro ao baixar pagamento");
              }

              alert("Pagamento baixado com sucesso!");
              carregarGrid();
            } catch (error) {
              alert("Erro ao baixar: " + error.message);
            }
          }
        });
      });

    } catch (error) {
      alert("Erro ao carregar pagamentos: " + error.message);
    }
  }

  // 🔹 Inserir pagamento
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const pagamento = {
      ds_pagamento: document.getElementById('txtPagamento').value,
      dt_pagamento: chkPago.checked ? document.getElementById('dtpPagamento').value : null,
      dt_vencimento: document.getElementById('dtpVencimento').value,
      id_fornecedor: parseInt(cmbFornecedores.value),
      vl_pagamento: txtValor.value,
      id_forma_pagamento: parseInt(cmbFormaPagamento.value),
      id_usuario: 3 // 🔹 ajustar conforme usuário logado
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
        alert('Pagamento lançado com sucesso!');
        form.reset();
        groupDtPagamento.classList.add('hidden');
        carregarGrid();
      } else {
        const err = await response.json();
        alert('Erro ao salvar pagamento: ' + (err.detail || response.status));
      }
    } catch (error) {
      alert('Erro ao enviar: ' + error.message);
    }
  });

  // 🔹 Inicialização
  (async () => {
    if (!await validarToken()) {
        return
    }
    token =localStorage.getItem("token");
    if (token) {
      carregarSelects();
      carregarGrid();
    }
  })();
});

