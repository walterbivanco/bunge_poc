// Configuración
const API_URL = window.location.origin;

// Referencias a elementos del DOM
const messagesContainer = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const sendIcon = document.getElementById('send-icon');
const loadingIcon = document.getElementById('loading-icon');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const clearChatBtn = document.getElementById('clear-chat-btn');

// Estado
let isLoading = false;
let messageCount = 0;

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    questionInput.focus();
    loadChatHistory();
});

// Limpiar chat
clearChatBtn.addEventListener('click', () => {
    if (confirm('¿Estás seguro de que quieres limpiar toda la conversación?')) {
        clearChat();
    }
});

// Verificar health del backend
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDot.classList.add('online');
            statusText.textContent = 'Conectado';
        } else {
            statusDot.classList.remove('online');
            statusText.textContent = 'Servicio degradado';
        }
    } catch (error) {
        statusDot.classList.add('offline');
        statusText.textContent = 'Sin conexión';
        console.error('Error checking health:', error);
    }
}

// Manejar envío del formulario
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (isLoading) return;
    
    const question = questionInput.value.trim();
    if (!question) return;
    
    // Agregar mensaje del usuario
    addMessage(question, 'user');
    saveChatHistory();
    
    // Limpiar input
    questionInput.value = '';
    
    // Deshabilitar input mientras procesa
    setLoading(true);
    
    // Agregar spinner de carga
    const loadingId = addLoadingMessage();
    
    try {
        // Llamar al backend
        const response = await fetch(`${API_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Remover spinner
        removeLoadingMessage(loadingId);
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error en el servidor');
        }
        
        // Agregar respuesta del bot con resultados
        addBotResponse(data);
        saveChatHistory();
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        addMessage(`❌ Error: ${error.message}`, 'error');
        saveChatHistory();
    } finally {
        setLoading(false);
        questionInput.focus();
    }
});

// Agregar mensaje simple
function addMessage(text, type = 'bot') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<p>${escapeHtml(text)}</p>`;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Agregar respuesta del bot con tabla
function addBotResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // SQL generado
    contentDiv.innerHTML = `
        <p><strong>📝 SQL Generado:</strong></p>
        <div class="sql-block">${escapeHtml(data.sql)}</div>
    `;
    
    // Resultados
    if (data.total_rows > 0) {
        const tableHtml = generateTable(data.columns, data.rows);
        contentDiv.innerHTML += `
            <p style="margin-top: 16px;"><strong>📊 Resultados:</strong></p>
            ${tableHtml}
            <p class="table-info">Mostrando ${data.total_rows} fila(s)</p>
        `;
    } else {
        contentDiv.innerHTML += `<p style="margin-top: 16px;">No se encontraron resultados.</p>`;
    }
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Generar tabla HTML
function generateTable(columns, rows) {
    let html = '<div class="table-container"><table class="results-table">';
    
    // Headers
    html += '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</tr></thead>';
    
    // Rows
    html += '<tbody>';
    rows.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
            const cellValue = cell === null ? '<em>null</em>' : escapeHtml(String(cell));
            html += `<td>${cellValue}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    
    html += '</table></div>';
    return html;
}

// Setear estado de loading
function setLoading(loading) {
    isLoading = loading;
    sendBtn.disabled = loading;
    questionInput.disabled = loading;
    
    if (loading) {
        sendIcon.style.display = 'none';
        loadingIcon.style.display = 'inline';
    } else {
        sendIcon.style.display = 'inline';
        loadingIcon.style.display = 'none';
    }
}

// Scroll al final
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Escapar HTML para prevenir XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Agregar mensaje de carga con spinner
function addLoadingMessage() {
    const loadingId = `loading-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot loading-message';
    messageDiv.id = loadingId;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <div class="spinner"></div>
        <span class="loading-text">Procesando tu pregunta...</span>
    `;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return loadingId;
}

// Remover mensaje de carga
function removeLoadingMessage(loadingId) {
    const loadingMsg = document.getElementById(loadingId);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Limpiar todo el chat
function clearChat() {
    // Remover todos los mensajes excepto el de bienvenida
    const messages = messagesContainer.querySelectorAll('.message:not(:first-child)');
    messages.forEach(msg => msg.remove());
    
    // Limpiar localStorage
    localStorage.removeItem('chatHistory');
    messageCount = 0;
    
    console.log('Chat limpiado');
}

// Guardar historial en localStorage
function saveChatHistory() {
    const messages = [];
    messagesContainer.querySelectorAll('.message:not(:first-child)').forEach(msg => {
        const type = msg.classList.contains('user') ? 'user' : 
                     msg.classList.contains('error') ? 'error' : 'bot';
        const content = msg.querySelector('.message-content').innerHTML;
        messages.push({ type, content });
    });
    
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

// Cargar historial desde localStorage
function loadChatHistory() {
    try {
        const history = localStorage.getItem('chatHistory');
        if (history) {
            const messages = JSON.parse(history);
            messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.type}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = msg.content;
                
                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);
            });
            
            messageCount = messages.length;
            scrollToBottom();
        }
    } catch (error) {
        console.error('Error cargando historial:', error);
        localStorage.removeItem('chatHistory');
    }
}

