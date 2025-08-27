// Ao clicar em uma linha da tabela, preenche os inputs com os dados
document.querySelectorAll("#tabela tbody tr").forEach(row => {
  row.addEventListener("click", () => {
    const cells = row.querySelectorAll("td");
    document.getElementById("nome").value = cells[0].textContent;
    document.getElementById("email").value = cells[1].textContent;
    document.getElementById("telefone").value = cells[2].textContent;
    document.getElementById("rg").value = cells[3].textContent;
  });
});
