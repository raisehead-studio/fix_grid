let power_data = [];
let chart = null;
let mode = 'village'; // 預設分類模式

document.addEventListener("DOMContentLoaded", async () => {
  const res = await fetch('/api/power_reports');
  power_data = await res.json();
  renderData();
});

function switchMode(newMode) {
  mode = newMode;
  renderData();
}

function syncRowHeights(leftSelector, rightSelector) {
  const leftRows = document.querySelectorAll(leftSelector);
  const rightRows = document.querySelectorAll(rightSelector);

  leftRows.forEach((leftRow, i) => {
    const height = leftRow.getBoundingClientRect().height;
    console.log(height)
    rightRows[i].style.height = `${height}px`;
  });
}

function randomOffset(base, range = 2) {
  return base + Math.floor(Math.random() * (range * 2 + 1)) - range;
}

function renderData() {
  if (mode === 'village') renderByVillage();
  else renderByDistrict();
}

function renderByVillage() {
  const tableLeft = document.getElementById('left-table-body');
  const tableRight = document.getElementById('right-table-body');
  const tableHead = document.getElementById('left-table-head');

  tableHead.innerHTML = `<tr><th>里</th><th>停電戶數</th></tr>`;
  tableLeft.innerHTML = '';
  tableRight.innerHTML = '';

  const villageMap = {};

  power_data.forEach(entry => {
    if (!villageMap[entry.village]) villageMap[entry.village] = 0;
    villageMap[entry.village] += entry.count;
  });

  const labels = [];
  const values = [];
  const taipowerDefaults = [];

  Object.entries(villageMap).forEach(([village, count]) => {
    labels.push(village);
    values.push(count);
    const taipower = randomOffset(count, 2);
    taipowerDefaults.push(taipower);

    const tr1 = document.createElement('tr');
    tr1.className = "border-t border-b";
    tr1.innerHTML = `<td>${village}</td><td>${count}</td>`;
    tableLeft.appendChild(tr1);

    const tr2 = document.createElement('tr');
    tr2.className = "border-t border-b";
    tr2.innerHTML = `<td>${taipower}</td>`;
    tableRight.appendChild(tr2);
  });

  renderChart(labels, values, taipowerDefaults);
}

function renderByDistrict() {
  const tableLeft = document.getElementById('left-table-body');
  const tableRight = document.getElementById('right-table-body');
  const tableHead = document.getElementById('left-table-head');

  tableHead.innerHTML = `<tr><th class="w-[6ch]">行政區</th><th>里</th><th class="w-[8ch]">停電戶數</th></tr>`;
  tableLeft.innerHTML = '';
  tableRight.innerHTML = '';

  const districtMap = {};

  power_data.forEach(entry => {
    if (!districtMap[entry.district]) {
      districtMap[entry.district] = { villages: new Set(), count: 0 };
    }
    districtMap[entry.district].villages.add(entry.village);
    districtMap[entry.district].count += entry.count;
  });

  const labels = [];
  const values = [];
  const taipowerDefaults = [];

  Object.entries(districtMap).forEach(([district, data]) => {
    const villageStr = [...data.villages].join('、');
    const count = data.count;

    labels.push(district);
    values.push(count);
    const taipower = randomOffset(count, 2);
    taipowerDefaults.push(taipower);

    const tr1 = document.createElement('tr');
    tr1.className = "border-t border-b";
    tr1.innerHTML = `<td>${district}</td><td>${villageStr}</td><td>${count}</td>`;
    tableLeft.appendChild(tr1);

    const tr2 = document.createElement('tr');
    tr2.className = "border-t border-b";
    tr2.innerHTML = `<td>${taipower}</td>`;
    tableRight.appendChild(tr2);
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      syncRowHeights("#left-table-body tr", "#right-table-body tr");
    });
  }, 0);
  renderChart(labels, values, taipowerDefaults);
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
