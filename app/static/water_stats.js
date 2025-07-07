let sortField = '';
let sortOrder = 'asc';
let filteredReports = [];

function syncRowHeights(leftSelector, rightSelector) {
  const leftRows = document.querySelectorAll(leftSelector);
  const rightRows = document.querySelectorAll(rightSelector);

  const rowCount = Math.min(leftRows.length, rightRows.length);

  for (let i = 0; i < rowCount; i++) {
    const leftHeight = leftRows[i].getBoundingClientRect().height;
    const rightHeight = rightRows[i].getBoundingClientRect().height;
    const maxHeight = Math.max(leftHeight, rightHeight);

    leftRows[i].style.height = `${maxHeight}px`;
    rightRows[i].style.height = `${maxHeight}px`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchReports();
});

document.getElementById('filterDistrict').addEventListener('change', () => fetchReports());
document.getElementById('filterVillage').addEventListener('change', () => fetchReports());

let water_data = {};

async function fetchReports() {
  const res = await fetch('/api/water_reports');
  const canViewStatus = userPermissions.includes("view_status");
  let data = await res.json();

  // 取得排序與篩選設定
  const selectedDistrict = document.getElementById('filterDistrict').value;
  const selectedVillage = document.getElementById('filterVillage').value;
  
  // 篩選處理
  if (selectedDistrict && selectedDistrict != "") {
    data = data.filter(e => e.district_id == selectedDistrict);
  }
  if (selectedVillage && selectedVillage != "") {
    data = data.filter(e => e.village_id == selectedVillage);
  }

  if (canViewStatus) {
    const mismatchOnly = document.getElementById('filterMismatch').checked;
    if (mismatchOnly) {
      data = data.filter(e => e.report_status !== e.taiwater_status);
    }
  }

  // 排序處理
  if (sortField) {
    data.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  filteredReports = data;
  const reportBody = document.getElementById('report-table-body');
  reportBody.innerHTML = '';

  data.forEach((entry, index) => {
    water_data[entry.id] = entry
    // 左表格：回報
    const reportRow = document.createElement('tr');
    reportRow.className = "border-b";
    reportRow.innerHTML = `
      <td>${entry.id}</td>
      <td>${entry.district}</td>
      <td>${entry.village}</td>
      <td>${entry.location}</td>
      <td>${entry.water_station === '是' ? '是' : '否'}</td>
      <td>${entry.taiwater_water_station_status === '是' ? '是' : '否'}</td>
      <td>${
        entry.taiwater_eta_hours
          ? `<span class="${entry.taiwater_eta_hours > 24 ? 'text-red-600 font-bold' : ''}">
              ${entry.taiwater_eta_hours} 小時
            </span>`
          : '-'
      }</td>
    `;
    reportBody.appendChild(reportRow);
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      syncRowHeights("#report-table-body tr", "#taipower-table-body tr");
    });
  }, 0);
}

function exportToExcel() {
  if (filteredReports.length === 0) {
    alert("目前沒有資料可以匯出！");
    return;
  }

  const rows = [[
    "序號", "行政區", "里", "地點", "需加水站", "已設加水站", "預估修復時間"
  ]];

  filteredReports.forEach(entry => {
    rows.push([
      entry.id,
      entry.district,
      entry.village,
      entry.location,
      entry.water_station === '是' ? '是' : '否',
      entry.taiwater_water_station_status === '是' ? '是' : '否',
      entry.taiwater_eta_hours != null ? `${entry.taiwater_eta_hours} 小時` : '-'
    ]);
  });

  const ws = XLSX.utils.aoa_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "停水彙整");

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0]; // e.g. 2025-06-29-18-22-10
  const filename = `停水彙整_${timestamp}.xlsx`;

  XLSX.writeFile(wb, filename);
}

window.onload = async () => {
  loadFilterDistricts()
}

async function loadFilterDistricts() {
  const districts = await fetch('/api/districts').then(res => res.json());
  const districtSelect = document.getElementById('filterDistrict');
  districtSelect.innerHTML = `<option value="">全部</option>`
  districts.forEach(d => districtSelect.innerHTML += `<option value="${d.id}">${d.name}</option>`);
  document.getElementById('filterDistrict').addEventListener('change', e => loadFilterVillages(e.target.value));
}

async function loadFilterVillages(districtId) {
  const res = await fetch(`/api/villages/${districtId}`);
  const villages = await res.json();
  const villageSelect = document.getElementById('filterVillage');
  villageSelect.innerHTML = '<option value="">全部</option>';
  villages.forEach(v => villageSelect.innerHTML += `<option value="${v.id}">${v.name}</option>`);
}

function clearFilters() {
  sortField = '';
  sortOrder = 'asc';
  document.getElementById('filterDistrict').value = '';
  document.getElementById('filterVillage').innerHTML = '<option value="">全部</option>';
  fetchReports();
}

function setSort(field) {
  if (sortField === field) {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  } else {
    sortField = field;
    sortOrder = 'asc';
  }
  updateSortIndicators();
  fetchReports();
}

function updateSortIndicators() {
  const fields = [
    'id', 'district', 'village', 'location', 'reason', 'count', 'contact', 'phone', 'created_at', 'report_status',
    'water_station', 'taiwater_water_station_status', 'taiwater_eta_hours'
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
