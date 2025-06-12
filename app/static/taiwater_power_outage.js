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

let power_data = {};

async function fetchReports() {
  const res = await fetch('/api/taiwater_power_reports');
  const canViewStatus = userPermissions.includes("view_status");
  let data = await res.json();

  // 取得排序與篩選設定
  const selectedSortField = document.getElementById('sortField').value;

  // 篩選處理
  if (canViewStatus) {
    const mismatchOnly = document.getElementById('filterMismatch').checked;
    if (mismatchOnly) {
      data = data.filter(e => e.report_status !== e.taipower_status);
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
      <td>${entry.created_at}</td>
      <td>
        ${entry.report_status 
          ? '<span class="text-green-600">已復電</span>' 
          : (canEditReport 
              ? `<button onclick="confirmReportRestore(${entry.id})" class="text-red-600 underline">未復電</button>` 
              : '<span class="text-red-600">未復電</span>')}
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
      if (index == 0) {
        taipowerBody.innerHTML = '';
      }
      const statusRow = document.createElement('tr');
      statusRow.className = "border-b";
      statusRow.innerHTML = `
        <td>
          ${entry.taipower_status 
            ? '<span class="text-green-600">已復電</span>' 
            : (canEditStatus 
                ? `<button onclick="confirmStatusRestore(${entry.id})" class="text-red-600 underline">未復電</button>` 
                : '<span class="text-red-600">未復電</span>')}
        </td>
        <td>${entry.taipower_description || '-'}</td>
        <td>${
          entry.taipower_eta_hours
            ? `<span class="${entry.taipower_eta_hours > 24 ? 'text-red-600 font-bold' : ''}">
                ${entry.taipower_eta_hours} 小時
              </span>`
            : '-'
        }</td>
        <td>${entry.taipower_support || '-'}</td>
        <td class="text-center">
          ${!entry.taipower_status && canEditStatus 
            ? `<button onclick="openEditStatus(${entry.id})" class="text-blue-600">✏️</button>` 
            : ''}
        </td>
      `;
      taipowerBody.appendChild(statusRow);
    }
  });
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
  entry = power_data[entry_id]
  currentEditingStatusId = entry.id;
  document.getElementById('confirmStatusText').innerHTML = `
  ⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 供電狀態？<br><br>
  此操作將立即生效，確認後將無法修改或復原。<br>
  請再次確認設定是否正確。`;
  document.getElementById('confirmStatusRestoreModal').classList.remove('hidden');
}

function submitStatusRestore() {
  fetch(`/api/taiwater_power_reports/${currentEditingStatusId}/toggle_taipower_status`, {
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

let sortField = '';
let sortOrder = 'asc';

function toggleSortOrder() {
  sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  document.getElementById('sortOrderBtn').innerText = sortOrder === 'asc' ? '升序 ⬆️' : '降序 ⬇️';
}

function clearFilters() {
  document.getElementById('sortField').value = '';
  document.getElementById('filterMismatch').checked = false;
  document.getElementById('sortOrderBtn').innerText = '升序 ⬆️';
  sortAscending = true;
  fetchReports();
}
