(() => {
  // Simulação inicial dos serviços (substituir com backend real)
  let servicos = [
    { id: 1, descricao: "Consultoria Financeira", valor: 1500.0, recorrente: true },
    { id: 2, descricao: "Manutenção Técnica", valor: 500.0, recorrente: false },
    { id: 3, descricao: "Desenvolvimento Web", valor: 3000.0, recorrente: false },
  ];

  let acao = 1; // 1 = adicionar, 2 = alterar
  let servicoSelecionadoId = null;

  // DOM refs
  const form = document.getElementById("formServico");
  const txtServico = document.getElementById("txtServico");
  const txtValor = document.getElementById("txtValor");
  const chkRecorrente = document.getElementById("chkRecorrente");
  const btnAction = document.getElementById("btnAction");
  const tabelaBody = document.querySelector("#dgvServicos tbody");

  // Formata valor para BRL
  function formatCurrency(value) {
    return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  }

  // Validação básica dos inputs
  function validarFormulario() {
    let valido = true;

    // Descrição
    if (!txtServico.value.trim()) {
      mostrarErro(txtServico, true);
      valido = false;
    } else {
      mostrarErro(txtServico, false);
    }

    // Valor - verifica se é número válido > 0
    const valorNum = parseFloat(txtValor.value.replace(",", "."));
    if (!valorNum || valorNum <= 0) {
      mostrarErro(txtValor, true);
      valido = false;
    } else {
      mostrarErro(txtValor, false);
    }

    return valido;
  }

  function mostrarErro(input, mostrar) {
    const grupo = input.parentElement;
    const erroMsg = grupo.querySelector(".error-message");
    if (mostrar) {
      erroMsg.hidden = false;
      input.classList.add("input-error");
    } else {
      erroMsg.hidden = true;
      input.classList.remove("input-error");
    }
  }

  // Atualiza tabela
  function carregarGrid() {
    tabelaBody.innerHTML = "";

    servicos.forEach((servico) => {
      const tr = document.createElement("tr");
      tr.dataset.id = servico.id;

      tr.innerHTML = `
        <td>${servico.id}</td>
        <td>${servico.descricao}</td>
        <td>${formatCurrency(servico.valor)}</td>
        <td>${servico.recorrente ? "Sim" : "Não"}</td>
      `;

      tr.addEventListener("dblclick", () => {
        selecionarServico(servico.id);
      });

      tabelaBody.appendChild(tr);
    });
  }

  // Selecionar serviço para edição
  function selecionarServico(id) {
    const servico = servicos.find((s) => s.id === id);
    if (!servico) return;

    servicoSelecionadoId = servico.id;
    txtServico.value = servico.descricao;
    txtValor.value = servico.valor.toFixed(2).replace(".", ",");
    chkRecorrente.checked = servico.recorrente;

    acao = 2;
    btnAction.textContent = "Alterar";

    // Marca linha selecionada
    [...tabelaBody.children].forEach((tr) => {
      tr.classList.toggle("selected", parseInt(tr.dataset.id) === servico.id);
    });
  }

  // Limpar formulário após ação
  function limparFormulario() {
    txtServico.value = "";
    txtValor.value = "";
    chkRecorrente.checked = false;
    acao = 1;
    servicoSelecionadoId = null;
    btnAction.textContent = "Adicionar";
    [...tabelaBody.children].forEach((tr) => tr.classList.remove("selected"));
  }

  // Adicionar ou alterar serviço
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    if (!validarFormulario()) return;

    const descricao = txtServico.value.trim();
    const valor = parseFloat(txtValor.value.replace(",", "."));
    const recorrente = chkRecorrente.checked;

    if (acao === 1) {
      // Adicionar
      const novoId = servicos.length ? Math.max(...servicos.map(s => s.id)) + 1 : 1;
      servicos.push({ id: novoId, descricao, valor, recorrente });
      alert("Serviço inserido com sucesso!");
    } else if (acao === 2 && servicoSelecionadoId !== null) {
      // Alterar
      const index = servicos.findIndex(s => s.id === servicoSelecionadoId);
      if (index > -1) {
        servicos[index] = { id: servicoSelecionadoId, descricao, valor, recorrente };
        alert("Serviço alterado com sucesso!");
      }
    }

    limparFormulario();
    carregarGrid();
  });

  // Permite só números e vírgula no campo valor
  txtValor.addEventListener("keypress", (e) => {
    const allowedKeys = ["0","1","2","3","4","5","6","7","8","9",",","."];
    if (!allowedKeys.includes(e.key) && e.key !== "Backspace") {
      e.preventDefault();
    }
  });

  // Inicializa a tabela e configurações
  carregarGrid();
})();
