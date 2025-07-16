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

function openReportModal() {
  document.getElementById('reportModal').classList.remove('hidden');

  // 預填使用者資料
  document.getElementById('contact_name').value = currentUser.full_name;
  document.getElementById('contact_phone').value = currentUser.phone;
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

  fetch("/api/taiwater_power_reports", {
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
if (canViewStatus) {
  document.getElementById('filterMismatch').addEventListener('change', () => fetchReports());
}

let power_data = {};

async function fetchReports() {
  const res = await fetch('/api/taiwater_power_reports');
  let data = await res.json();

  let hideReportEdit = data.every(e => e.report_status);
  let hideTaipowerEdit = data.every(e => e.taipower_status);

  // 控制 <th> 顯示與否
  const canEditReport = userPermissions.includes("edit_report");
  document.getElementById('th-edit-report').style.display = (hideReportEdit || !canEditReport) ? 'none' : '';
  if (userPermissions.includes("view_status")) {
    document.getElementById('th-edit-taipower').style.display = hideTaipowerEdit ? 'none' : '';
  }

  // 篩選處理
  if (canViewStatus) {
    const mismatchOnly = document.getElementById('filterMismatch').checked;
    if (mismatchOnly) {
      data = data.filter(e => {
        const r = e.report_status;
        const t = e.taipower_status;

        const bothOne = r == 1 && t == 1;
        const bothNotOne = r != 1 && t != 1;

        return !(bothOne || bothNotOne);  // 不是一致 → 是不一致
      });
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
  const taipowerBody = document.getElementById('taipower-table-body');
  if (canViewStatus) {
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
      <td>${entry.facility}</td>
      <td>${entry.pole_number}</td>
      <td>${entry.electricity_number}</td>
      <td>${entry.reason}</td>
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
      const statusRow = document.createElement('tr');
      statusRow.className = "border-b";
      statusRow.innerHTML = `
        <td>
          ${
            entry.taipower_status === 1
              ? '<span class="text-green-600 whitespace-nowrap">已復電</span>'
              : canEditStatus
                ? `<button onclick="confirmStatusRestore(${entry.id})" class="${
                    entry.taipower_status === 0 ? 'text-yellow-600' : 'text-gray-600'
                  } underline whitespace-nowrap">${
                    entry.taipower_status === 0 ? '搶修中' : '✏️'
                  }</button>`
                : `<span class="${
                    entry.taipower_status === 0 ? 'text-yellow-600' : 'text-gray-600'
                  } whitespace-nowrap">${
                    entry.taipower_status === 0 ? '搶修中' : '尚無狀態'
                  }</span>`
          }
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

function exportToExcel() {
  if (filteredReports.length === 0) {
    alert("目前沒有資料可以匯出！");
    return;
  }

  const includeTaipower = canViewStatus;

  const rows = [[
    "序號", "設施名稱", "桿號", "電號", "停電原因", "聯絡人", "電話", "通報時間", "狀態"
  ]];

  if (includeTaipower) {
    rows[0].push("台電狀態", "說明", "預估修復時間", "支援內容", "更新時間");
  }

  filteredReports.forEach(e => {
    const row = [
      e.id,
      e.facility,
      e.pole_number,
      e.electricity_number,
      e.reason,
      e.contact,
      e.phone,
      e.created_at,
      e.report_status ? '已復電' : '未復電'
    ];

    if (includeTaipower) {
      row.push(
        e.taipower_status ? '已復電' : '未復電',
        e.taipower_description || '-',
        e.taipower_eta_hours != null ? `${e.taipower_eta_hours} 小時` : '-',
        e.taipower_support || '-',
        e.taipower_restored_at || '-'
      );
    }

    rows.push(row);
  });

  const ws = XLSX.utils.aoa_to_sheet(rows);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "台水停電通報");

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0]; // 例如 2025-06-29-15-00-00
  const filename = `台水停電通報_${timestamp}.xlsx`;

  XLSX.writeFile(wb, filename);
}

// Modals

let currentEditingReportId = null;
let currentEditingStatusId = null;

function openEditReport(entry_id) {
  entry = power_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('edit-facility').value = entry.facility || '';
  document.getElementById('edit-pole-number').value = entry.pole_number || '';
  document.getElementById('edit-electricity-number').value = entry.electricity_number || '';
  document.getElementById('edit-reason').value = entry.reason || '';
  document.getElementById('edit-contact').value = entry.contact || '';
  document.getElementById('edit-phone').value = entry.phone || '';
  document.getElementById('editReportModal').classList.remove('hidden');
}

function submitEditReport() {
  const payload = {
    facility: document.getElementById('edit-facility').value,
    pole_number: document.getElementById('edit-pole-number').value,
    electricity_number: document.getElementById('edit-electricity-number').value,
    reason: document.getElementById('edit-reason').value,
    contact_name: document.getElementById('edit-contact').value,
    contact_phone: document.getElementById('edit-phone').value
  };
  fetch(`/api/taiwater_power_reports/${currentEditingReportId}/update_report`, {
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
  fetch(`/api/taiwater_power_reports/${currentEditingStatusId}/update_taipower`, {
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
  fetch(`/api/taiwater_power_reports/${currentEditingReportId}/toggle_report_status`, {
    method: 'POST'
  }).then(() => {
    closeConfirmReportRestore();
    fetchReports();
  });
}

function confirmStatusRestore(entry_id) {
  const entry = power_data[entry_id];
  currentEditingStatusId = entry.id;

  let nextStatus, message;

  if (entry.taipower_status === null) {
    nextStatus = 0;
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.facility}</strong> 為搶修狀態？<br><br>`;
  } else if (entry.taipower_status === 0) {
    nextStatus = 1;
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.facility}</strong> 為已復電？<br><br>`;
  } else {
    return;
  }

  document.getElementById('confirmStatusText').innerHTML = message;
  document.getElementById('confirmStatusRestoreModal').dataset.nextStatus = nextStatus;
  document.getElementById('confirmStatusRestoreModal').classList.remove('hidden');
}

function submitStatusRestore() {
  const modal = document.getElementById('confirmStatusRestoreModal');
  const nextStatus = parseInt(modal.dataset.nextStatus);

  fetch(`/api/taiwater_power_reports/${currentEditingStatusId}/toggle_taipower_status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taipower_status: nextStatus })
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

// window.onload = async () => {
//   loadFilterDistricts()
// }

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
  document.getElementById('filterMismatch').checked = false;
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
    'taipower_status', 'taipower_description', 'taipower_eta_hours', 'taipower_support', 'taipower_restored_at',
    'electricity_number', 'pole_number', 'facility',
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
