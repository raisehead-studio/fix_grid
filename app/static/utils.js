/**
 * 同步左右表格的行高度
 * @param {string} leftSelector - 左表格行的選擇器
 * @param {string} rightSelector - 右表格行的選擇器
 * @param {boolean} forceSync - 是否強制同步（即使高度相同也重新設置）
 */
function syncRowHeights(leftSelector, rightSelector, forceSync = false) {
  const leftRows = document.querySelectorAll(leftSelector);
  const rightRows = document.querySelectorAll(rightSelector);

  const rowCount = Math.min(leftRows.length, rightRows.length);

  for (let i = 0; i < rowCount; i++) {
    const leftRow = leftRows[i];
    const rightRow = rightRows[i];
    
    // 獲取實際內容高度
    const leftHeight = leftRow.scrollHeight;
    const rightHeight = rightRow.scrollHeight;
    const maxHeight = Math.max(leftHeight, rightHeight);

    // 檢查是否需要更新高度
    const currentLeftHeight = parseInt(leftRow.style.height) || 0;
    const currentRightHeight = parseInt(rightRow.style.height) || 0;
    
    if (forceSync || currentLeftHeight !== maxHeight || currentRightHeight !== maxHeight) {
      leftRow.style.height = `${maxHeight}px`;
      rightRow.style.height = `${maxHeight}px`;
    }
  }
}

/**
 * 延遲同步行高度，確保 DOM 完全渲染後再執行
 * @param {string} leftSelector - 左表格行的選擇器
 * @param {string} rightSelector - 右表格行的選擇器
 * @param {number} delay - 延遲時間（毫秒）
 */
function syncRowHeightsDelayed(leftSelector, rightSelector, delay = 100) {
  setTimeout(() => {
    requestAnimationFrame(() => {
      syncRowHeights(leftSelector, rightSelector, true);
    });
  }, delay);
}

/**
 * 監聽表格變化並自動同步高度
 * @param {string} leftSelector - 左表格行的選擇器
 * @param {string} rightSelector - 右表格行的選擇器
 * @param {string} tableSelector - 表格容器選擇器
 */
function autoSyncRowHeights(leftSelector, rightSelector, tableSelector = null) {
  // 初始同步
  syncRowHeightsDelayed(leftSelector, rightSelector);
  
  // 監聽視窗大小變化
  window.addEventListener('resize', () => {
    syncRowHeightsDelayed(leftSelector, rightSelector);
  });
  
  // 如果提供了表格選擇器，監聽表格內容變化
  if (tableSelector) {
    const observer = new MutationObserver(() => {
      syncRowHeightsDelayed(leftSelector, rightSelector);
    });
    
    const table = document.querySelector(tableSelector);
    if (table) {
      observer.observe(table, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
      });
    }
  }
}

/**
 * 重置表格行高度
 * @param {string} leftSelector - 左表格行的選擇器
 * @param {string} rightSelector - 右表格行的選擇器
 */
function resetRowHeights(leftSelector, rightSelector) {
  const leftRows = document.querySelectorAll(leftSelector);
  const rightRows = document.querySelectorAll(rightSelector);
  
  leftRows.forEach(row => {
    row.style.height = '';
  });
  
  rightRows.forEach(row => {
    row.style.height = '';
  });
}

/**
 * 同步左右表格的表頭高度
 * @param {string} leftTheadSelector - 左表格表頭的選擇器
 * @param {string} rightTheadSelector - 右表格表頭的選擇器
 * @param {boolean} forceSync - 是否強制同步（即使高度相同也重新設置）
 */
function syncTheadHeights(leftTheadSelector, rightTheadSelector, forceSync = false) {
  const leftThead = document.querySelector(leftTheadSelector);
  const rightThead = document.querySelector(rightTheadSelector);
  
  if (!leftThead || !rightThead) {
    console.warn('無法找到表頭元素:', { leftTheadSelector, rightTheadSelector });
    return;
  }
  
  // 獲取表頭行
  const leftTheadRows = leftThead.querySelectorAll('tr');
  const rightTheadRows = rightThead.querySelectorAll('tr');
  
  const rowCount = Math.min(leftTheadRows.length, rightTheadRows.length);
  
  for (let i = 0; i < rowCount; i++) {
    const leftRow = leftTheadRows[i];
    const rightRow = rightTheadRows[i];
    
    // 獲取實際內容高度
    const leftHeight = leftRow.scrollHeight;
    const rightHeight = rightRow.scrollHeight;
    const maxHeight = Math.max(leftHeight, rightHeight);
    
    // 檢查是否需要更新高度
    const currentLeftHeight = parseInt(leftRow.style.height) || 0;
    const currentRightHeight = parseInt(rightRow.style.height) || 0;
    
    if (forceSync || currentLeftHeight !== maxHeight || currentRightHeight !== maxHeight) {
      leftRow.style.height = `${maxHeight}px`;
      rightRow.style.height = `${maxHeight}px`;
    }
  }
}

