// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = null;
let representanteSelecionado = null; // Guarda o representante selecionado para edição

// -------------------------
// Função para obter token
// -------------------------
async function obterToken() {
    const url = 'http://localhost:8000/token';
    const formData = new URLSearchParams();
    formData.append('username', 'usuario');
    formData.append('password', '1234');
    formData.append('grant_type', 'password');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao obter token: ${erro}`);
        }

        const data = await response.json();
        tokenGlobal = data.access_token;
        return tokenGlobal;

    } catch (err) {
        console.error('Erro ao obter token:', err);
        alert("Falha ao autenticar. Verifique o backend e abra via localhost:5501.");
        return null;
    }
}

// -------------------------
// Função para carregar representantes
// -------------------------
async function carregarRepresentantes() {
    if (!tokenGlobal) {
        await obterToken();
        if (!tokenGlobal) return;
    }

    const url = 'http://127.0.0.1:8000/Representantes';

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar representantes: ${erro}`);
        }

        const representantes = await response.json();
        const tbody = document.querySelector('#tabela-representantes tbody');
        tbody.innerHTML = '';

        representantes.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${r.Cliente || ''}</td>
                <td>${r.RG !== "None" ? r.RG : ''}</td>
                <td>${r.CPF !== "None" ? r.CPF : ''}</td>
                <td>${r.Telefone !== "None" ? r.Telefone : ''}</td>
                <td>${r.DtNascimento !== "None" ? r.DtNascimento : ''}</td>
                <td>${r.Email !== "None" ? r.Email : ''}</td>
                <td>
                    <button class="acao-btn editar" data-id="${r.Id}">Editar</button>
                    <button class="acao-btn excluir" data-id="${r.Id}">Excluir</button>
                </td>
            `;

            tr.addEventListener('click', () => carregarFormulario(r, tr));
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        alert("Falha ao carregar representantes. Veja o console para detalhes.");
    }
}

// -------------------------
// Carrega formulário para edição
// -------------------------
function carregarFormulario(rep, linha) {
    representanteSelecionado = rep;
    const form = document.getElementById('form-representante');

    form.nome.value = rep.Cliente || '';
    form.rg.value = rep.RG !== "None" ? rep.RG : '';
    form.cpf.value = rep.CPF !== "None" ? rep.CPF : '';
    form.telefone.value = rep.Telefone !== "None" ? rep.Telefone : '';
    form.email.value = rep.Email !== "None" ? rep.Email : '';

    if (rep.DtNascimento && rep.DtNascimento !== "None") {
        const [ano, mes, dia] = rep.DtNascimento.split("-");
        form.dataNasc.value = `${ano}-${mes}-${dia}`;
    } else {
        form.dataNasc.value = '';
    }

    form.querySelector("button[type=submit]").textContent = "Atualizar";

    document.querySelectorAll('#tabela-representantes tbody tr').forEach(tr => tr.classList.remove('selected'));
    linha.classList.add('selected');
}

// -------------------------
// Limpar formulário
// -------------------------
function limparFormulario() {
    representanteSelecionado = null;
    const form = document.getElementById('form-representante');
    form.reset();
    form.querySelector("button[type=submit]").textContent = "Salvar";
    document.querySelectorAll('#tabela-representantes tbody tr').forEach(tr => tr.classList.remove('selected'));
}

// -------------------------
// Salvar ou Alterar Representante
// -------------------------
async function salvarRepresentante(event) {
    event.preventDefault();
    const form = document.getElementById('form-representante');

    const rep = {
        id_cliente: representanteSelecionado?.Id ?? 0,
        nm_cliente: form.nome.value.trim(),
        dt_nascimento: formatarData(form.dataNasc.value.trim()),
        cpf: form.cpf.value.trim(),
        rg: form.rg.value.trim(),
        telefone: form.telefone.value.trim(),
        email: form.email.value.trim()
    };

    if (Object.values(rep).some(v => v === "")) {
        alert("Preencha todos os campos!");
        return;
    }

    if (!tokenGlobal) {
        await obterToken();
        if (!tokenGlobal) return;
    }

    const url = representanteSelecionado
        ? 'http://127.0.0.1:8000/AlterarRepresentante'
        : 'http://127.0.0.1:8000/InserirRepresentante';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${tokenGlobal}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rep)
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao salvar representante: ${erro}`);
        }

        const data = await response.json();
        alert(data.mensagem || 'Representante salvo com sucesso!');
        limparFormulario();
        carregarRepresentantes();

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar representante. Veja o console para detalhes.");
    }
}

// -------------------------
// Excluir representante
// -------------------------
async function excluirRepresentante(id) {
    if (!confirm("Deseja realmente excluir este representante?")) return;

    if (!tokenGlobal) {
        await obterToken();
        if (!tokenGlobal) return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/ExcluirRepresentante/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) throw new Error(`Erro ao excluir representante: ${response.status}`);
        alert("Representante excluído com sucesso!");
        carregarRepresentantes();

    } catch (err) {
        console.error(err);
        alert("Erro ao excluir representante.");
    }
}

// -------------------------
// Formatar data para dd/mm/yyyy
// -------------------------
function formatarData(inputDate) {
    if (!inputDate) return "";
    const [ano, mes, dia] = inputDate.split("-");
    return `${dia}/${mes}/${ano}`;
}

// -------------------------
// Inicialização
// -------------------------
window.addEventListener('DOMContentLoaded', () => {
    carregarRepresentantes();

    const form = document.getElementById('form-representante');
    form.addEventListener('submit', salvarRepresentante);
    form.addEventListener('reset', limparFormulario);

    const tabela = document.querySelector('#tabela-representantes tbody');
    tabela.addEventListener('click', (e) => {
        if (e.target.classList.contains('excluir')) {
            const id = Number(e.target.dataset.id);
            excluirRepresentante(id);
        }
    });
});
