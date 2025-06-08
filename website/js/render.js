async function loadNodes() {
  try {
    const res = await fetch('/nodes.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error('加载 nodes.json 出错：', error);
    return [];
  }
}

function uniqueRegions(nodes) {
  return [...new Set(nodes.map(n => n.region))];
}

function createFilterButtons(regions) {
  const bar = document.getElementById('filter-bar');
  if (!bar) {
    console.error('找不到 filter-bar 容器');
    return;
  }
  bar.innerHTML = ''; // 清空旧按钮
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
          <td>${n.city || '-'}</td>
          <td>${n.protocol || '-'}</td>
          <td>${n.count || '-'}</td>
          <td><a class="download-link" href="${n.download_url || '#'}" target="_blank">下载配置</a></td>
        </tr>`).join('')}
    </tbody>`;
  const container = document.createElement('div');
  container.id = `region-${region}`;
  container.appendChild(table);
  return container;
}

let allNodes = [];
let regions = [];

async function render() {
  allNodes = await loadNodes();
  if (!allNodes.length) {
    console.warn('nodes.json 为空或加载失败');
    return;
  }
  regions = uniqueRegions(allNodes);
  createFilterButtons(regions);

  const list = document.getElementById('server-list');
  if (!list) {
    console.error('找不到 server-list 容器');
    return;
  }
  list.innerHTML = ''; // 清空旧内容

  regions.forEach(r => {
    const regionNodes = allNodes.filter(n => n.region === r);
    const tableDiv = createTableForRegion(r, regionNodes);
    tableDiv.style.display = r === regions[0] ? '' : 'none';
    list.appendChild(tableDiv);
  });
}

function showRegion(region) {
  regions.forEach(r => {
    const el = document.getElementById(`region-${r}`);
    if (el) el.style.display = (r === region ? '' : 'none');
  });
}

// 等 DOM 加载完成再执行
document.addEventListener('DOMContentLoaded', () => {
  render();
});
