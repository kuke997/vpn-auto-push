fetch("output/nodes.json")
  .then(res => res.json())
  .then(data => {
    const list = document.getElementById("vpn-list-section");
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
  });

