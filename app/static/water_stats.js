document.addEventListener("DOMContentLoaded", () => {
  fetchReports();
});

let water_data = {};

async function fetchReports() {
  const res = await fetch('/api/water_reports');
  const canViewStatus = userPermissions.includes("view_status");
  let data = await res.json();

  // 取得排序與篩選設定
  const selectedSortField = document.getElementById('sortField').value;
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
  if (selectedSortField) {
    data.sort((a, b) => {
      let aVal = a[selectedSortField];
      let bVal = b[selectedSortField];

      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }

  const reportBody = document.getElementById('report-table-body');
  reportBody.innerHTML = '';

  data.forEach((entry, index) => {
    water_data[entry.id] = entry
    // 左表格：回報
    const reportRow = document.createElement('tr');
    const canEditReport = userPermissions.includes("edit_report");
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
}
