// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = null;
let servicoSelecionado = null; // Guarda o serviço selecionado para edição

// -------------------------
// Função para obter o token
// -------------------------
// async function obterToken() {
//     const url = 'http://localhost:8000/token';
//     const formData = new URLSearchParams();
//     formData.append('username', 'usuario');
//     formData.append('password', '1234');
//     formData.append('grant_type', 'password');

//     try {
//         const response = await fetch(url, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//             body: formData
//         });

//         if (!response.ok) {
//             const erro = await response.text();
//             throw new Error(`Erro ao obter token: ${erro}`);
//         }

//         const data = await response.json();
//         tokenGlobal = data.access_token;
//         return tokenGlobal;

//     } catch (err) {
//         console.error('Erro ao obter token:', err);
//         alert("Falha ao autenticar. Verifique o backend e abra via localhost:5501.");
//         return null;
//     }
// }

// -------------------------
// Função para carregar serviços
// -------------------------
async function carregarServicos() {
    if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");

    const url = 'http://127.0.0.1:8000/Servicos';

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar serviços: ${erro}`);
        }

        const servicos = await response.json();

        const tbody = document.querySelector('#gridServicos tbody');
        tbody.innerHTML = '';

        servicos.forEach(s => {
            const tr = document.createElement('tr');
            const valorFormatado = Number(s.Valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            tr.innerHTML = `
                <td>${s.ID}</td>
                <td>${s.Servico}</td>
                <td>R$ ${valorFormatado}</td>
                <td>${s.Recorrente ? 'Sim' : 'Não'}</td>
            `;
            tr.addEventListener('click', () => carregarFormulario(s, tr));
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        alert("Falha ao carregar serviços. Veja o console para detalhes.");
    }
}

// -------------------------
// Função para carregar formulário com serviço selecionado
// -------------------------
function carregarFormulario(servico, linha) {
    servicoSelecionado = servico;
    document.getElementById('txtServico').value = servico.Servico;
    document.getElementById('txtValor').value = servico.Valor;
    document.getElementById('chkRecorrente').checked = servico.Recorrente;
    document.getElementById('btnAction').textContent = 'Alterar';

    document.querySelectorAll('#gridServicos tbody tr').forEach(tr => tr.classList.remove('selected'));
    linha.classList.add('selected');
}

// -------------------------
// Função para limpar formulário
// -------------------------
function limparFormulario() {
    servicoSelecionado = null;
    document.getElementById('txtServico').value = '';
    document.getElementById('txtValor').value = '';
    document.getElementById('chkRecorrente').checked = false;
    document.getElementById('btnAction').textContent = 'Salvar';

    document.querySelectorAll('#gridServicos tbody tr').forEach(tr => tr.classList.remove('selected'));
}

// -------------------------
// Função para salvar serviço (inserir ou alterar)
// -------------------------
async function salvarServico(event) {
    event.preventDefault();

    const dsServico = document.getElementById('txtServico').value.trim();
    const valor = parseFloat(document.getElementById('txtValor').value.replace(',', '.'));
    const recorrente = document.getElementById('chkRecorrente').checked ? 1 : 0;

    if (!dsServico || isNaN(valor)) {
        alert("Preencha todos os campos corretamente.");
        return;
    }

    // if (!tokenGlobal) {
    //     await obterToken();
    //     if (!tokenGlobal) return;
    // }
    if (!await validarToken()) {
        return
    }
    tokenGlobal =localStorage.getItem("token");

    const url = servicoSelecionado
        ? 'http://127.0.0.1:8000/AlterarServico/'
        : 'http://127.0.0.1:8000/InserirServico/';

    const payload = servicoSelecionado
        ? { id_servico: servicoSelecionado.ID, ds_servico: dsServico, vl_servico: valor, fl_recorrente: recorrente }
        : { id_servico: 0, ds_servico: dsServico, vl_servico: valor, fl_recorrente: recorrente };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${tokenGlobal}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Falha ao salvar serviço: ${erro}`);
        }

        const data = await response.json();
        alert(data.mensagem || 'Serviço salvo com sucesso!');
        limparFormulario();
        carregarServicos();

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar serviço. Veja o console para detalhes.");
    }
}

async function AlterarServico(servico) {
  try {
    const response = await fetch("http://127.0.0.1:8000/AlterarServico", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(servico),
    });

    if (!response.ok) {
      throw new Error(`Erro ao alterar serviço: ${response.status}`);
    }

    const data = await response.json();
    alert("Serviço alterado com sucesso!");
    carregarServicos(); // Atualiza a grid após alteração
    limparFormulario(); // Reseta o formulário
    return data;
  } catch (error) {
    console.error(error);
    alert("Erro ao alterar serviço");
  }
}

// -------------------------
// Inicializa ao carregar a página
// -------------------------
window.addEventListener('DOMContentLoaded', () => {
    carregarServicos();
    document.getElementById('formServico').addEventListener('submit', salvarServico);
    document.getElementById('btnNovo').addEventListener('click', limparFormulario);
});
