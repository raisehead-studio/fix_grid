let sortField = '';
let sortOrder = 'asc';
let reportStatusFilter = 'all';    // 'all' | 'restored' | 'unrestored'
let taipowerStatusFilter = 'all';  // 'all' | 'restored' | 'unrestored'
let isDeleteMode = false;          // 是否處於刪除模式
let selectedItems = new Set();     // 選中的項目
let currentDeleteId = null;        // 當前要刪除的項目 ID
let selectedDistricts = new Set(); // 選中的行政區
let selectedVillages = new Set();  // 選中的里

// 檢查是否超過24小時且未復水
function isOver24HoursAndUnrestored(createdAt, reportStatus) {
  const createdTime = new Date(createdAt.replace(" ", "T") + "Z");
  const now = new Date();
  const diffHours = (now - createdTime) / (1000 * 60 * 60);
  return diffHours > 24 && !reportStatus; // 超過24小時且未復水
}

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
  const entry = water_data[currentEditingReportId];
  currentDeleteId = currentEditingReportId; // 使用相同的 ID
  document.getElementById('confirmDeleteText').innerHTML = `
  ⚠️ 確定要刪除 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 這筆資料？<br><br>
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
  
  fetch('/api/water_reports/batch_delete', {
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

  fetch("/api/water_reports", {
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

let water_data = {};
let filteredReports = [];

async function fetchReports() {
  const res = await fetch('/api/water_reports');
  let data = await res.json();

  let hideReportEdit = data.every(e => e.report_status);
  let hideTaipowerEdit = data.every(e => e.taiwater_status);

  // 控制 <th> 顯示與否
  const canEditReport = userPermissions.includes("edit_report");
  document.getElementById('th-edit-report').style.display = (hideReportEdit || !canEditReport) ? 'none' : '';
  if (userPermissions.includes("view_status")) {
    document.getElementById('th-edit-taiwater').style.display = hideTaipowerEdit ? 'none' : '';
  }

  // 取得排序與篩選設定
  // 篩選處理
  if (selectedDistricts.size > 0) {
    data = data.filter(e => selectedDistricts.has(e.district_id.toString()));
  }
  if (selectedVillages.size > 0) {
    data = data.filter(e => selectedVillages.has(e.village_id.toString()));
  }

  if (canViewStatus) {
    const mismatchOnly = document.getElementById('filterMismatch').checked;
    if (mismatchOnly) {
      data = data.filter(e => {
        const r = e.report_status;
        const t = e.taiwater_status;

        const bothOne = r == 1 && t == 1;
        const bothNotOne = r != 1 && t != 1;

        return !(bothOne || bothNotOne);  // 不是一致 → 是不一致
      });
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
    data = data.filter(e => e.taiwater_status == target);
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
  if (canViewStatus) {
    const taiwaterBody = document.getElementById('taiwater-table-body');
    taiwaterBody.innerHTML = '';
  }

  data.forEach((entry, index) => {
    water_data[entry.id] = entry
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
      <td>${entry.district}</td>
      <td>${entry.village}</td>
      <td>${entry.location}</td>
      <td>${entry.water_station === '是' ? '是' : '否'}</td>
      <td>${entry.contact}</td>
      <td>${entry.phone}</td>
      <td class="whitespace-nowrap ${isOver24HoursAndUnrestored(entry.created_at, entry.report_status) ? 'text-red-600 font-semibold' : ''}" 
          title="${'通報時間: ' + new Date(entry.created_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" }) + (entry.report_restored_at ? '\n復水時間: ' + new Date(entry.report_restored_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" }) : '') + (entry.report_updated_time ? '\n更新時間: ' + new Date(entry.report_updated_time.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" }) : '')}">
        ${new Date(entry.created_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" })}
      </td>
      <td>
        <div class="whitespace-pre-line overflow-x-auto overflow-y-auto max-h-[6em] max-w-[10em]">${entry.remarks || '-'}</div>
      </td>
      <td>
        ${entry.report_status 
          ? '<span class="text-green-600 whitespace-nowrap">已復水</span>' 
          : (canEditReport 
              ? `<button onclick="confirmReportRestore(${entry.id})" class="text-red-600 underline whitespace-nowrap">未復水</button>` 
              : '<span class="text-red-600 whitespace-nowrap">未復水</span>')}
      </td>
      <td class="text-center">
        ${!entry.report_status && canEditReport && !isDeleteMode
          ? `<button onclick="openEditReport(${entry.id})" class="text-blue-600">✏️</button>` 
          : ''}
      </td>
    `;
    reportBody.appendChild(reportRow);

    // 右表格：台水狀態
    if (canViewStatus) {
      const canEditStatus = userPermissions.includes("edit_status");
      const taiwaterBody = document.getElementById('taiwater-table-body');
      const statusRow = document.createElement('tr');
      statusRow.className = "border-b";
      statusRow.innerHTML = `
        <td>
          ${
            entry.taiwater_status === 1
              ? '<span class="text-green-600 whitespace-nowrap">已復水</span>'
              : canEditStatus
                ? `<button onclick="confirmStatusRestore(${entry.id})" class="${
                    entry.taiwater_status === 0 ? 'text-yellow-600' : 'text-gray-600'
                  } underline whitespace-nowrap">${
                    entry.taiwater_status === 0 ? '搶修中' : '✏️'
                  }</button>`
                : `<span class="${
                    entry.taiwater_status === 0 ? 'text-yellow-600' : 'text-gray-600'
                  } whitespace-nowrap">${
                    entry.taiwater_status === 0 ? '搶修中' : '尚無狀態'
                  }</span>`
          }
        </td>
        <td>
          <div class="whitespace-pre-line overflow-x-auto overflow-y-auto max-h-[6em] max-w-[10em]">${entry.taiwater_description || '-'}</div>
        </td>
        <td>${
          entry.taiwater_eta_hours
            ? `<span class="${entry.taiwater_eta_hours > 24 ? 'text-red-600 font-bold' : ''}">
                ${entry.taiwater_eta_hours} 小時
              </span>`
            : '-'
        }</td>
        <td>${entry.taiwater_water_station_status === '是' ? '已新增' : '未新增'}</td>
        <td>${entry.taiwater_support || '-'}</td>
        <td class="whitespace-nowrap">${entry.taiwater_restored_at ? new Date(entry.taiwater_restored_at.replace(" ", "T") + "Z").toLocaleString("zh-TW", { timeZone: "Asia/Taipei" }) : '-'}</td>
        <td class="text-center">
          ${!entry.taiwater_status && canEditStatus 
            ? `<button onclick="openEditStatus(${entry.id})" class="text-blue-600">✏️</button>` 
            : ''}
        </td>
      `;
      taiwaterBody.appendChild(statusRow);
    }
  });

  setTimeout(() => {
    requestAnimationFrame(() => {
      // 同步表體高度
      syncRowHeightsDelayed("#report-table-body tr", "#taiwater-table-body tr");
      // 同步表頭高度
      syncTheadHeightsDelayed(".col-span-3 table thead", ".col-span-2 table thead");
    });
  }, 0);
}

