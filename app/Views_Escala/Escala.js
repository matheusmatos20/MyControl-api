const API_BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';

let cache = {
  cargas: [],
  postos: [],
  cargos: [],
};

window.addEventListener('load', async () => {
  const ok = await validarToken();
  if (!ok) return;

  // Datas padrão (semana atual)
  const hoje = new Date();
  const ini = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate() - hoje.getDay() + 1);
  const fim = new Date(ini.getFullYear(), ini.getMonth(), ini.getDate() + 6);
  document.getElementById('dtInicio').value = ini.toISOString().slice(0, 10);
  document.getElementById('dtFim').value = fim.toISOString().slice(0, 10);

  bindUI();
  await Promise.all([
    carregarCargas(),
    carregarPostos(),
    carregarCargos(),
  ]);
  await montarFiltros();
  await renderGrid();
});

function bindUI() {
  document.getElementById('btnCadastroCarga').onclick = () => abrirModal('modalCarga');
  document.getElementById('btnCadastroPosto').onclick = () => abrirModal('modalPosto');
  const btnFolgasTop = document.getElementById('btnFolgasTop');
  if (btnFolgasTop) btnFolgasTop.onclick = () => abrirFolgaModal();
  document.getElementById('btnSalvarCarga').onclick = salvarCarga;
  document.getElementById('btnSalvarPosto').onclick = salvarPosto;
  document.getElementById('btnGerar').onclick = gerarEscala;
  document.getElementById('btnExport').onclick = exportarCSV;
  // Botão de folga já existe na toolbar (evitar duplicidade)

  document.querySelectorAll('[data-close]')
    .forEach(btn => btn.addEventListener('click', (e) => fecharModal(e.target.getAttribute('data-close'))));
  document.getElementById('selPostoFiltro').addEventListener('change', renderGrid);
  document.getElementById('selCargoFiltro').addEventListener('change', () => {});

  // Modal cell
  document.getElementById('btnSalvarCell').onclick = salvarEdicaoCelula;
  document.getElementById('btnExcluirCell').onclick = excluirItemCelula;
  document.getElementById('btnSalvarFolga').onclick = salvarFolga;
  document.getElementById('btnListarFolgas').onclick = listarFolgas;
}

function abrirModal(id) { document.getElementById(id).hidden = false; }
function fecharModal(id) { document.getElementById(id).hidden = true; }

async function carregarCargas() {
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/carga-horaria`, { headers: { 'Authorization': `Bearer ${token}` } });
  cache.cargas = resp.ok ? await resp.json() : [];
  // Preenche selects e grid listagem
  const selCarga = document.getElementById('selCarga');
  if (selCarga) {
    selCarga.innerHTML = cache.cargas.map(c => `<option value="${c.ID}">${c.ID} - ${c.Descricao}</option>`).join('');
  }
  const tbody = document.querySelector('#tblCarga tbody');
  if (tbody) {
    tbody.innerHTML = (cache.cargas || []).map(c => `
      <tr>
        <td>${c.ID}</td>
        <td>${c.Descricao}</td>
        <td>${c.HorasSemanais ?? ''}</td>
        <td><button class="btn" data-del-carga="${c.ID}">Excluir</button></td>
      </tr>
    `).join('');
    tbody.querySelectorAll('button[data-del-carga]')
      .forEach(b => b.addEventListener('click', () => excluirCarga(b.getAttribute('data-del-carga'))));
  }
}

async function carregarPostos() {
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/postos`, { headers: { 'Authorization': `Bearer ${token}` } });
  cache.postos = resp.ok ? await resp.json() : [];
  // Listagem
  const tbody = document.querySelector('#tblPostos tbody');
  if (tbody) {
    tbody.innerHTML = (cache.postos || []).map(p => `
      <tr>
        <td>${p.ID}</td>
        <td>${p.Posto}</td>
        <td>${p.CargaHoraria ?? ''}</td>
        <td>${p.Quantidade}</td>
        <td><button class="btn" data-del-posto="${p.ID}">Excluir</button></td>
      </tr>
    `).join('');
    tbody.querySelectorAll('button[data-del-posto]')
      .forEach(b => b.addEventListener('click', () => excluirPosto(b.getAttribute('data-del-posto'))));
  }
}

async function excluirCarga(id) {
  if (!confirm('Excluir carga horária?')) return;
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/carga-horaria/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
  if (!resp.ok) {
    const d = await resp.json().catch(() => ({}));
    alert(`Falha ao excluir: ${d.detail || resp.status}`);
    return;
  }
  await carregarCargas();
}

