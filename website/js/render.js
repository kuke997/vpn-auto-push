// 渲染 VPN 节点列表
fetch("nodes.json")
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! 状态码: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    const list = document.getElementById("vpn-list-section");
    if (!data || data.length === 0) {
      list.innerHTML = "<p>暂无节点数据</p>";
      return;
    }

    data.forEach((node, i) => {
      const div = document.createElement("div");
      div.className = "vpn-item";
      div.innerHTML = `
        <h3>订阅 ${i + 1}</h3>
        <div class="country">通用</div>
        <div class="info">支持协议：Clash/V2Ray/SS</div>
        <button onclick="window.open('${node.url}', '_blank')">下载配置</button>
      `;
      list.appendChild(div);
    });
  })
  .catch(error => {
    console.error("加载节点数据失败:", error);
    const list = document.getElementById("vpn-list-section");
    list.innerHTML = `<p style="color:red;">加载节点数据失败: ${error.message}</p>`;
  });