// export excel
function exportToExcel() {
  if (filteredReports.length === 0) {
    alert("目前沒有資料可以匯出！");
    return;
  }

  const dataRows = filteredReports.map(e => {
    const eta = e.taiwater_eta_hours;
    const isOver24h = eta != null && eta > 24;

    return [
      e.id,
      e.district,
      e.village,
      e.location,
      e.water_station === '是' ? '是' : '否',
      e.contact,
      e.phone,
      e.created_at,
      e.report_updated_time,
      e.report_status ? '是' : '否',
      canViewStatus ? (e.taiwater_status ? '已復水' : '搶修中') : '',
      canViewStatus ? (e.taiwater_description || '') : '',
      canViewStatus ? (e.taiwater_water_station_status === '是' ? '已新增' : '未新增') : '',
      canViewStatus ? (eta != null ? `${eta} 小時` : '') : '',
      canViewStatus ? (eta != null ? (isOver24h ? '是' : '否') : '') : ''
    ];
  });

  // 使用 +8 時區
  const now = new Date();
  const taipei = new Date(now.getTime() + (8 * 60 * 60 * 1000));
  const timestamp = taipei.toISOString().replace(/[:T]/g, '-').split('.')[0];
  const filename = `(表二)停水彙整表_${timestamp}.xlsx`;

  fetch("/api/export-excel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      template: "sheet2.xlsx",
      filename,
      data: dataRows,
      start_row: 6,   // 從第 6 列開始
      start_col: 1    // 從 A 欄開始
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
  entry = water_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('edit-location').value = entry.location || '';
  document.getElementById('edit-water-station').value = entry.water_station || '否';
  document.getElementById('edit-contact').value = entry.contact || '';
  document.getElementById('edit-phone').value = entry.phone || '';
  document.getElementById('edit-remarks').value = entry.remarks || '';
  document.getElementById('editReportModal').classList.remove('hidden');
}

function submitEditReport() {
  const payload = {
    location: document.getElementById('edit-location').value,
    water_station: document.getElementById('edit-water-station').value,
    contact_name: document.getElementById('edit-contact').value,
    contact_phone: document.getElementById('edit-phone').value,
    remarks: document.getElementById('edit-remarks').value,
  };
  fetch(`/api/water_reports/${currentEditingReportId}/update_report`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  }).then(() => {
    closeModal('editReportModal');
    fetchReports();
  });
}