/**
 * 延遲同步表頭高度，確保 DOM 完全渲染後再執行
 * @param {string} leftTheadSelector - 左表格表頭的選擇器
 * @param {string} rightTheadSelector - 右表格表頭的選擇器
 * @param {number} delay - 延遲時間（毫秒）
 */
function syncTheadHeightsDelayed(leftTheadSelector, rightTheadSelector, delay = 100) {
  setTimeout(() => {
    requestAnimationFrame(() => {
      syncTheadHeights(leftTheadSelector, rightTheadSelector, true);
    });
  }, delay);
}

/**
 * 同步表格的完整高度（包括表頭和表體）
 * @param {string} leftTableSelector - 左表格的選擇器
 * @param {string} rightTableSelector - 右表格的選擇器
 * @param {boolean} includeThead - 是否同步表頭高度
 * @param {boolean} forceSync - 是否強制同步
 */
function syncTableHeights(leftTableSelector, rightTableSelector, includeThead = true, forceSync = false) {
  const leftTable = document.querySelector(leftTableSelector);
  const rightTable = document.querySelector(rightTableSelector);
  
  if (!leftTable || !rightTable) {
    console.warn('無法找到表格元素:', { leftTableSelector, rightTableSelector });
    return;
  }
  
  // 同步表體高度
  const leftTbody = leftTable.querySelector('tbody');
  const rightTbody = rightTable.querySelector('tbody');
  
  if (leftTbody && rightTbody) {
    const leftRows = leftTbody.querySelectorAll('tr');
    const rightRows = rightTbody.querySelectorAll('tr');
    
    const rowCount = Math.min(leftRows.length, rightRows.length);
    
    for (let i = 0; i < rowCount; i++) {
      const leftRow = leftRows[i];
      const rightRow = rightRows[i];
      
      const leftHeight = leftRow.scrollHeight;
      const rightHeight = rightRow.scrollHeight;
      const maxHeight = Math.max(leftHeight, rightHeight);
      
      const currentLeftHeight = parseInt(leftRow.style.height) || 0;
      const currentRightHeight = parseInt(rightRow.style.height) || 0;
      
      if (forceSync || currentLeftHeight !== maxHeight || currentRightHeight !== maxHeight) {
        leftRow.style.height = `${maxHeight}px`;
        rightRow.style.height = `${maxHeight}px`;
      }
    }
  }
  
  // 同步表頭高度
  if (includeThead) {
    const leftThead = leftTable.querySelector('thead');
    const rightThead = rightTable.querySelector('thead');
    
    if (leftThead && rightThead) {
      const leftTheadRows = leftThead.querySelectorAll('tr');
      const rightTheadRows = rightThead.querySelectorAll('tr');
      
      const theadRowCount = Math.min(leftTheadRows.length, rightTheadRows.length);
      
      for (let i = 0; i < theadRowCount; i++) {
        const leftRow = leftTheadRows[i];
        const rightRow = rightTheadRows[i];
        
        const leftHeight = leftRow.scrollHeight;
        const rightHeight = rightRow.scrollHeight;
        const maxHeight = Math.max(leftHeight, rightHeight);
        
        const currentLeftHeight = parseInt(leftRow.style.height) || 0;
        const currentRightHeight = parseInt(rightRow.style.height) || 0;
        
        if (forceSync || currentLeftHeight !== maxHeight || currentRightHeight !== maxHeight) {
          leftRow.style.height = `${maxHeight}px`;
          rightRow.style.height = `${maxHeight}px`;
        }
      }
    }
  }
}

/**
 * 延遲同步完整表格高度
 * @param {string} leftTableSelector - 左表格的選擇器
 * @param {string} rightTableSelector - 右表格的選擇器
 * @param {boolean} includeThead - 是否同步表頭高度
 * @param {number} delay - 延遲時間（毫秒）
 */
function syncTableHeightsDelayed(leftTableSelector, rightTableSelector, includeThead = true, delay = 100) {
  setTimeout(() => {
    requestAnimationFrame(() => {
      syncTableHeights(leftTableSelector, rightTableSelector, includeThead, true);
    });
  }, delay);
}

/**
 * 自動同步表格高度（包括表頭和表體）
 * @param {string} leftTableSelector - 左表格的選擇器
 * @param {string} rightTableSelector - 右表格的選擇器
 * @param {boolean} includeThead - 是否同步表頭高度
 * @param {string} containerSelector - 容器選擇器（可選）
 */
function autoSyncTableHeights(leftTableSelector, rightTableSelector, includeThead = true, containerSelector = null) {
  // 初始同步
  syncTableHeightsDelayed(leftTableSelector, rightTableSelector, includeThead);
  
  // 監聽視窗大小變化
  window.addEventListener('resize', () => {
    syncTableHeightsDelayed(leftTableSelector, rightTableSelector, includeThead);
  });
  
  // 如果提供了容器選擇器，監聽內容變化
  if (containerSelector) {
    const observer = new MutationObserver(() => {
      syncTableHeightsDelayed(leftTableSelector, rightTableSelector, includeThead);
    });
    
    const container = document.querySelector(containerSelector);
    if (container) {
      observer.observe(container, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
      });
    }
  }
} 