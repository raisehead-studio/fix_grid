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

let power_data = {};

async function fetchReports() {
  const res = await fetch('/api/power_reports');
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
  const taipowerBody = document.getElementById('taipower-table-body');
  taipowerBody.innerHTML = '';

  data.forEach((entry, index) => {
    if (entry.taipower_status === 1) return;
    power_data[entry.id] = entry
    // 左表格：回報
    const reportRow = document.createElement('tr');
    reportRow.className = "border-b";
    reportRow.innerHTML = `
      <td>${entry.id}</td>
      <td>${entry.district}</td>
      <td>${entry.village}</td>
      <td>${entry.location}</td>
      <td>${entry.reason}</td>
      <td>${entry.count}</td>
      <td>${entry.contact}</td>
      <td>${entry.phone}</td>
      <td>${entry.created_at}</td>
    `;
    reportBody.appendChild(reportRow);

    // 右表格：台電狀態
    const statusRow = document.createElement('tr');
    statusRow.className = "border-b";
    statusRow.innerHTML = `
      <td>${entry.taipower_description || '-'}</td>
      <td>${
        entry.taipower_eta_hours
          ? `<span class="${entry.taipower_eta_hours > 24 ? 'text-red-600 font-bold' : ''}">
              ${entry.taipower_eta_hours} 小時
            </span>`
          : '-'
      }</td>
      <td>${entry.taipower_support || '-'}</td>
    `;
    taipowerBody.appendChild(statusRow);
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      syncRowHeights("#report-table-body tr", "#taipower-table-body tr");
    });
  }, 0);
}

function exportToExcel() {
  const exportData = filteredReports.filter(e => e.taipower_status !== 1);
  if (exportData.length === 0) {
    alert("目前沒有可匯出的資料！");
    return;
  }

  const dataRows = exportData.map(e => {
    const eta = e.taipower_eta_hours;
    const isOver24h = eta != null && eta > 24;

    return [
      e.district,
      e.village,
      e.location,
      e.count,
      e.reason,
      e.contact,
      e.phone,
      e.created_at,
      e.taipower_description || "",
      e.taipower_support || "",
      eta != null ? (isOver24h ? "是" : "否") : ""
    ];
  });

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0];
  const filename = `(表四)台電支援需求彙整表_${timestamp}.xlsx`;

  fetch("/api/export-excel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template: "sheet4.xlsx",
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
    'id', 'district', 'village', 'location', 'reason', 'count', 'contact', 'phone', 'created_at',
    'taipower_description', 'taipower_eta_hours', 'taipower_support', 'taipower_restored_at'
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
