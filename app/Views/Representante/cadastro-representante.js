// -------------------------
// Variáveis globais
// -------------------------
let tokenGlobal = null;
let representanteSelecionado = null;

// -------------------------
// Carregar representantes
// -------------------------
async function carregarRepresentantes() {
    if (!await validarToken()) return;
    tokenGlobal = localStorage.getItem("token");

    try {
        const response = await fetch("http://127.0.0.1:8000/Representantes", {
            method: "GET",
            headers: { "Authorization": `Bearer ${tokenGlobal}` }
        });

        if (!response.ok) {
            const erro = await response.text();
            throw new Error(`Erro ao carregar representantes: ${erro}`);
        }

        const representantes = await response.json();
        const tbody = document.querySelector("#tabela-representantes tbody");
        tbody.innerHTML = "";

        representantes.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.Cliente || ""}</td>
                <td>${r.RG !== "None" ? r.RG : ""}</td>
                <td>${r.CPF !== "None" ? r.CPF : ""}</td>
                <td>${r.Telefone !== "None" ? r.Telefone : ""}</td>
                <td>${r.DtNascimento !== "None" ? r.DtNascimento : ""}</td>
                <td>${r.Email !== "None" ? r.Email : ""}</td>`;
                // <td>
                //      <button class="acao-btn excluir" data-id="${r.Id}">Excluir</button>
                // </td>
            // `;

            tr.addEventListener("click", () => carregarFormulario(r, tr));
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        alert("Falha ao carregar representantes.");
    }
}

// -------------------------
// Carregar formulário
// -------------------------
function carregarFormulario(rep, linha) {
    representanteSelecionado = rep;
    const form = document.getElementById("form-representante");

    form.nome.value = rep.Cliente || "";
    form.rg.value = rep.RG !== "None" ? rep.RG : "";
    form.cpf.value = rep.CPF !== "None" ? rep.CPF : "";
    form.telefone.value = rep.Telefone !== "None" ? rep.Telefone : "";
    form.email.value = rep.Email !== "None" ? rep.Email : "";
    form.dataNasc.value = (rep.DtNascimento && rep.DtNascimento !== "None") ? rep.DtNascimento.split("T")[0] : "";

    form.querySelector("button[type=submit]").textContent = "Atualizar";

    document.querySelectorAll("#tabela-representantes tbody tr").forEach(tr => tr.classList.remove("selected"));
    linha.classList.add("selected");
}

// -------------------------
// Limpar formulário
// -------------------------
function limparFormulario() {
    representanteSelecionado = null;
    const form = document.getElementById("form-representante");
    form.reset();
    form.querySelector("button[type=submit]").textContent = "Salvar";
    document.querySelectorAll("#tabela-representantes tbody tr").forEach(tr => tr.classList.remove("selected"));
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
        ? "http://127.0.0.1:8000/AlterarRepresentante"
        : "http://127.0.0.1:8000/InserirRepresentante";

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
        const response = await fetch(`http://127.0.0.1:8000/ExcluirRepresentante/${id}`, {
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
    const linhas = document.querySelectorAll("#tabela-representantes tbody tr");

    linhas.forEach(linha => {
        const nome = normalizarTexto(linha.querySelector("td")?.textContent || "");
        linha.style.display = nome.includes(filtro) ? "" : "none";
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

    const tabela = document.querySelector("#tabela-representantes tbody");
    tabela.addEventListener("click", (e) => {
        if (e.target.classList.contains("excluir")) {
            const id = Number(e.target.dataset.id);
            excluirRepresentante(id);
        }
    });

    document.getElementById("filtroNome").addEventListener("input", aplicarFiltro);
});