async function excluirPosto(id) {
  if (!confirm('Excluir posto?')) return;
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/postos/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
  if (!resp.ok) {
    const d = await resp.json().catch(() => ({}));
    alert(`Falha ao excluir posto: ${d.detail || resp.status}`);
    return;
  }
  await carregarPostos();
  await montarFiltros();
}

async function carregarCargos() {
  // Para filtro de cargo
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/Cargos`, { headers: { 'Authorization': `Bearer ${token}` } });
  cache.cargos = resp.ok ? await resp.json() : [];
}

async function montarFiltros() {
  const selPosto = document.getElementById('selPostoFiltro');
  selPosto.innerHTML = `<option value="">Todos os Postos</option>` +
    cache.postos.map(p => `<option value="${p.ID}">${p.ID} - ${p.Posto}</option>`).join('');
  const selCargo = document.getElementById('selCargoFiltro');
  selCargo.innerHTML = `<option value="">Todos os Cargos</option>` +
    cache.cargos.map(c => `<option value="${c.ID}">${c.ID} - ${c.Cargo}</option>`).join('');
}

async function salvarCarga() {
  const token = localStorage.getItem('token');
  const ds = document.getElementById('dsCarga').value.trim();
  const qt = document.getElementById('qtHoras').value ? parseInt(document.getElementById('qtHoras').value, 10) : null;
  if (!ds) { alert('Informe a descrição.'); return; }
  const resp = await fetch(`${API_BASE}/carga-horaria`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ ds_carga_horaria: ds, qt_horas_semanais: qt })
  });
  if (!resp.ok) { alert('Falha ao salvar carga horária.'); return; }
  await carregarCargas();
  fecharModal('modalCarga');
}

async function salvarPosto() {
  const token = localStorage.getItem('token');
  const nm = document.getElementById('nmPosto').value.trim();
  const id_carga = parseInt(document.getElementById('selCarga').value, 10);
  const qt = parseInt(document.getElementById('qtColab').value, 10) || 1;
  if (!nm || !id_carga) { alert('Informe o nome e a carga horária.'); return; }
  const resp = await fetch(`${API_BASE}/postos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ nm_posto: nm, id_carga_horaria: id_carga, qt_colaboradores: qt })
  });
  if (!resp.ok) { alert('Falha ao salvar posto.'); return; }
  await carregarPostos();
  await montarFiltros();
  fecharModal('modalPosto');
}

function toYMDLocal(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const da = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${da}`;
}

function parseLocalYMD(s) {
  const [y, m, d] = (s || '').split('-').map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d);
}

function intervaloDatas() {
  const di = document.getElementById('dtInicio').value;
  const df = document.getElementById('dtFim').value;
  if (!di || !df) return [];
  const datas = [];
  let d = parseLocalYMD(di);
  const end = parseLocalYMD(df);
  if (!d || !end) return [];
  while (d <= end) {
    datas.push(toYMDLocal(d));
    d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1);
  }
  return datas;
}

async function renderGrid() {
  const token = localStorage.getItem('token');
  const grid = document.getElementById('gridContainer');
  const datas = intervaloDatas();
  const postoFiltro = document.getElementById('selPostoFiltro').value;

  const postos = postoFiltro ? cache.postos.filter(p => String(p.ID) === String(postoFiltro)) : cache.postos;
  if (!datas.length || !postos.length) {
    grid.innerHTML = '<div class="empty">Selecione período e/ou cadastre postos.</div>';
    return;
  }

  // Cabeçalho
  let html = '<table><thead><tr><th>Posto</th>' + datas.map(d => `<th>${d}</th>`).join('') + '</tr></thead><tbody>';

  for (const p of postos) {
    html += `<tr><td>${p.Posto}</td>`;
    const reqs = datas.map(d => fetch(`${API_BASE}/escala/posto/${p.ID}/data/${d}`, { headers: { 'Authorization': `Bearer ${token}` } }));
    const rs = await Promise.all(reqs);
    const rows = await Promise.all(rs.map(r => r.ok ? r.json() : []));
    for (let i = 0; i < rows.length; i++) {
      const lista = rows[i] || [];
      const nomes = lista.map(x => x.NomeFuncionario || x.IdFuncionario).join(', ');
      const dStr = datas[i];
      html += `<td class="cell-editable" data-idposto="${p.ID}" data-date="${dStr}">${nomes || ''}</td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  grid.innerHTML = html;
  // Bind click cells
  grid.querySelectorAll('.cell-editable').forEach(td => {
    td.addEventListener('click', () => abrirEditorCelula(td, datas));
  });
}

