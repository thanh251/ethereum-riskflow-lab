const state = { graph: {nodes: [], edges: []}, alerts: [], metrics: {}, filter: 'all' };
const short = a => a ? `${a.slice(0, 7)}…${a.slice(-5)}` : '—';
const number = value => new Intl.NumberFormat('vi-VN', {maximumFractionDigits: 2}).format(value || 0);
const when = ts => ts ? new Date(ts * 1000).toLocaleString('vi-VN') : '—';

async function getJson(path, fallback) {
  try { const r = await fetch(path); return r.ok ? await r.json() : fallback; }
  catch { return fallback; }
}

function renderKpis() {
  const m = state.metrics;
  const high = state.alerts.filter(a => a.severity === 'high').length;
  const values = [
    ['Giao dịch', number(m.transfer_count)], ['Địa chỉ', number(m.node_count)],
    ['Cạnh graph', number(m.edge_count)], ['Tổng USDC', number(m.total_amount)], ['Cảnh báo cao', high]
  ];
  document.querySelector('#kpis').innerHTML = values.map(([label, value]) => `<div class="kpi"><strong>${value}</strong><span>${label}</span></div>`).join('');
}

function renderAlerts() {
  const rows = state.alerts.filter(a => state.filter === 'all' || a.severity === state.filter).slice(0, 100);
  document.querySelector('#alerts').innerHTML = rows.map(a => `<tr data-address="${a.address}">
    <td title="${a.address}">${short(a.address)}</td><td><strong>${a.score}</strong></td>
    <td><span class="badge ${a.severity}">${a.severity}</span></td>
    <td>${a.reasons[0]?.message || 'Tín hiệu tổng hợp'}</td><td>${when(a.observed_at)}</td></tr>`).join('');
  document.querySelectorAll('#alerts tr').forEach(row => row.onclick = () => showNode(row.dataset.address));
}

function showNode(address) {
  const node = state.graph.nodes.find(n => n.address === address) || {};
  const alert = state.alerts.find(a => a.address === address);
  const reasons = alert?.reasons || [];
  document.querySelector('#node-detail').innerHTML = `<div class="detail-address">${address}</div>
    <p><span class="score">${alert?.score ?? 0}</span> / 100 ${alert ? `<span class="badge ${alert.severity}">${alert.severity}</span>` : ''}</p>
    <p>Vào: <b>${number(node.in_amount)} USDC</b> · Ra: <b>${number(node.out_amount)} USDC</b></p>
    <p>Đối tác gửi: <b>${node.unique_senders ?? 0}</b> · Đối tác nhận: <b>${node.unique_receivers ?? 0}</b></p>
    <p>Fast-forward: <b>${number((node.fast_forward_ratio || 0) * 100)}%</b></p>
    ${reasons.length ? reasons.map(r => `<div class="reason"><b>${r.code} · +${r.points}</b>${r.message}</div>`).join('') : '<p class="empty">Không có cảnh báo trên ngưỡng hiển thị.</p>'}`;
}

function renderGraph() {
  const svg = document.querySelector('#graph');
  const nodes = state.graph.nodes.slice(0, 90);
  const ids = new Set(nodes.map(n => n.address));
  const edges = state.graph.edges.filter(e => ids.has(e.source) && ids.has(e.target)).slice(0, 180);
  const alerts = new Map(state.alerts.map(a => [a.address, a]));
  const width = 920, height = 520, cx = width / 2, cy = height / 2;
  const positions = new Map(nodes.map((n, i) => {
    const ring = i < 18 ? 150 : i < 50 ? 230 : 310;
    const angle = (i * 2.399963) % (Math.PI * 2);
    return [n.address, {x: cx + Math.cos(angle) * ring, y: cy + Math.sin(angle) * ring * .72}];
  }));
  svg.innerHTML = edges.map(e => { const a = positions.get(e.source), b = positions.get(e.target); return `<line class="edge" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke-width="${Math.min(6, 1 + Math.log10(1 + e.amount))}"/>`; }).join('') +
    nodes.map(n => { const p = positions.get(n.address), a = alerts.get(n.address); const fill = a?.severity === 'high' ? '#b23b3b' : a?.severity === 'medium' ? '#a76b16' : '#1d5e85'; const r = Math.min(14, 4 + Math.sqrt(n.tx_count || 1)); return `<circle class="node" data-address="${n.address}" cx="${p.x}" cy="${p.y}" r="${r}" fill="${fill}"><title>${short(n.address)} · ${a?.score || 0}</title></circle>`; }).join('');
  svg.querySelectorAll('.node').forEach(node => node.addEventListener('click', () => showNode(node.dataset.address)));
}

document.querySelectorAll('.filters button').forEach(button => button.onclick = () => {
  document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
  button.classList.add('active'); state.filter = button.dataset.filter; renderAlerts();
});

Promise.all([
  getJson('/api/graph', {nodes: [], edges: []}), getJson('/api/alerts', []),
  getJson('/api/metrics', {}), getJson('/api/source', null), getJson('/api/scenario', null)
]).then(([graph, alerts, metrics, source, scenario]) => {
  Object.assign(state, {graph, alerts, metrics});
  document.querySelector('#source-label').textContent = source ? `Mainnet · block ${source.from_block}–${source.to_block}` : scenario ? `ABM · seed ${scenario.seed}` : 'Chưa có artifact';
  renderKpis(); renderAlerts(); renderGraph();
  if (alerts[0]) showNode(alerts[0].address);
});

