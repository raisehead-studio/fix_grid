let sortField = '';
let sortOrder = 'asc';
let reportStatusFilter = 'all';    // 'all' | 'restored' | 'unrestored'
let taipowerStatusFilter = 'all';  // 'all' | 'restored' | 'unrestored'

function cycleReportStatusFilter(event) {
  event.stopPropagation();  // 防止觸發排序
  const btn = document.getElementById('filterBtnReportStatus');
  if (reportStatusFilter === 'all') {
    reportStatusFilter = 1;
    btn.textContent = '⭕️';
  } else if (reportStatusFilter === 1) {
    reportStatusFilter = 0;
    btn.textContent = '❌';
  } else {
    reportStatusFilter = 'all';
    btn.textContent = '❓';
  }
  fetchReports();
}

function cycleTaipowerStatusFilter(event) {
  event.stopPropagation();  // 防止觸發排序
  const btn = document.getElementById('filterBtnTaipowerStatus');
  if (taipowerStatusFilter === 'all') {
    taipowerStatusFilter = 1;
    btn.textContent = '⭕️';
  } else if (taipowerStatusFilter === 1) {
    taipowerStatusFilter = 0;
    btn.textContent = '❌';
  } else {
    taipowerStatusFilter = 'all';
    btn.textContent = '❓';
  }
  fetchReports();
}

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

function openReportModal() {
  document.getElementById('reportModal').classList.remove('hidden');

  // 預填使用者資料
  document.getElementById('district').value = currentUser.district;
  document.getElementById('contact_name').value = currentUser.full_name;
  document.getElementById('contact_phone').value = currentUser.phone;

  // 載入對應的里選單
  loadVillages(currentUser.district_id).then(() => {
    document.getElementById('village').value = currentUser.village_id;
  });
}

function closeReportModal() {
  document.getElementById('reportModal').classList.add('hidden');
}

async function loadVillages(districtId) {
  const res = await fetch(`/api/villages/${districtId}`);
  const villages = await res.json();
  const villageSelect = document.getElementById('village');
  villageSelect.innerHTML = '';
  villages.forEach(v => {
    villageSelect.innerHTML += `<option value="${v.id}">${v.name}</option>`;
  });
}

