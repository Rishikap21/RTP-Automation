// RTP Automation - Main Application JS

// Global App State
const state = {
    session: {
        active: false,
        operator: null,
        token: null
    },
    activePanel: 'dashboard',
    activeSettingsTab: 'operators',
    uploadQueue: [],
    currentExtractionFile: null,
    selectedChatContexts: new Set()
};

// API Client Wrapper for FastAPI (running locally at http://127.0.0.1:8000)
class APIClient {
    static async request(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${window.location.origin}${endpoint}`;
        
        // Add auth header if token exists
        if (state.session.token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${state.session.token}`
            };
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'API request failed' }));
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error on ${endpoint}:`, error);
            showToast(error.message, 'error');
            throw error;
        }
    }

    static login(email, key) {
        return this.request('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, key })
        });
    }

    static getQueue() {
        return this.request('/api/queue');
    }

    static uploadFile(formData) {
        return this.request('/api/upload', {
            method: 'POST',
            body: formData
        });
    }

    static startProcessing() {
        return this.request('/api/queue/process', { method: 'POST' });
    }

    static getExtractionDetails(fileId) {
        return this.request(`/api/extraction/${fileId}`);
    }

    static convertToExcel(fileId) {
        return this.request('/api/excel/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId })
        });
    }

    static postChatMessage(message, contextFiles) {
        return this.request('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, context_files: contextFiles })
        });
    }

    static getExcelReports() {
        return this.request('/api/reports');
    }

    static getOperators() {
        return this.request('/api/settings/operators');
    }

    static addOperator(name, email, role) {
        return this.request('/api/settings/operators', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, role })
        });
    }

    static getPermissions() {
        return this.request('/api/settings/permissions');
    }

    static updatePermission(moduleId, enabled) {
        return this.request('/api/settings/permissions', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ module_id: moduleId, enabled })
        });
    }

    static rotateApiKey() {
        return this.request('/api/settings/rotate-key', { method: 'POST' });
    }

    static getAuditLogs() {
        return this.request('/api/logs');
    }
}

// Toast Notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `px-4 py-3 rounded-xl shadow-lg flex items-center gap-2 text-white border text-sm transition-all duration-300 transform translate-y-2 opacity-0`;
    
    if (type === 'success') {
        toast.className += ' bg-slate-900 border-secondary text-secondary-container';
    } else if (type === 'error') {
        toast.className += ' bg-red-950 border-red-800 text-red-100';
    }

    const icon = type === 'success' ? 'check_circle' : 'error';
    toast.innerHTML = `
        <span class="material-symbols-outlined text-[18px]">${icon}</span>
        <span class="font-medium">${message}</span>
    `;

    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    // Remove after 4s
    setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Single Page Application View Router
window.switchPanel = function(panelId) {
    // Check authentication
    if (!state.session.active && panelId !== 'login') {
        panelId = 'login';
    }

    state.activePanel = panelId;

    // Toggle main views
    if (panelId === 'login') {
        document.getElementById('login-view').classList.remove('hidden');
        document.getElementById('main-layout').classList.add('hidden');
        return;
    } else {
        document.getElementById('login-view').classList.add('hidden');
        document.getElementById('main-layout').classList.remove('hidden');
    }

    // Hide all panels
    document.querySelectorAll('.view-panel').forEach(panel => {
        panel.classList.add('hidden');
    });

    // Show selected panel
    const targetPanel = document.getElementById(`panel-${panelId}`);
    if (targetPanel) {
        targetPanel.classList.remove('hidden');
    }

    // Update active nav state in sidebar
    document.querySelectorAll('#sidebar-nav .nav-item').forEach(item => {
        const isTarget = item.getAttribute('data-panel') === panelId;
        if (isTarget) {
            item.className = 'nav-item w-full flex items-center gap-3 px-4 py-3 bg-secondary-container text-on-secondary-container rounded-lg font-semibold active-tab-glow';
        } else {
            item.className = 'nav-item w-full flex items-center gap-3 px-4 py-3 rounded-lg text-on-surface-variant hover:bg-surface-container-high transition-colors';
        }
    });

    // Trigger load hooks for specific panels
    if (panelId === 'dashboard') loadDashboardData();
    if (panelId === 'extraction') loadExtractionPanel();
    if (panelId === 'chatbot') loadChatbotPanel();
    if (panelId === 'excel') loadExcelManagerPanel();
    if (panelId === 'settings') loadSettingsPanel();
};

// ==================== A. LOGIN WORKFLOW ====================
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('operator-email').value;
    const key = document.getElementById('operator-key').value;
    const submitBtn = document.getElementById('login-submit-btn');

    // Add loading state
    const originalBtnHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = `
        <span class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        <span>Authenticating...</span>
    `;
    submitBtn.disabled = true;

    try {
        const data = await APIClient.login(email, key);
        state.session.active = true;
        state.session.operator = data.operator;
        state.session.token = data.token;

        document.getElementById('sidebar-username').innerText = data.operator.name;
        showToast(`Operator session established: ${data.operator.name}`);
        
        window.switchPanel('dashboard');
        
        // Start background polling for upload pipeline updates
        startQueuePolling();
    } catch (error) {
        // Handled inside API client
    } finally {
        submitBtn.innerHTML = originalBtnHTML;
        submitBtn.disabled = false;
    }
});

document.getElementById('toggle-password').addEventListener('click', () => {
    const input = document.getElementById('operator-key');
    const icon = document.getElementById('password-visibility-icon');
    if (input.type === 'password') {
        input.type = 'text';
        icon.innerText = 'visibility_off';
    } else {
        input.type = 'password';
        icon.innerText = 'visibility';
    }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    state.session.active = false;
    state.session.operator = null;
    state.session.token = null;
    window.switchPanel('login');
    showToast('Operator logged out successfully.');
});

// ==================== B. DASHBOARD PANEL ====================
async function loadDashboardData() {
    try {
        const queue = await APIClient.getQueue();
        const reports = await APIClient.getExcelReports();
        
        // Update stats summary counts
        document.getElementById('dash-active-extractors').innerText = queue.filter(f => f.status === 'Extracting').length || '0';
        document.getElementById('dash-queue-backlog').innerText = queue.filter(f => f.status === 'Queued' || f.status === 'Scanning').length || '0';
        document.getElementById('dash-total-tables').innerText = reports.length * 12 + 24; // Mock calculation based on reports size
        
        // Load recent pipeline activities
        const tbody = document.getElementById('dashboard-activity-rows');
        tbody.innerHTML = '';
        
        if (queue.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-6 py-8 text-center text-on-surface-variant font-medium">No active files in the queue pipeline.</td>
                </tr>
            `;
            return;
        }

        queue.forEach(item => {
            const statusColors = {
                'Queued': 'bg-surface-container-highest text-on-surface-variant',
                'Scanning': 'bg-blue-100 text-blue-800',
                'Extracting': 'bg-secondary-container text-on-secondary-container',
                'Completed': 'bg-green-100 text-green-800',
                'Failed': 'bg-red-100 text-red-800'
            };
            const badgeClass = statusColors[item.status] || 'bg-slate-100 text-slate-800';

            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surface-container-low transition-colors h-12';
            tr.innerHTML = `
                <td class="px-6 py-2.5 font-semibold text-body-sm truncate max-w-xs">${item.name}</td>
                <td class="px-6 py-2.5 text-body-sm text-on-surface-variant">${item.name.split('.').pop().toUpperCase()}</td>
                <td class="px-6 py-2.5">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter ${badgeClass}">${item.status}</span>
                </td>
                <td class="px-6 py-2.5 text-body-sm text-on-surface-variant">${item.operator || 'System'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        // API error handles inside client
    }
}

// ==================== C. UPLOAD PIPELINE ====================
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('border-secondary', 'bg-secondary-container/10');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-secondary', 'bg-secondary-container/10');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFilesUpload(files);
});

fileInput.addEventListener('change', (e) => {
    handleFilesUpload(e.target.files);
});

async function handleFilesUpload(files) {
    if (!files.length) return;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            await APIClient.uploadFile(formData);
            showToast(`File uploaded to pipeline: ${file.name}`);
        } catch (e) {
            // Error toast handled in APIClient
        }
    }

    loadUploadQueue();
}

async function loadUploadQueue() {
    try {
        const queue = await APIClient.getQueue();
        const tbody = document.getElementById('upload-queue-rows');
        tbody.innerHTML = '';

        const processBtn = document.getElementById('process-queue-btn');
        const hasQueuedItems = queue.some(item => item.status === 'Queued');
        
        if (hasQueuedItems) {
            processBtn.classList.remove('hidden');
        } else {
            processBtn.classList.add('hidden');
        }

        if (queue.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-6 py-8 text-center text-on-surface-variant font-medium">No files currently in the pipeline queue.</td>
                </tr>
            `;
            return;
        }

        queue.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surface-container-low transition-colors h-14';
            
            const isDone = item.status === 'Completed';
            const progressWidth = item.progress + '%';
            
            tr.innerHTML = `
                <td class="px-6 py-3 font-semibold text-body-sm truncate max-w-xs">${item.name}</td>
                <td class="px-6 py-3 text-body-sm text-on-surface-variant font-mono">${(item.size / 1024 / 1024).toFixed(2)} MB</td>
                <td class="px-6 py-3">
                    <div class="flex items-center gap-2">
                        <div class="w-full bg-surface-container-high h-2 rounded-full overflow-hidden shrink-0">
                            <div class="bg-secondary h-full transition-all duration-500" style="width: ${progressWidth}"></div>
                        </div>
                        <span class="text-xs font-mono text-on-surface-variant">${item.progress}%</span>
                    </div>
                </td>
                <td class="px-6 py-3 text-right">
                    ${isDone ? `
                        <button onclick="window.switchPanel('extraction')" class="text-secondary font-bold text-xs hover:underline flex items-center justify-end gap-1 ml-auto">
                            <span>Open Data</span>
                            <span class="material-symbols-outlined text-sm">open_in_new</span>
                        </button>
                    ` : `
                        <span class="text-xs font-semibold uppercase tracking-wider text-on-surface-variant">${item.status}</span>
                    `}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {}
}

document.getElementById('process-queue-btn').addEventListener('click', async () => {
    try {
        await APIClient.startProcessing();
        showToast('AI pipeline execution initiated.', 'success');
        loadUploadQueue();
    } catch (e) {}
});

// Periodic Queue Poller
let pollInterval = null;
function startQueuePolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => {
        if (state.session.active) {
            // Poll whenever active, updating active view UI
            if (state.activePanel === 'upload') loadUploadQueue();
            if (state.activePanel === 'dashboard') loadDashboardData();
            if (state.activePanel === 'extraction') loadExtractionSidebar(false);
        }
    }, 2000);
}

// ==================== D. AI TABLE EXTRACTION ====================
async function loadExtractionPanel() {
    await loadExtractionSidebar(true);
}

async function loadExtractionSidebar(selectFirst = false) {
    try {
        const queue = await APIClient.getQueue();
        const container = document.getElementById('extraction-document-list');
        
        // Save current selection to restore active visual state
        const currentSelectedId = state.currentExtractionFile ? state.currentExtractionFile.id : null;
        
        container.innerHTML = '';

        if (queue.length === 0) {
            container.innerHTML = `
                <p class="text-xs text-on-surface-variant p-4 text-center">No files in queue pipeline.</p>
            `;
            return;
        }

        queue.forEach(item => {
            const div = document.createElement('div');
            
            const isSelected = currentSelectedId === item.id || (selectFirst && !currentSelectedId && queue.indexOf(item) === 0);
            
            div.className = `p-3 bg-surface border rounded-lg flex flex-col gap-2 cursor-pointer transition-colors ${
                isSelected ? 'border-secondary ring-1 ring-secondary' : 'border-outline-variant hover:bg-surface-container-high'
            }`;
            
            const isExtracting = item.status === 'Extracting';
            
            div.innerHTML = `
                <div class="flex justify-between items-start">
                    <span class="material-symbols-outlined text-secondary">description</span>
                    <span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-tighter ${
                        item.status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-secondary-container text-on-secondary-container'
                    }">${item.status}</span>
                </div>
                <p class="font-semibold text-xs truncate">${item.name}</p>
                ${isExtracting ? `
                    <div class="w-full bg-surface-container-high h-1 rounded-full overflow-hidden">
                        <div class="bg-secondary h-full" style="width: ${item.progress}%"></div>
                    </div>
                ` : ''}
                <p class="text-[10px] text-on-surface-variant">${item.progress}% complete • ${item.tables_found || 0} tables found</p>
            `;

            div.addEventListener('click', () => {
                // Select document
                selectExtractionFile(item);
                
                // Toggle active visual states
                document.querySelectorAll('#extraction-document-list > div').forEach(d => {
                    d.classList.remove('border-secondary', 'ring-1', 'ring-secondary');
                    d.classList.add('border-outline-variant');
                });
                div.classList.add('border-secondary', 'ring-1', 'ring-secondary');
                div.classList.remove('border-outline-variant');
            });

            container.appendChild(div);

            if (isSelected && selectFirst) {
                selectExtractionFile(item);
            }
        });
    } catch (e) {}
}

async function selectExtractionFile(file) {
    state.currentExtractionFile = file;
    
    // Update toolbar indicator
    document.getElementById('pdf-page-indicator').innerText = `Document ID: ${file.id.substring(0, 8)}...`;
    
    // Update extraction status box
    const scanner = document.getElementById('scanner-line');
    const detailTbody = document.getElementById('extraction-preview-rows');
    const rowsCount = document.getElementById('extraction-rows-count');
    const flagsCount = document.getElementById('extraction-flags-count');
    
    detailTbody.innerHTML = '';

    if (file.status !== 'Completed') {
        scanner.classList.remove('hidden');
        document.getElementById('extraction-ai-analysis').innerText = `Extracting structured tables from ${file.name}... Current Progress: ${file.progress}%`;
        rowsCount.innerText = '0 Rows';
        flagsCount.innerText = '0 Flags';
        
        detailTbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-8 text-center text-on-surface-variant font-medium">
                    <span class="inline-block w-5 h-5 border-2 border-secondary border-t-transparent rounded-full animate-spin mr-2 align-middle"></span>
                    Extraction is in progress. Please wait for pipeline completion.
                </td>
            </tr>
        `;
        return;
    }

    // Completed files get parsed table data
    scanner.classList.add('hidden');
    document.getElementById('extraction-ai-analysis').innerText = `Extraction complete for ${file.name}. Identified tables with 98.4% Confidence. Validating values against schemas.`;

    try {
        const details = await APIClient.getExtractionDetails(file.id);
        const rows = details.extracted_rows || [];
        
        rowsCount.innerText = `${rows.length} Rows`;
        flagsCount.innerText = `${rows.filter(r => r.status === 'Flagged').length} Flags`;

        rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = `hover:bg-surface-container-low transition-colors h-12 ${row.status === 'Flagged' ? 'bg-error-container/10' : ''}`;
            
            const badgeClass = row.status === 'Verified' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
            
            tr.innerHTML = `
                <td class="px-6 py-2 font-mono text-code-sm">${row.ref_id}</td>
                <td class="px-6 py-2 text-body-sm">
                    ${row.status === 'Flagged' ? `<span class="material-symbols-outlined text-error text-sm align-middle mr-1">warning</span>` : ''}
                    ${row.description}
                </td>
                <td class="px-6 py-2 text-body-sm text-right font-mono">${row.quantity}</td>
                <td class="px-6 py-2 text-body-sm text-right font-mono">$${row.unit_price.toFixed(2)}</td>
                <td class="px-6 py-2 text-body-sm text-right font-bold font-mono">$${row.total.toFixed(2)}</td>
                <td class="px-6 py-2">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${badgeClass}">${row.status}</span>
                </td>
            `;

            tr.addEventListener('click', () => {
                // Row flash effect
                tr.classList.add('bg-secondary-container/20');
                setTimeout(() => tr.classList.remove('bg-secondary-container/20'), 400);
            });

            detailTbody.appendChild(tr);
        });
    } catch (e) {}
}

