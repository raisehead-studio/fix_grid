let power_data = [];
let chart = null;
let mode = 'district'; // 預設分類模式

document.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch('/api/power_stats');
  power_data = await res.json();
  switchMode(mode);
});

function switchMode(newMode) {
  mode = newMode;
  renderData();

  const btnVillage = document.getElementById("btn-village");
  const btnDistrict = document.getElementById("btn-district");

  if (mode === "village") {
    btnVillage.className = "px-4 py-2 bg-blue-600 text-white rounded";
    btnDistrict.className = "px-4 py-2 bg-gray-600 text-white rounded";
  } else {
    btnVillage.className = "px-4 py-2 bg-gray-600 text-white rounded";
    btnDistrict.className = "px-4 py-2 bg-blue-600 text-white rounded";
  }
}



function renderData() {
  if (mode === 'village') renderByVillage();
  else renderByDistrict();
}

function renderByVillage() {
  const tableLeft = document.getElementById('left-table-body');
  const tableRight = document.getElementById('right-table-body');
  const leftTableHead = document.getElementById('left-table-head');
  const rightTableHead = document.getElementById('right-table-head');

  leftTableHead.innerHTML = `<tr><th>里</th><th>停電戶數</th></tr>`;
  rightTableHead.innerHTML = `<tr><th>停電戶數</th></tr>`;
  tableLeft.innerHTML = '';
  tableRight.innerHTML = '';

  // 整合資料
  const villageMap = new Map();
  power_data.forEach(row => {
    const key = row.village;
    if (!villageMap.has(key)) {
      villageMap.set(key, {
        village: row.village,
        gov: 0,
        tp: 0
      });
    }
    const data = villageMap.get(key);
    data.gov += row.gov_count || 0;
    data.tp += row.tp_count || 0;
  });

  // 排序
  const sorted = [...villageMap.values()].sort((a, b) => Math.max(b.gov, b.tp) - Math.max(a.gov, a.tp));

  const labels = [], values = [], tp_values = [];

  sorted.forEach(({ village, gov, tp }) => {
    labels.push(village);
    values.push(gov);
    tp_values.push(tp);

    const tr1 = document.createElement('tr');
    tr1.className = "border-t border-b";
    tr1.innerHTML = `<td>${village}</td><td>${gov}</td>`;
    tableLeft.appendChild(tr1);

    const tr2 = document.createElement('tr');
    tr2.className = "border-t border-b";
    tr2.innerHTML = `<td>${tp}</td>`;
    tableRight.appendChild(tr2);
  });

  renderChart(labels, values, tp_values);
}

function renderByDistrict() {
  const tableLeft = document.getElementById('left-table-body');
  const tableRight = document.getElementById('right-table-body');
  const leftTableHead = document.getElementById('left-table-head');
  const rightTableHead = document.getElementById('right-table-head');

  leftTableHead.innerHTML = `<tr><th class="w-[6ch]">行政區</th><th>里</th><th class="w-[8ch]">停電戶數</th></tr>`;
  rightTableHead.innerHTML = `<tr><th>里</th><th class="w-[8ch]">台電戶數</th></tr>`;
  tableLeft.innerHTML = '';
  tableRight.innerHTML = '';

  const govMap = new Map(); // Map<區名, { count, Set<里> }>
  const tpMap = new Map();  // Map<區名, { count, Set<里> }>

  power_data.forEach(row => {
    const district = row.district;
    const village = row.village;
    const gov = row.gov_count || 0;
    const tp = row.tp_count || 0;

    if (gov > 0) {
      if (!govMap.has(district)) {
        govMap.set(district, { count: 0, villages: new Set() });
      }
      govMap.get(district).count += gov;
      govMap.get(district).villages.add(village);
    }

    if (tp > 0) {
      if (!tpMap.has(district)) {
        tpMap.set(district, { count: 0, villages: new Set() });
      }
      tpMap.get(district).count += tp;
      tpMap.get(district).villages.add(village);
    }
  });

  // 統整所有出現過的行政區
  const allDistricts = new Set([...govMap.keys(), ...tpMap.keys()]);
  const rows = [];

  allDistricts.forEach(district => {
    const govData = govMap.get(district);
    const tpData = tpMap.get(district);

    const govCount = govData?.count || 0;
    const tpCount = tpData?.count || 0;

    const govVillages = govData ? [...govData.villages].sort().join('、') : '';
    const tpVillages = tpData ? [...tpData.villages].sort().join('、') : '';

    rows.push({
      district,
      govCount,
      govVillages,
      tpCount,
      tpVillages
    });
  });

  // 排序：依左右最大值排序
  rows.sort((a, b) => Math.max(b.govCount, b.tpCount) - Math.max(a.govCount, a.tpCount));

  const labels = [], govValues = [], tpValues = [];

  rows.forEach(row => {
    labels.push(row.district);
    govValues.push(row.govCount);
    tpValues.push(row.tpCount);

    const trLeft = document.createElement('tr');
    trLeft.className = "border-t border-b";
    trLeft.innerHTML = `<td>${row.district}</td><td>${row.govVillages}</td><td>${row.govCount}</td>`;
    tableLeft.appendChild(trLeft);

    const trRight = document.createElement('tr');
    trRight.className = "border-t border-b";
    trRight.innerHTML = `<td>${row.tpVillages}</td><td>${row.tpCount}</td>`;
    tableRight.appendChild(trRight);
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      // 同步表體高度
      syncRowHeightsDelayed("#left-table-body tr", "#right-table-body tr");
      // 同步表頭高度
      syncTheadHeightsDelayed("#left-table-head", "#right-table-head");
    });
  }, 0);

  renderChart(labels, govValues, tpValues);
}

