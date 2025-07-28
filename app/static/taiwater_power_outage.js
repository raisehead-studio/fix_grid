let sortField = '';
let sortOrder = 'asc';
let filteredReports = [];
let isDeleteMode = false;          // 是否處於刪除模式
let selectedItems = new Set();     // 選中的項目
let currentDeleteId = null;        // 當前要刪除的項目 ID

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

// 切換刪除模式
function toggleDeleteMode() {
  isDeleteMode = !isDeleteMode;
  selectedItems.clear();
  
  const deleteBtn = document.querySelector('button[onclick="toggleDeleteMode()"]');
  const selectAllTh = document.getElementById('th-select-all');
  const batchDeleteBtn = document.getElementById('batchDeleteBtn');
  const selectAllCheckbox = document.getElementById('selectAllCheckbox');
  
  if (isDeleteMode) {
    deleteBtn.textContent = '取消刪除';
    deleteBtn.className = 'bg-gray-600 text-white px-4 py-2 rounded';
    selectAllTh.style.display = '';
    batchDeleteBtn.style.display = '';
  } else {
    deleteBtn.textContent = '刪除資料';
    deleteBtn.className = 'bg-red-600 text-white px-4 py-2 rounded';
    selectAllTh.style.display = 'none';
    batchDeleteBtn.style.display = 'none';
    // 重置全選勾選框狀態
    if (selectAllCheckbox) {
      selectAllCheckbox.checked = false;
    }
  }
  
  fetchReports();
}

// 全選/取消全選
function toggleSelectAll() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"][data-item-id]');
  const selectAllCheckbox = document.getElementById('selectAllCheckbox');
  
  checkboxes.forEach(checkbox => {
    checkbox.checked = selectAllCheckbox.checked;
    if (selectAllCheckbox.checked) {
      selectedItems.add(checkbox.dataset.itemId);
    } else {
      selectedItems.delete(checkbox.dataset.itemId);
    }
  });
  
  updateDeleteButton();
}

// 切換單個項目選中狀態
function toggleItemSelection(itemId) {
  if (selectedItems.has(itemId)) {
    selectedItems.delete(itemId);
  } else {
    selectedItems.add(itemId);
  }
  
  updateDeleteButton();
}

// 更新刪除按鈕狀態
function updateDeleteButton() {
  const batchDeleteBtn = document.getElementById('batchDeleteBtn');
  if (selectedItems.size > 0) {
    batchDeleteBtn.textContent = `批量刪除 (${selectedItems.size})`;
    batchDeleteBtn.disabled = false;
    batchDeleteBtn.className = 'bg-red-600 text-white px-4 py-2 rounded';
  } else {
    batchDeleteBtn.textContent = '批量刪除';
    batchDeleteBtn.disabled = true;
    batchDeleteBtn.className = 'bg-gray-400 text-white px-4 py-2 rounded cursor-not-allowed';
  }
}

// 確認刪除單個項目
function confirmDeleteReport() {
  const entry = power_data[currentEditingReportId];
  currentDeleteId = currentEditingReportId; // 使用相同的 ID
  document.getElementById('confirmDeleteText').innerHTML = `
  ⚠️ 確定要刪除 <strong>#${entry.id} ${entry.facility} ${entry.location}</strong> 這筆資料？<br><br>
  此操作將永久刪除該筆資料，確認後將無法復原。<br>
  請再次確認是否要刪除。`;
  document.getElementById('confirmDeleteModal').classList.remove('hidden');
}

// 確認批量刪除
function confirmBatchDelete() {
  if (selectedItems.size === 0) return;
  
  document.getElementById('confirmDeleteText').innerHTML = `
  ⚠️ 確定要刪除選取的 ${selectedItems.size} 筆資料？<br><br>
  此操作將永久刪除這些資料，確認後將無法復原。<br>
  請再次確認是否要刪除。`;
  document.getElementById('confirmDeleteModal').classList.remove('hidden');
}