function submitReport(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  fetch("/api/power_reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  }).then(res => {
    if (res.ok) {
      closeReportModal();
      location.reload();
    } else {
      alert("回報失敗！");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  fetchReports();
});

const canViewStatus = userPermissions.includes("view_status");
document.getElementById('filterDistrict').addEventListener('change', () => fetchReports());
document.getElementById('filterVillage').addEventListener('change', () => fetchReports());
if (canViewStatus) {
  document.getElementById('filterMismatch').addEventListener('change', () => fetchReports());
}

let power_data = {};
let filteredReports = [];

async function fetchReports() {
  const res = await fetch('/api/power_reports');
  let data = await res.json();

  let hideReportEdit = data.every(e => e.report_status);
  let hideTaipowerEdit = data.every(e => e.taipower_status);

  // 控制 <th> 顯示與否
  document.getElementById('th-edit-report').style.display = hideReportEdit ? 'none' : '';
  if (userPermissions.includes("view_status")) {
    document.getElementById('th-edit-taipower').style.display = hideTaipowerEdit ? 'none' : '';
  }

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
      data = data.filter(e => e.report_status !== e.taipower_status);
    }
  }

  // 狀態篩選
  if (reportStatusFilter !== 'all') {
    console.log(data[0])
    const target = reportStatusFilter === 1;
    data = data.filter(e => e.report_status == target);
  }
  if (canViewStatus && taipowerStatusFilter !== 'all') {
    const target = taipowerStatusFilter === 1;
    data = data.filter(e => e.taipower_status == target);
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

  filteredReports = data;  // 存入供匯出用的資料
  const reportBody = document.getElementById('report-table-body');
  reportBody.innerHTML = '';
  if (canViewStatus) {
    const taipowerBody = document.getElementById('taipower-table-body');
    taipowerBody.innerHTML = '';
  }

  data.forEach((entry, index) => {
    power_data[entry.id] = entry
    // 左表格：回報
    const reportRow = document.createElement('tr');
    const canEditReport = userPermissions.includes("edit_report");
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
      <td class="whitespace-nowrap">${entry.created_at}</td>
      <td>
        ${entry.report_status 
          ? '<span class="text-green-600 whitespace-nowrap">已復電</span>' 
          : (canEditReport 
              ? `<button onclick="confirmReportRestore(${entry.id})" class="text-red-600 underline whitespace-nowrap">未復電</button>` 
              : '<span class="text-red-600 whitespace-nowrap">未復電</span>')}
      </td>
      <td class="text-center">
        ${!entry.report_status && canEditReport 
          ? `<button onclick="openEditReport(${entry.id})" class="text-blue-600">✏️</button>` 
          : ''}
      </td>
    `;
    reportBody.appendChild(reportRow);

    // 右表格：台電狀態
    if (canViewStatus) {
      const canEditStatus = userPermissions.includes("edit_status");
      const taipowerBody = document.getElementById('taipower-table-body');
      const statusRow = document.createElement('tr');
      statusRow.className = "border-b";
      statusRow.innerHTML = `
        <td>
          ${entry.taipower_status 
            ? '<span class="text-green-600 whitespace-nowrap">已復電</span>' 
            : (canEditStatus 
                ? `<button onclick="confirmStatusRestore(${entry.id})" class="text-red-600 underline whitespace-nowrap">未復電</button>` 
                : '<span class="text-red-600 whitespace-nowrap">未復電</span>')}
        </td>
        <td>
          <div class="whitespace-pre-line overflow-x-auto overflow-y-auto max-h-[6em] max-w-[10em]">${entry.taipower_description || '-'}</div>
        </td>
        <td>${
          entry.taipower_eta_hours
            ? `<span class="${entry.taipower_eta_hours > 24 ? 'text-red-600 font-bold' : ''}">
                ${entry.taipower_eta_hours} 小時
              </span>`
            : '-'
        }</td>
        <td>${entry.taipower_support || '-'}</td>
        <td class="whitespace-nowrap">${entry.taipower_restored_at ? entry.taipower_restored_at : '-'}</td>
        <td class="text-center">
          ${!entry.taipower_status && canEditStatus 
            ? `<button onclick="openEditStatus(${entry.id})" class="text-blue-600">✏️</button>` 
            : ''}
        </td>
      `;
      taipowerBody.appendChild(statusRow);
    }
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      syncRowHeights("#report-table-body tr", "#taipower-table-body tr");
    });
  }, 0);
}

// export excel
function exportToExcel() {
  if (filteredReports.length === 0) {
    alert("目前沒有資料可以匯出！");
    return;
  }

  const includeTaipower = canViewStatus;
  const rows = [[
    "序號", "行政區", "里", "地點", "停電原因", "停電戶數",
    "聯絡人", "電話", "通報時間", "狀態"
  ]];

  if (includeTaipower) {
    rows[0].push("台電狀態", "台電說明", "預估修復時間", "支援內容", "台電更新時間");
  }

  filteredReports.forEach(e => {
    const row = [
      e.id,
      e.district,
      e.village,
      e.location,
      e.reason,
      e.count,
      e.contact,
      e.phone,
      e.created_at,
      e.report_status ? "已復電" : "未復電"
    ];

    if (includeTaipower) {
      row.push(
        e.taipower_status ? "已復電" : "未復電",
        e.taipower_description || "-",
        e.taipower_eta_hours != null ? `${e.taipower_eta_hours} 小時` : "-",
        e.taipower_support || "-",
        e.taipower_restored_at || "-"
      );
    }

    rows.push(row);
  });

  const ws = XLSX.utils.aoa_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "停電彙整");

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0];  // yyyy-mm-dd-HH-MM-SS
  const filename = `停電彙整_${timestamp}.xlsx`;

  XLSX.writeFile(wb, filename);
}

// Modals

let currentEditingReportId = null;
let currentEditingStatusId = null;

function openEditReport(entry_id) {
  entry = power_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('edit-location').value = entry.location || '';
  document.getElementById('edit-reason').value = entry.reason || '';
  document.getElementById('edit-count').value = entry.count || 1;
  document.getElementById('edit-contact').value = entry.contact || '';
  document.getElementById('edit-phone').value = entry.phone || '';
  document.getElementById('editReportModal').classList.remove('hidden');
}

function submitEditReport() {
  const payload = {
    location: document.getElementById('edit-location').value,
    reason: document.getElementById('edit-reason').value,
    count: parseInt(document.getElementById('edit-count').value),
    contact_name: document.getElementById('edit-contact').value,
    contact_phone: document.getElementById('edit-phone').value
  };
  fetch(`/api/power_reports/${currentEditingReportId}/update_report`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  }).then(() => {
    closeModal('editReportModal');
    fetchReports();
  });
}

function openEditStatus(entry_id) {
  entry = power_data[entry_id]
  currentEditingStatusId = entry.id;
  document.getElementById('edit-description').value = entry.taipower_description || '';
  document.getElementById('edit-estimate-hour').value = entry.taipower_eta_hours || '';
  document.getElementById('edit-support').value = entry.taipower_support || '';
  document.getElementById('editStatusModal').classList.remove('hidden');
}

function submitEditStatus() {
  const payload = {
    taipower_note: document.getElementById('edit-description').value,
    taipower_eta_hours: parseInt(document.getElementById('edit-estimate-hour').value),
    taipower_support: document.getElementById('edit-support').value
  };
  fetch(`/api/power_reports/${currentEditingStatusId}/update_taipower`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  }).then(() => {
    closeEditStatusModal();
    fetchReports();
  });
}

function confirmReportRestore(entry_id) {
  entry = power_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('confirmReportText').innerHTML = `
  ⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 供電狀態？<br><br>
  此操作將立即生效，確認後將無法修改或復原。<br>
  請再次確認設定是否正確。`;
  document.getElementById('confirmReportRestoreModal').classList.remove('hidden');
}

function submitReportRestore() {
  fetch(`/api/power_reports/${currentEditingReportId}/toggle_report_status`, {
    method: 'POST'
  }).then(() => {
    closeConfirmReportRestore();
    fetchReports();
  });
}

function confirmStatusRestore(entry_id) {
  entry = power_data[entry_id]
  currentEditingStatusId = entry.id;
  document.getElementById('confirmStatusText').innerHTML = `
  ⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 供電狀態？<br><br>
  此操作將立即生效，確認後將無法修改或復原。<br>
  請再次確認設定是否正確。`;
  document.getElementById('confirmStatusRestoreModal').classList.remove('hidden');
}

function submitStatusRestore() {
  fetch(`/api/power_reports/${currentEditingStatusId}/toggle_taipower_status`, {
    method: 'POST'
  }).then(() => {
    closeConfirmStatusRestore();
    fetchReports();
  });
}

function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}
function closeEditReportModal() {
  closeModal('editReportModal');
}
function closeEditStatusModal() {
  closeModal('editStatusModal');
}
function closeConfirmReportRestore() {
  closeModal('confirmReportRestoreModal');
}
function closeConfirmStatusRestore() {
  closeModal('confirmStatusRestoreModal');
}

function checkModalClick(event, modalId) {
  const modal = document.getElementById(modalId);
  if (event.target === modal) {
    modal.classList.add("hidden");
  }
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
  reportStatusFilter = 'all';
  taipowerStatusFilter = 'all';
  document.getElementById('filterBtnReportStatus').textContent = '❓';
  document.getElementById('filterDistrict').value = '';
  document.getElementById('filterVillage').innerHTML = '<option value="">全部</option>';
  if (canViewStatus) {
    document.getElementById('filterMismatch').checked = false;
    document.getElementById('filterBtnTaipowerStatus').textContent = '❓';
  }
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
    'taipower_status', 'taipower_description', 'taipower_eta_hours', 'taipower_support', 'taipower_restored_at'
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