function openEditStatus(entry_id) {
  entry = water_data[entry_id]
  currentEditingStatusId = entry.id;
  document.getElementById('edit-description').value = entry.taiwater_description || '';
  document.getElementById('edit-estimate-hour').value = entry.taiwater_eta_hours || '';
  document.getElementById('edit-water-station-status').value = entry.taiwater_water_station_status || '否';
  document.getElementById('edit-support').value = entry.taiwater_support || '';
  document.getElementById('editStatusModal').classList.remove('hidden');
}

function submitEditStatus() {
  const payload = {
    taiwater_note: document.getElementById('edit-description').value,
    taiwater_water_station_status: document.getElementById('edit-water-station-status').value,
    taiwater_eta_hours: parseInt(document.getElementById('edit-estimate-hour').value),
    taiwater_support: document.getElementById('edit-support').value
  };
  fetch(`/api/water_reports/${currentEditingStatusId}/update_taiwater`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  }).then(() => {
    closeEditStatusModal();
    fetchReports();
  });
}

function confirmReportRestore(entry_id) {
  entry = water_data[entry_id]
  currentEditingReportId = entry.id;
  document.getElementById('confirmReportText').innerHTML = `
  ⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 供水狀態？<br><br>
  此操作將立即生效，確認後將無法修改或復原。<br>
  請再次確認設定是否正確。`;
  document.getElementById('confirmReportRestoreModal').classList.remove('hidden');
}

function submitReportRestore() {
  fetch(`/api/water_reports/${currentEditingReportId}/toggle_report_status`, {
    method: 'POST'
  }).then(() => {
    closeConfirmReportRestore();
    fetchReports();
  });
}

function confirmStatusRestore(entry_id) {
  const entry = water_data[entry_id];
  currentEditingStatusId = entry.id;

  let nextStatus, message;

  if (entry.taiwater_status === null) {
    nextStatus = 0;
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 為<span class='text-red-600 font-bold text-lg'>搶修中</span>狀態？<br><br>`;
  } else if (entry.taiwater_status === 0) {
    nextStatus = 1;
    message = `⚠️ 確定要切換 <strong>#${entry.id} ${entry.district} ${entry.village} ${entry.location}</strong> 為<span class='text-red-600 font-bold text-lg'>已復水</span>？<br><br>`;
  } else {
    return; // 1 = 已復水，不可再次變更
  }

  document.getElementById('confirmStatusText').innerHTML = message;
  document.getElementById('confirmStatusRestoreModal').dataset.nextStatus = nextStatus;
  document.getElementById('confirmStatusRestoreModal').classList.remove('hidden');
}

