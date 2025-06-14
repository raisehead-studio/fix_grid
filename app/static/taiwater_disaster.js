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
        if (selectedId) {
          loadExcelData(selectedId);
        } else {
          document.querySelector("#excel-table tbody").innerHTML = "";
        }
      });
    });
}

function loadExcelData(disasterId) {
  fetch(`/api/taiwater_disasters/${disasterId}/data`)
    .then(res => res.json())
    .then(json => {
      const tbody = document.querySelector("#excel-table tbody");
      tbody.innerHTML = "";
      json.data.forEach((row, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${i + 1}</td>
          <td>${row["行政區"]}</td>
          <td>${row["里"]}</td>
          <td>${row["目前停水戶數"]}</td>
          <td>${row["已復水戶數"]}</td>
          <td>${row["累積停水戶數"]}</td>
          <td>${row["目前降壓戶數"]}</td>
          <td>${row["已降壓戶數"]}</td>
          <td>${row["累積降壓戶數"]}</td>
          <td>${row["目前停水影響戶數"]}</td>
          <td>${row["預計復水時間"]}</td>
        `;
        tbody.appendChild(tr);
      });
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

  // 檢查是否已有檔案
  fetch(`/api/taiwater_disasters/${selectedId}/data`)
    .then(res => res.json())
    .then(data => {
      if (data.data && data.data.length > 0 && !overwriteConfirmed) {
        document.getElementById("confirm-overwrite-modal").classList.remove("hidden");
      } else {
        overwriteConfirmed = false;
        document.getElementById("upload-modal").classList.remove("hidden");
      }
    });
}

function closeUploadModal() {
  document.getElementById("upload-modal").classList.add("hidden");
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
  const form = document.getElementById("upload-form");
  const formData = new FormData(form);

  // 取目前選取的 name
  const name = document.querySelector("#history-select option:checked").textContent;
  formData.append("name", name);

  fetch(`/api/taiwater_disasters/${selectedId}/upload`, {
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(() => {
      closeUploadModal();
      loadExcelData(selectedId);
    });
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