async function gerarEscala() {
  const token = localStorage.getItem('token');
  const di = document.getElementById('dtInicio').value;
  const df = document.getElementById('dtFim').value;
  const id_posto = document.getElementById('selPostoFiltro').value;
  const id_cargo = document.getElementById('selCargoFiltro').value;
  if (!di || !df) { alert('Informe o período.'); return; }
  const body = {
    periodo_inicio: di,
    periodo_fim: df,
    limpar_existente: true
  };
  if (id_posto) body.id_postos = [parseInt(id_posto, 10)];
  if (id_cargo) body.id_cargos = [parseInt(id_cargo, 10)];

  const resp = await fetch(`${API_BASE}/escala/gerar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify(body)
  });
  const data = await resp.json();
  if (!resp.ok) {
    alert(`Falha ao gerar escala: ${data.detail || resp.status}`);
    return;
  }
  await renderGrid();
}

function exportarCSV() {
  const grid = document.querySelector('#gridContainer table');
  if (!grid) { alert('Nada para exportar.'); return; }
  const linhas = [];
  const rows = Array.from(grid.querySelectorAll('tr'));
  for (const tr of rows) {
    const cols = Array.from(tr.querySelectorAll('th,td')).map(td => '"' + String(td.textContent || '').replace(/"/g, '""') + '"');
    linhas.push(cols.join(','));
  }
  const csv = linhas.join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `escala_${new Date().toISOString().slice(0,10)}.csv`;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// --------- Edição por célula ---------
let cellContext = { idPosto: null, data: null, itens: [] };

async function abrirEditorCelula(td, datas) {
  const idPosto = td.getAttribute('data-idposto');
  // Coluna -> data index
  const ths = Array.from(td.closest('table').querySelectorAll('thead th'));
  const colIdx = Array.from(td.parentElement.children).indexOf(td);
  const dataRef = ths[colIdx].textContent;

  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/escala/posto/${idPosto}/data/${dataRef}`, { headers: { 'Authorization': `Bearer ${token}` } });
  const itens = resp.ok ? await resp.json() : [];
  cellContext = { idPosto, data: dataRef, itens };

  // Preenche colaboradores para seleção com restrição por cargo do posto, quando aplicável
  const sel = document.getElementById('selColaborador');
  let colabs = await carregarColaboradoresCombo();
  const posto = (cache.postos || []).find(p => String(p.ID) === String(idPosto));
  const cargoReq = inferirCargoPorPosto((posto && posto.Posto ? String(posto.Posto) : '').toLowerCase());
  if (cargoReq) {
    colabs = colabs.filter(c => c.CargoId === cargoReq);
  }
  sel.innerHTML = colabs.map(c => `<option value="${c.Id}">${c.Nome}</option>`).join('');

  // Preenche tabela de itens
  const tbody = document.querySelector('#tblCellItems tbody');
  tbody.innerHTML = (itens || []).map(x => `<tr data-id="${x.Id}"><td>${x.Id}</td><td>${x.NomeFuncionario || x.IdFuncionario}</td></tr>`).join('');

  document.getElementById('infoCell').textContent = `Posto ${idPosto} em ${dataRef}`;
  abrirModal('modalEditCell');
}

