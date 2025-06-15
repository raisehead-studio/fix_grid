document.addEventListener("DOMContentLoaded", () => {
  fetchReports();
});

let power_data = {};

async function fetchReports() {
  const res = await fetch('/api/power_reports');
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
    const taipowerBody = document.getElementById('taipower-table-body');
    if (index == 0) {
      taipowerBody.innerHTML = '';
    }
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
}