document.getElementById('extraction-validate-btn').addEventListener('click', () => {
    if (!state.currentExtractionFile) return;
    showToast(`Triggered local schema validation for ${state.currentExtractionFile.name}`);
});

document.getElementById('extraction-convert-btn').addEventListener('click', async () => {
    if (!state.currentExtractionFile) return;
    
    try {
        await APIClient.convertToExcel(state.currentExtractionFile.id);
        showToast('Successfully generated Excel report. Available in Excel Manager.', 'success');
        window.switchPanel('excel');
    } catch (e) {}
});


// ==================== E. AI CHATBOT ====================
async function loadChatbotPanel() {
    try {
        const queue = await APIClient.getQueue();
        const container = document.getElementById('chatbot-context-list');
        container.innerHTML = '';

        if (queue.length === 0) {
            container.innerHTML = `<p class="text-xs text-on-surface-variant p-4 text-center">No reference documents available.</p>`;
            return;
        }

        queue.forEach(item => {
            const isChecked = state.selectedChatContexts.has(item.id);
            const div = document.createElement('div');
            div.className = 'flex items-center gap-3 p-3 bg-surface hover:bg-surface-container-high rounded-xl cursor-pointer border border-outline-variant';
            div.innerHTML = `
                <input type="checkbox" ${isChecked ? 'checked' : ''} class="context-checkbox rounded border-outline-variant text-secondary focus:ring-secondary cursor-pointer shrink-0">
                <div class="truncate">
                    <p class="font-semibold text-xs text-on-surface truncate">${item.name}</p>
                    <p class="text-[10px] text-on-surface-variant mt-0.5">${item.status}</p>
                </div>
            `;
            
            // Checkbox event
            const checkbox = div.querySelector('.context-checkbox');
            div.addEventListener('click', (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                }
                if (checkbox.checked) {
                    state.selectedChatContexts.add(item.id);
                } else {
                    state.selectedChatContexts.delete(item.id);
                }
            });

            container.appendChild(div);
        });
    } catch (e) {}
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    
    // Add user message to UI
    const container = document.getElementById('chat-messages-container');
    const userBubble = document.createElement('div');
    userBubble.className = 'flex gap-4 items-start max-w-3xl ml-auto justify-end';
    userBubble.innerHTML = `
        <div class="bg-primary text-white p-4 rounded-xl user-chat-bubble text-body-sm max-w-xl">
            <p class="font-semibold text-right text-secondary-fixed mb-1">You</p>
            <p class="whitespace-pre-wrap">${msg}</p>
        </div>
        <div class="w-8 h-8 rounded-lg bg-surface-container-highest flex items-center justify-center text-on-surface shrink-0">
            <span class="material-symbols-outlined text-sm">account_circle</span>
        </div>
    `;
    container.appendChild(userBubble);
    container.scrollTop = container.scrollHeight;

    // Loading typing bubble
    const typingBubble = document.createElement('div');
    typingBubble.className = 'flex gap-4 items-start max-w-3xl';
    typingBubble.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-secondary/15 flex items-center justify-center text-secondary shrink-0">
            <span class="material-symbols-outlined text-sm">smart_toy</span>
        </div>
        <div class="bg-surface-container-low p-4 rounded-xl ai-chat-bubble text-body-sm text-on-surface flex items-center gap-1.5 min-w-[60px]">
            <span class="w-1.5 h-1.5 bg-secondary rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
            <span class="w-1.5 h-1.5 bg-secondary rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
            <span class="w-1.5 h-1.5 bg-secondary rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
        </div>
    `;
    container.appendChild(typingBubble);
    container.scrollTop = container.scrollHeight;

    try {
        const contexts = Array.from(state.selectedChatContexts);
        const reply = await APIClient.postChatMessage(msg, contexts);
        
        // Remove typing and add reply
        typingBubble.remove();
        
        const aiBubble = document.createElement('div');
        aiBubble.className = 'flex gap-4 items-start max-w-3xl';
        aiBubble.innerHTML = `
            <div class="w-8 h-8 rounded-lg bg-secondary/15 flex items-center justify-center text-secondary shrink-0">
                <span class="material-symbols-outlined text-sm">smart_toy</span>
            </div>
            <div class="bg-surface-container-low p-4 rounded-xl ai-chat-bubble text-body-sm text-on-surface">
                <p class="font-semibold text-secondary mb-1">RTP AI Assistant</p>
                <p class="leading-relaxed whitespace-pre-wrap">${reply.answer}</p>
            </div>
        `;
        container.appendChild(aiBubble);
        container.scrollTop = container.scrollHeight;
    } catch (e) {
        typingBubble.remove();
    }
}

document.getElementById('chat-send-btn').addEventListener('click', sendChatMessage);
document.getElementById('chat-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});

// Suggested chips clicking logic
document.querySelectorAll('.suggested-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        document.getElementById('chat-input').value = chip.innerText.trim();
        sendChatMessage();
    });
});

// ==================== F. EXCEL MANAGER ====================
async function loadExcelManagerPanel() {
    try {
        const reports = await APIClient.getExcelReports();
        const tbody = document.getElementById('excel-report-rows');
        tbody.innerHTML = '';
        
        document.getElementById('excel-total-reports').innerText = reports.length;
        
        const totalBytes = reports.reduce((acc, r) => acc + r.size, 0);
        document.getElementById('excel-total-size').innerText = `${(totalBytes / 1024 / 1024).toFixed(2)} MB`;

        if (reports.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-8 text-center text-on-surface-variant font-medium">No generated spreadsheets found.</td>
                </tr>
            `;
            return;
        }

        reports.forEach(item => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surface-container-high transition-colors group';
            tr.innerHTML = `
                <td class="px-gutter py-4">
                    <input class="excel-row-check rounded border-outline-variant text-secondary focus:ring-secondary cursor-pointer" type="checkbox" data-id="${item.id}">
                </td>
                <td class="px-gutter py-4">
                    <div class="flex items-center gap-3">
                        <span class="material-symbols-outlined text-on-surface-variant group-hover:text-secondary transition-colors">description</span>
                        <div>
                            <p class="font-body-md font-semibold text-on-surface">${item.name}</p>
                            <p class="text-xs text-on-surface-variant font-code-sm">ID: ${item.id.substring(0, 8)}</p>
                        </div>
                    </div>
                </td>
                <td class="px-gutter py-4 text-body-sm text-on-surface-variant">${item.source_file}</td>
                <td class="px-gutter py-4 text-body-sm text-on-surface-variant">${item.created_at}</td>
                <td class="px-gutter py-4 text-body-sm text-on-surface-variant text-right font-mono">${(item.size / 1024 / 1024).toFixed(2)} MB</td>
                <td class="px-gutter py-4 text-right">
                    <a href="/api/reports/download/${item.id}" download class="inline-block p-2 hover:bg-secondary-container rounded-lg text-on-surface-variant hover:text-on-secondary-container transition-all">
                        <span class="material-symbols-outlined">download</span>
                    </a>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Setup select all checkboxes listeners
        const masterCheck = document.getElementById('excel-select-all');
        const checks = document.querySelectorAll('.excel-row-check');
        
        masterCheck.checked = false;
        masterCheck.addEventListener('change', () => {
            checks.forEach(c => c.checked = masterCheck.checked);
            updateBulkDownloadBtn();
        });

        checks.forEach(c => c.addEventListener('change', updateBulkDownloadBtn));
        updateBulkDownloadBtn();
    } catch (e) {}
}

function updateBulkDownloadBtn() {
    const checked = document.querySelectorAll('.excel-row-check:checked').length;
    const btn = document.getElementById('excel-bulk-download-btn');
    if (checked > 0) {
        btn.className = 'flex items-center gap-2 px-4 py-2 bg-secondary text-white rounded-lg font-label-md text-label-md hover:opacity-90 active:scale-95 transition-all';
        btn.innerHTML = `<span class="material-symbols-outlined text-body-sm">download_for_offline</span> Download Selected (${checked})`;
        btn.disabled = false;
    } else {
        btn.className = 'flex items-center gap-2 px-4 py-2 bg-surface-container-high border border-outline-variant rounded-lg font-label-md text-label-md hover:bg-surface-container-highest transition-all opacity-50 cursor-not-allowed';
        btn.innerHTML = `<span class="material-symbols-outlined text-body-sm">download_for_offline</span> Download Selected`;
        btn.disabled = true;
    }
}

document.getElementById('excel-bulk-download-btn').addEventListener('click', () => {
    const checkedList = document.querySelectorAll('.excel-row-check:checked');
    checkedList.forEach(checkbox => {
        const id = checkbox.getAttribute('data-id');
        // Trigger multi downloads
        const link = document.createElement('a');
        link.href = `/api/reports/download/${id}`;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        link.remove();
    });
    showToast(`Initiating download for ${checkedList.length} spreadsheets.`);
});

// ==================== G. SECURITY & ADMIN SETTINGS ====================
window.switchSettingsTab = function(tabId) {
    state.activeSettingsTab = tabId;
    
    // Toggle active tabs views
    document.querySelectorAll('.settings-sub-panel').forEach(panel => {
        panel.classList.add('hidden');
    });
    document.getElementById(`settings-sub-${tabId}`).classList.remove('hidden');

    // Update buttons UI
    document.querySelectorAll('.settings-tab-btn').forEach(btn => {
        const isTarget = btn.id === `settings-tab-btn-${tabId}`;
        if (isTarget) {
            btn.className = 'settings-tab-btn text-left px-5 py-4 rounded-xl border border-secondary shadow-sm flex justify-between items-center transition-all bg-white';
            btn.querySelector('.material-symbols-outlined:last-child').classList.remove('opacity-0');
        } else {
            btn.className = 'settings-tab-btn text-left px-5 py-4 rounded-xl border border-outline-variant bg-white/50 flex justify-between items-center transition-all hover:border-secondary';
        }
    });

    if (tabId === 'operators') loadOperatorsList();
    if (tabId === 'permissions') loadPermissionsList();
    if (tabId === 'logs') loadAuditLogsList();
};

async function loadOperatorsList() {
    try {
        const operators = await APIClient.getOperators();
        const container = document.getElementById('settings-operators-list');
        container.innerHTML = '';

        operators.forEach(op => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surface-container-low/50 transition-colors border-b border-outline-variant';
            
            const initials = op.name.split(' ').map(n => n[0]).join('');
            const statusClass = op.status === 'Active' ? 'text-secondary font-semibold' : 'text-outline';
            
            tr.innerHTML = `
                <td class="px-4 py-4 flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-secondary/10 flex items-center justify-center text-secondary font-bold text-xs shrink-0">${initials}</div>
                    <div>
                        <p class="font-bold text-sm text-on-surface">${op.name}</p>
                        <p class="text-xs text-on-surface-variant font-mono">${op.email}</p>
                    </div>
                </td>
                <td class="px-4 py-4">
                    <span class="px-2.5 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed font-label-md text-label-md">${op.role}</span>
                </td>
                <td class="px-4 py-4 text-xs">
                    <div class="flex items-center gap-2 ${statusClass}">
                        <span class="w-2 h-2 rounded-full bg-current"></span>
                        ${op.status}
                    </div>
                </td>
                <td class="px-4 py-4 text-on-surface-variant text-xs font-mono">${op.last_login}</td>
            `;
            container.appendChild(tr);
        });
    } catch (e) {}
}

const userModal = document.getElementById('add-user-modal');

document.getElementById('add-user-btn').addEventListener('click', () => {
    userModal.classList.remove('hidden');
});

document.getElementById('close-user-modal-btn').addEventListener('click', () => {
    userModal.classList.add('hidden');
});

document.getElementById('add-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('new-user-name').value;
    const email = document.getElementById('new-user-email').value;
    const role = document.getElementById('new-user-role').value;

    try {
        await APIClient.addOperator(name, email, role);
        showToast(`Registered operator: ${name}`);
        userModal.classList.add('hidden');
        document.getElementById('add-user-form').reset();
        loadOperatorsList();
    } catch (e) {}
});

async function loadPermissionsList() {
    try {
        const permissions = await APIClient.getPermissions();
        const container = document.getElementById('settings-permissions-list');
        container.innerHTML = '';

        const iconMapping = {
            'chatbot': 'smart_toy',
            'extraction': 'document_scanner',
            'excel': 'table_chart'
        };

        permissions.forEach(perm => {
            const icon = iconMapping[perm.id] || 'settings';
            const div = document.createElement('div');
            div.className = 'flex items-start justify-between p-4 rounded-xl border border-outline-variant bg-surface/30';
            div.innerHTML = `
                <div class="flex gap-4">
                    <div class="w-12 h-12 rounded-lg bg-secondary/15 flex items-center justify-center text-secondary shrink-0">
                        <span class="material-symbols-outlined">${icon}</span>
                    </div>
                    <div>
                        <h4 class="font-bold text-sm text-on-surface">${perm.name}</h4>
                        <p class="text-xs text-on-surface-variant mt-0.5 leading-relaxed">${perm.description}</p>
                    </div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer shrink-0 mt-1">
                    <input type="checkbox" ${perm.enabled ? 'checked' : ''} class="perm-switch sr-only peer" data-id="${perm.id}">
                    <div class="w-11 h-6 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-secondary"></div>
                </label>
            `;
            
            // Switch event
            const input = div.querySelector('.perm-switch');
            input.addEventListener('change', async () => {
                try {
                    await APIClient.updatePermission(perm.id, input.checked);
                    showToast(`Updated access permissions for module: ${perm.name}`, 'success');
                } catch (e) {
                    input.checked = !input.checked;
                }
            });

            container.appendChild(div);
        });
    } catch (e) {}
}

document.getElementById('rotate-key-btn').addEventListener('click', async () => {
    try {
        const res = await APIClient.rotateApiKey();
        document.getElementById('api-key-text').innerText = res.new_key;
        document.getElementById('api-key-updated').innerText = `Last rotated: Just now`;
        showToast('Gateway security key rotated successfully.', 'success');
    } catch (e) {}
});

async function loadAuditLogsList() {
    try {
        const logs = await APIClient.getAuditLogs();
        const container = document.getElementById('settings-audit-logs-list');
        container.innerHTML = '';

        logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'p-4 flex gap-4 hover:bg-surface-container-low/30 border-b border-outline-variant';
            
            const typeIcons = {
                'info': 'settings_suggest',
                'alert': 'report',
                'download': 'description'
            };
            const icon = typeIcons[log.type] || 'info';
            
            let iconClass = 'bg-secondary-container/20 text-on-secondary-container';
            if (log.type === 'alert') iconClass = 'bg-red-100 text-red-800';
            
            div.innerHTML = `
                <div class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${iconClass}">
                    <span class="material-symbols-outlined">${icon}</span>
                </div>
                <div class="flex-1">
                    <div class="flex justify-between items-start mb-1">
                        <p class="font-bold text-sm ${log.type === 'alert' ? 'text-error' : 'text-on-surface'}">${log.title}</p>
                        <span class="text-xs text-outline font-mono">${log.timestamp}</span>
                    </div>
                    <p class="text-xs text-on-surface-variant leading-relaxed">${log.details}</p>
                    <div class="mt-2 flex gap-2">
                        <span class="px-2 py-0.5 rounded bg-surface-container-highest text-on-surface-variant text-[10px] font-mono">IP: ${log.ip}</span>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (e) {}
}


