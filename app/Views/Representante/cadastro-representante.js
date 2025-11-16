// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = null;
let representanteSelecionado = null;

const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';
const buildApiUrl = window.buildApiUrl || (path => `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`);

// -------------------------
// Carregar representantes
// -------------------------
async function carregarRepresentantes() {
    if (!await validarToken()) return;
    tokenGlobal = localStorage.getItem("token");

    try {
        const response = await fetch(buildApiUrl('/Representantes'), {
            method: "GET",
            headers: { "Authorization": `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar representantes: ${erro}`);
        }

        const representantes = await response.json();
        const lista = document.getElementById("lista-representantes");
        lista.innerHTML = "";

        representantes.forEach(r => {
            const card = document.createElement("article");
            card.className = "representante-card";
            card.dataset.nome = normalizarTexto(r.Cliente || "");
            card.innerHTML = `
                <h3>${r.Cliente || "Sem nome"}</h3>
                <div class="dados">
                    <span><strong>RG:</strong> ${r.RG && r.RG !== "None" ? r.RG : "-"}</span>
                    <span><strong>CPF:</strong> ${r.CPF && r.CPF !== "None" ? r.CPF : "-"}</span>
                    <span><strong>Telefone:</strong> ${r.Telefone && r.Telefone !== "None" ? r.Telefone : "-"}</span>
                    <span><strong>Dt. Nasc.:</strong> ${r.DtNascimento && r.DtNascimento !== "None" ? r.DtNascimento : "-"}</span>
                    <span><strong>E-mail:</strong> ${r.Email && r.Email !== "None" ? r.Email : "-"}</span>
                </div>
            `;
            card.addEventListener("click", () => carregarFormulario(r, card));
            lista.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        alert("Falha ao carregar representantes.");
    }
}

// -------------------------
// Carregar formulário
// -------------------------
function carregarFormulario(rep, elemento) {
    representanteSelecionado = rep;
    const form = document.getElementById("form-representante");

    form.nome.value = rep.Cliente || "";
    form.rg.value = rep.RG !== "None" ? rep.RG : "";
    form.cpf.value = rep.CPF !== "None" ? rep.CPF : "";
    form.telefone.value = rep.Telefone !== "None" ? rep.Telefone : "";
    form.email.value = rep.Email !== "None" ? rep.Email : "";
    form.dataNasc.value = (rep.DtNascimento && rep.DtNascimento !== "None") ? rep.DtNascimento.split("T")[0] : "";

    form.querySelector("button[type=submit]").textContent = "Atualizar";

    document.querySelectorAll(".representante-card").forEach(card => card.classList.remove("selected"));
    if (elemento) {
        elemento.classList.add("selected");
    }
}

// -------------------------
// Limpar formulário
// -------------------------
function limparFormulario() {
    representanteSelecionado = null;
    const form = document.getElementById("form-representante");
    form.reset();
    form.querySelector("button[type=submit]").textContent = "Salvar";
    document.querySelectorAll(".representante-card").forEach(card => card.classList.remove("selected"));
}

// -------------------------
// Salvar representante
// -------------------------
async function salvarRepresentante(event) {
    event.preventDefault();
    const form = document.getElementById("form-representante");

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

    if (!await validarToken()) return;
    tokenGlobal = localStorage.getItem("token");

    const url = representanteSelecionado
        ? buildApiUrl('/AlterarRepresentante')
        : buildApiUrl('/InserirRepresentante');

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${tokenGlobal}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(rep)
        });

        if (!response.ok) throw new Error("Erro ao salvar representante.");

        const data = await response.json();
        alert(data.mensagem || "Representante salvo com sucesso!");
        limparFormulario();
        carregarRepresentantes();

    } catch (err) {
        console.error(err);
        alert("Erro ao salvar representante.");
    }
}

// -------------------------
// Excluir representante
// -------------------------
async function excluirRepresentante(id) {
    if (!confirm("Deseja realmente excluir este representante?")) return;

    if (!await validarToken()) return;
    tokenGlobal = localStorage.getItem("token");

    try {
        const response = await fetch(buildApiUrl(`/ExcluirRepresentante/${id}`), {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) throw new Error("Erro ao excluir representante.");
        alert("Representante excluído com sucesso!");
        carregarRepresentantes();

    } catch (err) {
        console.error(err);
        alert("Erro ao excluir representante.");
    }
}

// -------------------------
// Formatar data
// -------------------------
function formatarData(inputDate) {
    if (!inputDate) return "";
    const [ano, mes, dia] = inputDate.split("-");
    return `${dia}/${mes}/${ano}`;
}

// -------------------------
// Filtro por Nome
// -------------------------
function normalizarTexto(texto) {
    return texto
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
}

function aplicarFiltro() {
    const filtro = normalizarTexto(document.getElementById("filtroNome").value);
    document.querySelectorAll(".representante-card").forEach(card => {
        card.style.display = filtro ? (card.dataset.nome.includes(filtro) ? "" : "none") : "";
    });
}

// -------------------------
// Inicialização
// -------------------------
window.addEventListener("DOMContentLoaded", () => {
    carregarRepresentantes();

    const form = document.getElementById("form-representante");
    form.addEventListener("submit", salvarRepresentante);
    form.addEventListener("reset", limparFormulario);

    const lista = document.getElementById("lista-representantes");
    lista.addEventListener("click", (e) => {
        if (e.target.classList.contains("excluir")) {
            const id = Number(e.target.dataset.id);
            excluirRepresentante(id);
        }
    });

    document.getElementById("filtroNome").addEventListener("input", aplicarFiltro);
});