function renderChart(labels, data1, data2) {
  const ctx = document.getElementById('power-chart').getContext('2d');
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: '公所回報停電戶數',
          data: data1,
          backgroundColor: 'rgba(255, 99, 132, 0.6)',
        },
        {
          label: '台電公司官網戶數',
          data: data2,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
      },
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

function exportToExcel() {
  const govMap = new Map();
  const tpMap = new Map();

  power_data.forEach(row => {
    const district = row.district;
    const village = row.village;
    const gov = row.gov_count || 0;
    const tp = row.tp_count || 0;

    if (gov > 0) {
      if (!govMap.has(district)) {
        govMap.set(district, { count: 0, villages: new Set() });
      }
      govMap.get(district).count += gov;
      govMap.get(district).villages.add(village);
    }

    if (tp > 0) {
      if (!tpMap.has(district)) {
        tpMap.set(district, { count: 0, villages: new Set() });
      }
      tpMap.get(district).count += tp;
      tpMap.get(district).villages.add(village);
    }
  });

  const allDistricts = new Set([...govMap.keys(), ...tpMap.keys()]);
  const rows = [];

  allDistricts.forEach(district => {
    const govData = govMap.get(district);
    const tpData = tpMap.get(district);

    const govCount = govData?.count || 0;
    const tpCount = tpData?.count || 0;

    const mergedVillagesSet = new Set([
      ...(govData?.villages || []),
      ...(tpData?.villages || [])
    ]);
    const mergedVillages = [...mergedVillagesSet].sort().join('、');

    rows.push({
      district,
      mergedVillages,
      govCount,
      tpCount
    });
  });

  // ✅ 排序邏輯：依左右表中較大者為準
  rows.sort((a, b) => Math.max(b.govCount, b.tpCount) - Math.max(a.govCount, a.tpCount));

  const dataRows = rows.map(row => [
    row.district,
    row.mergedVillages,
    row.govCount,
    row.tpCount
  ]);

  if (dataRows.length === 0) {
    alert("目前沒有資料可以匯出！");
    return;
  }

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0];
  const filename = `(表五)停電彙整表(報告上級)_${timestamp}.xlsx`;

  fetch("/api/export-excel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template: "sheet5.xlsx",
      filename,
      data: dataRows,
      start_row: 5,
      start_col: 2
    })
  })
    .then(res => {
      if (!res.ok) return res.json().then(err => { throw new Error(err.error); });
      return res.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch(err => {
      alert("匯出失敗：" + err.message);
    });
}

function exportToExcelViaBackend() {
  fetch("/api/power_reports/export-power-report", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      data: power_data
    })
  })
  .then(response => response.blob())
  .then(blob => {
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0];
    const filename = `停電統計_${timestamp}.xlsx`;

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  });
}

// 台電回報 modal
function showTaipowerModal() {
  document.getElementById('taipowerModal').classList.remove('hidden');
  loadDistrictsForTaipower();
}
function hideTaipowerModal() {
  document.getElementById('taipowerModal').classList.add('hidden');
}
async function loadDistrictsForTaipower() {
  const res = await fetch('/api/districts');
  const data = await res.json();
  const select = document.getElementById('taipowerDistrict');
  select.innerHTML = data.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  loadVillagesForTaipower();
}
async function loadVillagesForTaipower() {
  const districtId = document.getElementById('taipowerDistrict').value;
  const res = await fetch(`/api/villages/${districtId}`);
  const data = await res.json();
  const select = document.getElementById('taipowerVillage');
  select.innerHTML = data.map(v => `<option value="${v.id}">${v.name}</option>`).join('');
}
async function submitTaipowerReport() {
  const payload = {
    district_id: document.getElementById('taipowerDistrict').value,
    village_id: document.getElementById('taipowerVillage').value,
    count: parseInt(document.getElementById('taipowerCount').value)
  };
  await fetch('/api/taipower_reports', {
    method: 'POST',
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  hideTaipowerModal();
  location.reload();
}