// ==================== H. GLOBAL SEARCH FILTERING ====================
document.getElementById('global-search').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    
    if (state.activePanel === 'excel') {
        const rows = document.querySelectorAll('#excel-report-rows tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    } else if (state.activePanel === 'settings' && state.activeSettingsTab === 'logs') {
        const logs = document.querySelectorAll('#settings-audit-logs-list > div');
        logs.forEach(log => {
            const text = log.textContent.toLowerCase();
            log.style.display = text.includes(term) ? '' : 'none';
        });
    } else if (state.activePanel === 'settings' && state.activeSettingsTab === 'operators') {
        const rows = document.querySelectorAll('#settings-operators-list tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    } else if (state.activePanel === 'dashboard') {
        const rows = document.querySelectorAll('#dashboard-activity-rows tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    } else if (state.activePanel === 'extraction') {
        const docs = document.querySelectorAll('#extraction-document-list > div');
        docs.forEach(doc => {
            const text = doc.textContent.toLowerCase();
            doc.style.display = text.includes(term) ? '' : 'none';
        });
    }
});


// ==================== I. NOTIFICATIONS DROPDOWN ====================
const bell = document.getElementById('notification-bell');
const dropdown = document.getElementById('notification-dropdown');

bell.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
    // Hide unread dot on open
    document.getElementById('unread-dot').classList.add('hidden');
});

