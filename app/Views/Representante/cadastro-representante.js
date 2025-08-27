document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-representante");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Captura os valores do formulário
    const representante = {
      nome: document.getElementById("nome").value.trim(),
      rg: document.getElementById("rg").value.trim(),
      cpf: document.getElementById("cpf").value.trim(),
      telefone: document.getElementById("telefone").value.trim(),
      email: document.getElementById("email").value.trim(),
    };

    // Validação simples
    if (!representante.nome || !representante.rg || !representante.cpf || !representante.telefone || !representante.email) {
      alert("Preencha todos os campos obrigatórios!");
      return;
    }

    // Desabilita o botão durante a requisição
    const btnSalvar = form.querySelector(".btn-primary");
    btnSalvar.disabled = true;
    btnSalvar.innerText = "Salvando...";

    try {
      // Simulação de chamada a API
      const response = await fakeApiInsert(representante);

      if (response.success) {
        alert("✅ Representante cadastrado com sucesso!");
        form.reset();
      } else {
        alert("❌ Erro ao cadastrar representante!");
      }
    } catch (error) {
      console.error(error);
      alert("⚠ Ocorreu um erro na comunicação com o servidor.");
    } finally {
      // Reabilita botão
      btnSalvar.disabled = false;
      btnSalvar.innerText = "Salvar";
    }
  });

  /**
   * Função que simula uma chamada POST a uma API
   * @param {Object} data 
   * @returns {Promise<Object>}
   */
  function fakeApiInsert(data) {
    return new Promise((resolve) => {
      console.log("📡 Enviando para API (simulado)...", data);

      // Simula tempo de resposta do servidor
      setTimeout(() => {
        // Retorno simulado da API
        resolve({ success: true, id: Math.floor(Math.random() * 1000) });
      }, 1500);
    });
  }
});
