document.addEventListener('DOMContentLoaded', () => {
  async function loadNodes() {
    const res = await fetch('/nodes.json', { cache: 'no-store' });
    return res.ok ? await res.json() : [];
  }

  function uniqueRegions(nodes) {
    return [...new Set(nodes.map(n => n.region))];
  }

  function createFilterButtons(regions) {
    const bar = document.getElementById('filter-bar');
    regions.forEach((r, i) => {
      const btn = document.createElement('button');
      btn.className = 'filter-btn' + (i === 0 ? ' active' : '');
      btn.textContent = r;
      btn.dataset.region = r;
      btn.onclick = () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        showRegion(r);
      };
      bar.appendChild(btn);
    });
  }

  function createTableForRegion(region, nodes) {
    const table = document.createElement('table');
    table.className = 'server-table';
    table.innerHTML = `
      <thead><tr><th>城市</th><th>协议</th><th>数量</th><th>操作</th></tr></thead>
      <tbody>
        ${nodes.map(n => `
          <tr>
            <td>${n.city}</td>
            <td>${n.protocol}</td>
            <td>${n.count}</td>
            <td><a class="download-link" href="${n.download_url}" target="_blank">下载配置</a></td>
          </tr>`).join('')}
      </tbody>`;
    const container = document.createElement('div');
    container.id = `region-${region}`;
    container.appendChild(table);
    return container;
  }

  let allNodes, regions;

  async function render() {
    allNodes = await loadNodes();
    regions = uniqueRegions(allNodes);
    createFilterButtons(regions);
    const list = document.getElementById('server-list');
    regions.forEach(r => {
      const regionNodes = allNodes.filter(n => n.region === r);
      const tableDiv = createTableForRegion(r, regionNodes);
      tableDiv.style.display = r === regions[0] ? '' : 'none';
      list.appendChild(tableDiv);
    });
  }

  function showRegion(region) {
    regions.forEach(r => {
      document.getElementByI