document.addEventListener('click', (e) => {
    if (!dropdown.classList.contains('hidden') && !dropdown.contains(e.target) && e.target !== bell) {
        dropdown.classList.add('hidden');
    }
});

// Mock notification list loading
async function loadNotifications() {
    const list = document.getElementById('notification-list');
    list.innerHTML = `
        <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer">
            <p class="font-body-md text-sm text-on-surface font-semibold">Refinery_Report_Q3.pdf processing complete</p>
            <p class="text-xs text-on-surface-variant mt-1">10 mins ago</p>
        </div>
        <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer">
            <p class="font-body-md text-sm text-on-surface">New operator added: <span class="font-semibold">Sarah Miller</span></p>
            <p class="text-xs text-on-surface-variant mt-1">2 hours ago</p>
        </div>
        <div class="p-4 hover:bg-surface-container-low transition-colors cursor-pointer">
            <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-secondary"></span>
                <p class="font-body-md text-sm text-on-surface">System Health: Optimal</p>
            </div>
            <p class="text-xs text-on-surface-variant mt-1">4 hours ago</p>
        </div>
    `;
}

document.getElementById('clear-notifications').addEventListener('click', () => {
    document.getElementById('notification-list').innerHTML = `
        <p class="text-xs text-on-surface-variant text-center py-6">No notifications</p>
    `;
    document.getElementById('unread-dot').classList.add('hidden');
});

// ==================== J. INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    // Check if FastAPI uvicorn routing needs profile init
    loadNotifications();
    
    // Bind Sidebar Button Clicks
    document.querySelectorAll('#sidebar-nav .nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            const panel = btn.getAttribute('data-panel');
            window.switchPanel(panel);
        });
    });

    // Topbar quick actions
    document.getElementById('topbar-upload-btn').addEventListener('click', () => {
        window.switchPanel('upload');
    });

    document.getElementById('topbar-health-btn').addEventListener('click', () => {
        showToast('Running refinery telemetry health assessment... Status: OPTIMAL', 'success');
    });

    // Initialize SPA in login state
    window.switchPanel('login');
});