function submitStatusRestore() {
  const modal = document.getElementById('confirmStatusRestoreModal');
  const nextStatus = parseInt(modal.dataset.nextStatus);

  fetch(`/api/water_reports/${currentEditingStatusId}/toggle_taiwater_status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taiwater_status: nextStatus })
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



window.onload = async () => {
  loadFilterDistricts()
  
  // 全域點擊事件：點擊其他地方關閉下拉選單
  document.addEventListener('click', () => {
    document.querySelectorAll('[id$="Dropdown"]').forEach(dropdown => {
      dropdown.classList.add('hidden');
    });
  });
}

async function loadFilterDistricts() {
  const districts = await fetch('/api/districts').then(res => res.json());
  const districtCheckboxes = document.getElementById('districtCheckboxes');
  districtCheckboxes.innerHTML = '';
  
  // 添加全選選項
  const selectAllDiv = document.createElement('div');
  selectAllDiv.className = 'flex items-center gap-2 p-2 hover:bg-blue-50 rounded cursor-pointer transition-colors border-b border-gray-200';
  selectAllDiv.innerHTML = `
    <input type="checkbox" id="district_select_all" 
           onchange="toggleAllDistricts()" 
           class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
    <label for="district_select_all" class="text-sm font-medium text-blue-600 cursor-pointer select-none">全選</label>
  `;
  districtCheckboxes.appendChild(selectAllDiv);
  
  districts.forEach(d => {
    const checkboxDiv = document.createElement('div');
    checkboxDiv.className = 'flex items-center gap-2 p-2 hover:bg-blue-50 rounded cursor-pointer transition-colors';
    checkboxDiv.innerHTML = `
      <input type="checkbox" id="district_${d.id}" value="${d.id}" 
             onchange="toggleDistrictFilter(${d.id})" 
             class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
      <label for="district_${d.id}" class="text-sm whitespace-nowrap cursor-pointer select-none">${d.name}</label>
    `;
    districtCheckboxes.appendChild(checkboxDiv);
  });
  
  // 設置下拉選單事件
  setupDropdownEvents('district');
  setupDropdownEvents('village');
}

async function loadFilterVillages() {
  // 根據選中的行政區載入對應的里
  if (selectedDistricts.size === 0) {
    // 如果沒有選中任何行政區，清空里選項
    renderVillageCheckboxes([]);
  } else {
    // 載入選中行政區的里
    const villagePromises = Array.from(selectedDistricts).map(districtId => 
      fetch(`/api/villages/${districtId}`).then(res => res.json())
    );
    const villageArrays = await Promise.all(villagePromises);
    const allVillages = villageArrays.flat();
    renderVillageCheckboxes(allVillages);
  }
}

function renderVillageCheckboxes(villages) {
  const villageCheckboxes = document.getElementById('villageCheckboxes');
  villageCheckboxes.innerHTML = '';
  
  villages.forEach(v => {
    const checkboxDiv = document.createElement('div');
    checkboxDiv.className = 'flex items-center gap-2 p-2 hover:bg-blue-50 rounded cursor-pointer transition-colors';
    checkboxDiv.innerHTML = `
      <input type="checkbox" id="village_${v.id}" value="${v.id}" 
             onchange="toggleVillageFilter(${v.id})" 
             class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500">
      <label for="village_${v.id}" class="text-sm whitespace-nowrap cursor-pointer select-none">${v.name}</label>
    `;
    villageCheckboxes.appendChild(checkboxDiv);
  });
}

// 切換行政區篩選
function toggleDistrictFilter(districtId) {
  const checkbox = document.getElementById(`district_${districtId}`);
  if (checkbox.checked) {
    selectedDistricts.add(districtId.toString());
  } else {
    selectedDistricts.delete(districtId.toString());
  }
  updateDropdownText('district');
  // 重新載入里選項
  loadFilterVillages();
  fetchReports();
}

// 切換里篩選
function toggleVillageFilter(villageId) {
  const checkbox = document.getElementById(`village_${villageId}`);
  if (checkbox.checked) {
    selectedVillages.add(villageId.toString());
  } else {
    selectedVillages.delete(villageId.toString());
  }
  updateDropdownText('village');
  fetchReports();
}

// 設置下拉選單事件
function setupDropdownEvents(type) {
  const btn = document.getElementById(`${type}DropdownBtn`);
  const dropdown = document.getElementById(`${type}Dropdown`);
  
  // 點擊按鈕切換下拉選單
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
  });
  
  // 防止下拉選單內部點擊關閉
  dropdown.addEventListener('click', (e) => {
    e.stopPropagation();
  });
}

// 更新下拉選單顯示文字
function updateDropdownText(type) {
  const textElement = document.getElementById(`${type}DropdownText`);
  const selectedSet = type === 'district' ? selectedDistricts : selectedVillages;
  
  if (selectedSet.size === 0) {
    textElement.textContent = `選擇${type === 'district' ? '行政區' : '里'}`;
  } else if (selectedSet.size === 1) {
    // 顯示單個選中的項目名稱
    const id = Array.from(selectedSet)[0];
    const checkbox = document.getElementById(`${type}_${id}`);
    if (checkbox) {
      const label = checkbox.nextElementSibling.textContent;
      textElement.textContent = label;
    }
  } else {
    // 顯示多個選中的項目數量
    textElement.textContent = `已選擇 ${selectedSet.size} 個${type === 'district' ? '行政區' : '里'}`;
  }
}

// 全選/取消全選行政區
function toggleAllDistricts() {
  const selectAllCheckbox = document.getElementById('district_select_all');
  const districtCheckboxes = document.querySelectorAll('#districtCheckboxes input[type="checkbox"]:not(#district_select_all)');
  
  districtCheckboxes.forEach(checkbox => {
    checkbox.checked = selectAllCheckbox.checked;
    if (selectAllCheckbox.checked) {
      selectedDistricts.add(checkbox.value);
    } else {
      selectedDistricts.delete(checkbox.value);
    }
  });
  
  updateDropdownText('district');
  loadFilterVillages();
  fetchReports();
}

function toggleSortOrder() {
  sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  document.getElementById('sortOrderBtn').innerText = sortOrder === 'asc' ? '升序 ⬆️' : '降序 ⬇️';
}

function clearFilters() {
  sortField = '';
  sortOrder = 'asc';
  reportStatusFilter = 'all';
  taipowerStatusFilter = 'all';
  selectedDistricts.clear();
  selectedVillages.clear();
  document.getElementById('filterBtnReportStatus').textContent = '❓';
  
  // 清除所有行政區勾選框（包括全選）
  document.querySelectorAll('#districtCheckboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
  // 清除所有里勾選框
  document.querySelectorAll('#villageCheckboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
  
  // 更新下拉選單顯示文字
  updateDropdownText('district');
  updateDropdownText('village');
  
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
    'id', 'district', 'village', 'location', 'water_station', 'remarks', 'contact', 'phone', 'created_at', 'report_status',
    'taiwater_status', 'taiwater_description', 'taiwater_eta_hours', 'taiwater_support', 'taiwater_restored_at', 'taiwater_water_station_status'
  ];
  fields.forEach(f => {
    const el = document.getElementById(`sort-indicator-${f}`);
    if (el) {
      el.innerText = (f === sortField) ? (sortOrder === 'asc' ? '⬆️' : '⬇️') : '';
    }
  });
}