async function carregarColaboradoresCombo() {
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/Colaboradores`, { headers: { 'Authorization': `Bearer ${token}` } });
  if (!resp.ok) return [];
  const rows = await resp.json();
  // normaliza e tenta extrair o id do cargo do texto "<id> - <cargo>"
  const parseCargoId = (txt) => {
    if (!txt) return null;
    const m = String(txt).match(/^(\s*\d+)/);
    return m ? parseInt(m[1], 10) : null;
  };
  return rows.map(r => ({
    Id: r.Id,
    Nome: r.NomeColaborador || r.Nome || r.NM_FUNCIONARIO || r.NM || r.NomeFuncionario,
    CargoId: parseCargoId(r.Cargo)
  }));
}

// Deduza o cargo exigido pelo nome do posto
function inferirCargoPorPosto(nomePostoLower) {
  if (!nomePostoLower) return null;
  const flat = nomePostoLower.normalize('NFD').replace(/\p{Diacritic}/gu,'');
  const has = (s) => flat.includes(s);
  if (has('enferm')) {
    if (has('tecn')) return 2; // Técnica de Enfermagem
    if (has('aux')) return 1;  // Auxiliar de Enfermagem
    return 3;                  // Enfermeira(o)
  }
  if (has('nutricion')) return 5;
  if (has('limpez')) return 6;
  if (has('cuidad')) return 4;
  return null;
}

async function salvarEdicaoCelula() {
  const sel = document.getElementById('selColaborador');
  const idFunc = parseInt(sel.value, 10);
  const obs = document.getElementById('txtObs').value || null;
  const token = localStorage.getItem('token');
  if (!cellContext || !cellContext.idPosto || !cellContext.data) return;

  if (!cellContext.itens || cellContext.itens.length === 0) {
    // Inserir novo
    const resp = await fetch(`${API_BASE}/escala`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ id_funcionario: idFunc, id_posto: parseInt(cellContext.idPosto, 10), data: cellContext.data, turno: null, observacao: obs })
    });
    if (!resp.ok) {
      const d = await resp.json().catch(() => ({}));
      alert(`Falha ao inserir: ${d.detail || resp.status}`);
      return;
    }
  } else {
    // Atualizar o primeiro item da célula (política simples)
    const idEscala = cellContext.itens[0].Id;
    const resp = await fetch(`${API_BASE}/escala/${idEscala}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ id_funcionario: idFunc, id_posto: parseInt(cellContext.idPosto, 10), data: cellContext.data, turno: cellContext.itens[0].Turno || null, observacao: obs })
    });
    if (!resp.ok) {
      const d = await resp.json().catch(() => ({}));
      alert(`Falha ao atualizar: ${d.detail || resp.status}`);
      return;
    }
  }
  fecharModal('modalEditCell');
  await renderGrid();
}

async function excluirItemCelula() {
  if (!cellContext || !cellContext.itens || cellContext.itens.length === 0) {
    alert('Nada para excluir.'); return;
  }
  const token = localStorage.getItem('token');
  const idEscala = cellContext.itens[0].Id;
  const resp = await fetch(`${API_BASE}/escala/${idEscala}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
  if (!resp.ok) {
    const d = await resp.json().catch(() => ({}));
    alert(`Falha ao excluir: ${d.detail || resp.status}`);
    return;
  }
  fecharModal('modalEditCell');
  await renderGrid();
}

// --------- Folgas ---------
async function abrirFolgaModal() {
  const sel = document.getElementById('selColabFolga');
  const colabs = await carregarColaboradoresCombo();
  sel.innerHTML = colabs.map(c => `<option value="${c.Id}">${c.Nome}</option>`).join('');
  document.getElementById('dtFolga').value = (new Date()).toISOString().slice(0,10);
  document.getElementById('obsFolga').value = '';
  abrirModal('modalFolga');
  await listarFolgas();
}

async function salvarFolga() {
  const idFunc = parseInt(document.getElementById('selColabFolga').value, 10);
  const data = document.getElementById('dtFolga').value;
  const obs = document.getElementById('obsFolga').value || null;
  if (!idFunc || !data) { alert('Selecione colaborador e data.'); return; }
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/escala/folga`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ id_funcionario: idFunc, data, observacao: obs })
  });
  if (!resp.ok) {
    const d = await resp.json().catch(() => ({}));
    alert(`Falha ao registrar folga: ${d.detail || resp.status}`);
    return;
  }
  await listarFolgas();
}

async function listarFolgas() {
  const idFunc = parseInt((document.getElementById('selColabFolga').value||'0'), 10);
  if (!idFunc) { return; }
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/escala/folgas/funcionario/${idFunc}`, { headers: { 'Authorization': `Bearer ${token}` } });
  const rows = resp.ok ? await resp.json() : [];
  const tbody = document.querySelector('#tblFolgas tbody');
  tbody.innerHTML = rows.map(r => `<tr><td>${r.Id}</td><td>${String(r.Data).slice(0,10)}</td><td>${r.Observacao||''}</td><td><button class="btn" data-del="${r.Id}">Excluir</button></td></tr>`).join('');
  tbody.querySelectorAll('button[data-del]').forEach(b => b.addEventListener('click', () => excluirFolga(b.getAttribute('data-del'))));
}

async function excluirFolga(idFolga) {
  const token = localStorage.getItem('token');
  const resp = await fetch(`${API_BASE}/escala/folga/${idFolga}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
  if (!resp.ok) {
    const d = await resp.json().catch(() => ({}));
    alert(`Falha ao excluir folga: ${d.detail || resp.status}`);
    return;
  }
  await listarFolgas();
}
