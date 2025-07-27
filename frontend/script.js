// Configuration
const CHAT_SERVICE_URL = 'http://localhost:8000';

// Global variables
let chatId = null;
let messageCount = 0;

// DOM elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const sessionIdElement = document.getElementById('sessionId');
const messageCountElement = document.getElementById('messageCount');
const lastSourceElement = document.getElementById('lastSource');
const helpButton = document.getElementById('helpButton');
const samplesModal = document.getElementById('samplesModal');
const closeSamplesButton = document.getElementById('closeSamples');
const clearChatButton = document.getElementById('clearChat');
const exportChatButton = document.getElementById('exportChat');
const checkServicesButton = document.getElementById('checkServices');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    checkServiceStatus();
});

function initializeChat() {
    // Generate a new chat ID
    chatId = generateChatId();
    sessionIdElement.textContent = chatId.substring(0, 8);
    
    // Focus on input
    messageInput.focus();
}

function generateChatId() {
    return 'chat_' + Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
}

function setupEventListeners() {
    // Send message on Enter key
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Send button click
    sendButton.addEventListener('click', sendMessage);
    
    // Character count
    messageInput.addEventListener('input', function(e) {
        const charCount = e.target.value.length;
        document.querySelector('.char-count').textContent = `${charCount}/500`;
    });
    
    // Help button
    helpButton.addEventListener('click', function() {
        samplesModal.style.display = 'flex';
    });
    
    // Close modal
    closeSamplesButton.addEventListener('click', function() {
        samplesModal.style.display = 'none';
    });
    
    // Click outside modal to close
    samplesModal.addEventListener('click', function(e) {
        if (e.target === samplesModal) {
            samplesModal.style.display = 'none';
        }
    });
    
    // Sample questions
    document.querySelectorAll('.sample-question').forEach(button => {
        button.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            messageInput.value = question;
            samplesModal.style.display = 'none';
            sendMessage();
        });
    });
    
    // Action buttons
    clearChatButton.addEventListener('click', clearChat);
    exportChatButton.addEventListener('click', exportChat);
    checkServicesButton.addEventListener('click', checkServiceStatus);
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Disable input and show typing indicator
    setInputState(false);
    showTypingIndicator(true);
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    document.querySelector('.char-count').textContent = '0/500';
    
    try {
        // Send to chat service
        const response = await fetch(`${CHAT_SERVICE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                chat_id: chatId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add bot response to chat
        addMessage(data.response, 'bot', data.source);
        
        // Update UI
        messageCount++;
        messageCountElement.textContent = messageCount;
        lastSourceElement.textContent = data.source || 'unknown';
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage(
            "I'm sorry, I'm having trouble connecting to the server. Please try again later.",
            'bot',
            'error'
        );
    } finally {
        // Re-enable input and hide typing indicator
        setInputState(true);
        showTypingIndicator(false);
        messageInput.focus();
    }
}

function addMessage(text, sender, source = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    if (sender === 'bot') {
        messageDiv.classList.add('bot-message');
    } else {
        messageDiv.classList.add('user-message');
    }
    
    const timestamp = new Date().toLocaleTimeString();
    const sourceText = source ? formatSource(source) : (sender === 'user' ? 'You' : 'AI');
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${sender === 'bot' ? 'fa-robot' : 'fa-user'}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${formatMessageText(text)}</div>
            <div class="message-meta">
                <span class="message-time">${timestamp}</span>
                <span class="message-source">${sourceText}</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessageText(text) {
    // Basic formatting for message text
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
        .replace(/\n/g, '<br>')                            // Line breaks
        .replace(/`(.*?)`/g, '<code>$1</code>');           // Code
}

function formatSource(source) {
    const sourceMap = {
        'knowledge_base': 'Knowledge Base',
        'web_search': 'Web Search',
        'fallback': 'Fallback',
        'error': 'Error'
    };
    return sourceMap[source] || source;
}

function setInputState(enabled) {
    messageInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    
    if (enabled) {
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
    } else {
        sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
}

function showTypingIndicator(show) {
    typingIndicator.style.display = show ? 'inline-flex' : 'none';
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Remove all messages except welcome message
        const messages = chatMessages.querySelectorAll('.message:not(.welcome-message .message)');
        messages.forEach(message => message.remove());
        
        // Reset counters
        messageCount = 0;
        messageCountElement.textContent = '0';
        lastSourceElement.textContent = '-';
        
        // Generate new chat ID
        chatId = generateChatId();
        sessionIdElement.textContent = chatId.substring(0, 8);
        
        messageInput.focus();
    }
}

function exportChat() {
    const messages = [];
    const messageElements = chatMessages.querySelectorAll('.message');
    
    messageElements.forEach(messageEl => {
        const text = messageEl.querySelector('.message-text').textContent;
        const time = messageEl.querySelector('.message-time').textContent;
        const source = messageEl.querySelector('.message-source').textContent;
        const isBot = messageEl.classList.contains('bot-message');
        
        messages.push({
            text: text,
            time: time,
            source: source,
            sender: isBot ? 'AI' : 'User'
        });
    });
    
    const exportData = {
        chatId: chatId,
        timestamp: new Date().toISOString(),
        messageCount: messages.length,
        messages: messages
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${chatId.substring(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function checkServiceStatus() {
    const statusIndicators = {
        'chat-status': { url: `${CHAT_SERVICE_URL}/health`, name: 'Chat Service' },
        'kb-status': { url: `${CHAT_SERVICE_URL.replace('8000', '8001')}/health`, name: 'Knowledge Base' },
        'search-status': { url: `${CHAT_SERVICE_URL.replace('8000', '8002')}/health`, name: 'Search Service' },
        'history-status': { url: `${CHAT_SERVICE_URL.replace('8000', '8003')}/health`, name: 'History Service' }
    };
    
    for (const [elementId, config] of Object.entries(statusIndicators)) {
        const indicator = document.getElementById(elementId);
        const icon = indicator.querySelector('i');
        
        try {
            const response = await fetch(config.url, { timeout: 5000 });
            if (response.ok) {
                icon.style.color = '#00ff00';  // Green
                indicator.title = `${config.name}: Healthy`;
            } else {
                throw new Error('Service unhealthy');
            }
        } catch (error) {
            icon.style.color = '#ff0000';  // Red
            indicator.title = `${config.name}: Unreachable`;
        }
    }
    
    // Show status check message
    addMessage(
        'Service status check completed. Check the indicators in the header for current status.',
        'bot',
        'system'
    );
}

// Auto-check services on load
setTimeout(checkServiceStatus, 2000);
