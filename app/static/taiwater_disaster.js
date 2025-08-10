let selectedId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadHistoryList();
});

function loadHistoryList() {
  fetch("/api/taiwater_disasters")
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("history-select");
      select.innerHTML = `<option value="">請選擇歷史資料</option>`;
      data.forEach(item => {
        const opt = document.createElement("option");
        opt.value = item.id;
        opt.textContent = item.name;
        select.appendChild(opt);
      });

      select.addEventListener("change", () => {
        selectedId = select.value;
        const deleteBtn = document.getElementById("delete-btn");
        
        if (selectedId) {
          loadExcelData(selectedId);
          deleteBtn.classList.remove("hidden");
        } else {
          document.querySelector("#excel-table tbody").innerHTML = "";
          deleteBtn.classList.add("hidden");
        }
      });
    });
}

function loadExcelData(disasterId) {
  fetch(`/api/taiwater_disasters/${disasterId}/download`)
    .then(res => res.blob())
    .then(blob => {
      const reader = new FileReader();
      reader.onload = function (evt) {
        const data = new Uint8Array(evt.target.result);
        const workbook = XLSX.read(data, { type: "array" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const json = XLSX.utils.sheet_to_json(sheet, { header: 1, range: 4 });
        renderExcelData(json);
      };
      reader.readAsArrayBuffer(blob);
    });
}

// 新增 modal 操作
function openNewModal() {
  document.getElementById("new-modal").classList.remove("hidden");
}

function closeNewModal() {
  document.getElementById("new-modal").classList.add("hidden");
}

function submitNew(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  fetch("/api/taiwater_disasters", {
    method: "POST",
    body: formData,
  })
    .then(() => {
      closeNewModal();

      // 重新載入歷史清單
      fetch("/api/taiwater_disasters")
        .then(res => res.json())
        .then(data => {
          const select = document.getElementById("history-select");
          select.innerHTML = `<option value="">請選擇...</option>`;
          data.forEach(item => {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.name;
            select.appendChild(opt);
          });

          if (data.length > 0) {
            selectedId = data[0].id;
            select.value = selectedId;
            setTimeout(() => openUploadModal(), 300);
          }
        });
    });
}

// 可擴充：上傳 Excel 的 modal 操作
let overwriteConfirmed = false;

function openUploadModal() {
  if (!selectedId) {
    alert("請先選擇歷史資料");
    return;
  }

  fetch(`/api/taiwater_disasters/${selectedId}/download`)
    .then(res => {
      if (res.status === 404) {
        // 沒有檔案，直接開啟上傳 modal
        overwriteConfirmed = false;
        document.getElementById("upload-modal").classList.remove("hidden");
        return null;
      }
      return res.blob();
    })
    .then(blob => {
      if (!blob) return;

      const reader = new FileReader();
      reader.onload = function (evt) {
        try {
          const data = new Uint8Array(evt.target.result);
          const workbook = XLSX.read(data, { type: "array" });
          const sheet = workbook.Sheets[workbook.SheetNames[0]];
          const json = XLSX.utils.sheet_to_json(sheet, { header: 1, range: 4 });

          if (json.length > 0 && !overwriteConfirmed) {
            document.getElementById("confirm-overwrite-modal").classList.remove("hidden");
          } else {
            overwriteConfirmed = false;
            document.getElementById("upload-modal").classList.remove("hidden");
          }
        } catch (error) {
          // 若解析失敗，當成沒有資料
          document.getElementById("upload-modal").classList.remove("hidden");
        }
      };
      reader.readAsArrayBuffer(blob);
    });
}

function closeUploadModal() {
  document.getElementById("upload-modal").classList.add("hidden");
  const fileInput = document.querySelector("#upload-form input[name='file']");
  if (fileInput) fileInput.value = "";
}

function cancelOverwrite() {
  document.getElementById("confirm-overwrite-modal").classList.add("hidden");
}

function confirmOverwrite() {
  overwriteConfirmed = true;
  document.getElementById("confirm-overwrite-modal").classList.add("hidden");
  document.getElementById("upload-modal").classList.remove("hidden");
}

function submitExcelUpload(e) {
  e.preventDefault();
  const fileInput = document.querySelector("#upload-form input[name='file']");
  const file = fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (evt) {
    const data = new Uint8Array(evt.target.result);
    const workbook = XLSX.read(data, { type: "array" });
    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    const json = XLSX.utils.sheet_to_json(sheet, { header: 1, range: 4 });

    // 顯示在畫面上
    renderExcelData(json);

    // 寄送檔案到後端保存
    const formData = new FormData();
    formData.append("file", file);
    const name = document.querySelector("#history-select option:checked").textContent;
    formData.append("name", name);

    fetch(`/api/taiwater_disasters/${selectedId}/upload`, {
      method: "POST",
      body: formData,
    }).then(() => {
      closeUploadModal();
    });
  };
  reader.readAsArrayBuffer(file);
}

// 可擴充：下載檔案 modal 操作與 download 範例 example.xlsx 功能
function downloadSelectedExcel() {
  if (!selectedId) {
    alert("請先選擇歷史資料");
    return;
  }
  window.location.href = `/api/taiwater_disasters/${selectedId}/download`;
}

function downloadExampleExcel() {
  window.location.href = "/api/taiwater_disasters/example";
}

function renderExcelData(jsonData) {
  const tbody = document.querySelector("#excel-table tbody");
  tbody.innerHTML = "";

  jsonData.forEach((row, i) => {
    const tr = document.createElement("tr");
    tr.className = "border-t border-b";
    let rowHtml = '';

    row.forEach((cell, colIndex) => {
      let cellValue = cell;

      // 第 10 欄（index 9）處理日期格式
      if (colIndex === 10 && typeof cell === "number" && cell > 40000 && cell < 60000) {
        const excelEpoch = new Date(Date.UTC(1899, 11, 30));
        const jsDate = new Date(excelEpoch.getTime() + cell * 86400000);
        const formatter = new Intl.DateTimeFormat("zh-TW", {
          year: "numeric",
          month: "numeric",
          day: "numeric",
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          hour12: false,
          timeZone: "UTC",
        });

        cellValue = formatter.format(jsDate);
      }

      rowHtml += `<td>${cellValue || ""}</td>`;
    });

    tr.innerHTML = rowHtml;
    tbody.appendChild(tr);
  });
}

// 刪除相關函數
function openDeleteModal() {
  if (!selectedId) {
    alert("請先選擇歷史資料");
    return;
  }
  
  const select = document.getElementById("history-select");
  const selectedOption = select.options[select.selectedIndex];
  const itemName = selectedOption.textContent;
  
  document.getElementById("delete-item-name").textContent = itemName;
  document.getElementById("delete-modal").classList.remove("hidden");
}

function closeDeleteModal() {
  document.getElementById("delete-modal").classList.add("hidden");
}

function confirmDelete() {
  if (!selectedId) return;
  
  fetch(`/api/taiwater_disasters/${selectedId}`, {
    method: "DELETE",
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        closeDeleteModal();
        
        // 重新載入歷史清單
        loadHistoryList();
        
        // 清空表格
        document.querySelector("#excel-table tbody").innerHTML = "";
        
        // 隱藏刪除按鈕
        document.getElementById("delete-btn").classList.add("hidden");
        
        // 重置選擇
        selectedId = null;
        document.getElementById("history-select").value = "";
        
        alert("刪除成功");
      } else {
        alert("刪除失敗：" + (data.message || "未知錯誤"));
      }
    })
    .catch(error => {
      console.error("刪除錯誤:", error);
      alert("刪除失敗：" + error.message);
    });
}