// 執行刪除
function submitDelete() {
  const idsToDelete = currentDeleteId ? [currentDeleteId] : Array.from(selectedItems);
  const isSingleDelete = !!currentDeleteId;
  
  fetch('/api/taiwater_power_reports/batch_delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids: idsToDelete })
  }).then(res => {
    if (res.ok) {
      closeConfirmDeleteModal();
      
      if (isSingleDelete) {
        // 單筆刪除：先關閉編輯視窗，再重置狀態
        closeEditReportModal();
        currentDeleteId = null;
        // 延遲一下再重新載入資料，確保 modal 完全關閉
        setTimeout(() => {
          fetchReports();
        }, 100);
      } else {
        // 批量刪除：退出刪除模式
        toggleDeleteMode();
      }
    } else {
      alert('刪除失敗！');
    }
  });
}

// 關閉刪除確認 Modal
function closeConfirmDeleteModal() {
  closeModal('confirmDeleteModal');
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
    
    // 刪除模式的勾選框
    const checkboxCell = isDeleteMode && userPermissions.includes("excel") 
      ? `<td class="text-center">
          <input type="checkbox" data-item-id="${entry.id}" 
                 onchange="toggleItemSelection(${entry.id})" 
                 class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
         </td>`
      : '';
    
    reportRow.innerHTML = `
      ${checkboxCell}
      <td>${entry.id}</td>
      <td>${entry.facility}</td>
      <td>${entry.location}</td>
      <td>${entry.pole_number}</td>
      <td>${entry.electricity_number}</td>
      <td>${entry.reason}</td>
      <td>${entry.contact}</td>
      <td>${entry.phone}</td>
      <td class="whitespace-nowrap">${new Date(entry.created_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" })}</td>
      <td>
        ${entry.report_status 
          ? '<span class="text-green-600 whitespace-nowrap">已復電</span>' 
          : (canEditReport 
              ? `<button onclick="confirmReportRestore(${entry.id})" class="text-red-600 underline whitespace-nowrap">未復電</button>` 
              : '<span class="text-red-600 whitespace-nowrap">未復電</span>')}
      </td>
      <td class="text-center">
        ${!entry.report_status && canEditReport && !isDeleteMode
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
        <td class="whitespace-nowrap">${entry.taipower_restored_at ? new Date(entry.taipower_restored_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" }) : '-'}</td>
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

  const dataRows = filteredReports.map(e => {
    const eta = e.taipower_eta_hours;
    const isOver24h = eta != null && eta > 24;

    return [
      e.facility,
      e.location,
      e.pole_number,
      e.electricity_number,
      e.reason,
      e.contact,
      e.phone,
      e.created_at,
      e.report_status ? "是" : "否",
      canViewStatus ? (e.taipower_status ? "已復電" : "搶修中") : "",
      canViewStatus ? (e.taipower_description || "") : "",
      canViewStatus ? (eta != null ? `${eta} 小時` : "") : "",
      canViewStatus ? (eta != null ? (isOver24h ? "是" : "否") : "") : "",
      canViewStatus ? (e.taipower_support || "") : ""
    ];
  });

  const now = new Date();
  const timestamp = now.toISOString().replace(/[:T]/g, '-').split('.')[0];
  const filename = `(表三)水公司停電彙整表_${timestamp}.xlsx`;

  fetch("/api/export-excel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template: "sheet3.xlsx",
      filename,
      data: dataRows,
      start_row: 5,   // 從第 5 列開始
      start_col: 2    // 從 B 欄開始
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

// Modals

let currentEditingReportId = null;
let currentEditingStatusId = null;

function openEditReport(entry_id) {
  entry = power_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('edit-facility').value = entry.facility || '';
  document.getElementById('edit-location').value = entry.location || '';
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
    location: document.getElementById('edit-location').value,
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
  ⚠️ 確定要切換 <strong>#${entry.id} ${entry.location} 桿號 ${entry.pole_number} 電號 ${entry.electricity_number}</strong> 供電狀態？<br><br>
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
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.facility}</strong> 為<span class='text-red-600 font-bold text-lg'>搶修中</span>狀態？<br><br>`;
  } else if (entry.taipower_status === 0) {
    nextStatus = 1;
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.facility}</strong> 為<span class='text-red-600 font-bold text-lg'>已復電</span>？<br><br>`;
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
    'electricity_number', 'pole_number', 'facility', 'location',
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
