function showQuestionGenerator() {
    hideAllSections();
    document.getElementById('question-generator').classList.remove('hidden');
}

function showMockInterview() {
    hideAllSections();
    document.getElementById('mock-interview').classList.remove('hidden');
}

function showAnswerEvaluator() {
    hideAllSections();
    document.getElementById('answer-evaluator').classList.remove('hidden');
}

function hideAllSections() {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
}

document.getElementById('question-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const role = document.getElementById('role').value;
    const experience = document.getElementById('experience').value;
    const numQuestions = document.getElementById('num-questions').value;
    const output = document.getElementById('questions-output');
    output.innerHTML = '<div class="loading">Generating questions...</div>';
    try {
        const response = await fetch('/generate-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: role, experience: experience, num_questions: numQuestions })
        });
        const data = await response.json();
        let html = '<h3>Generated Questions:</h3><ol>';
        data.questions.forEach(question => {
            if (question.trim()) { html += `<li>${question}</li>`; }
        });
        html += '</ol>';
        output.innerHTML = html;
    } catch (error) {
        output.innerHTML = '<p style="color: red;">Error generating questions. Please try again.</p>';
    }
});

let mockInterviewStarted = false;

async function startMockInterview() {
    const role = document.getElementById('mock-role').value;
    if (!role) { alert('Please enter a job role'); return; }
    mockInterviewStarted = true;
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    addMessage('ai', 'Hello! I will be conducting your interview today. Let us begin...');
    await sendMessage('Start the interview for ' + role);
}

async function sendAnswer() {
    const input = document.getElementById('user-answer');
    const message = input.value.trim();
    if (!message || !mockInterviewStarted) return;
    addMessage('user', message);
    input.value = '';
    await sendMessage(message);
}

async function sendMessage(message) {
    const role = document.getElementById('mock-role').value;
    try {
        const response = await fetch('/mock-interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: role, message: message })
        });
        const data = await response.json();
        addMessage('ai', data.response);
    } catch (error) {
        addMessage('ai', 'Sorry, there was an error. Please try again.');
    }
}

function addMessage(type, text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.getElementById('evaluation-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = document.getElementById('eval-question').value;
    const answer = document.getElementById('eval-answer').value;
    const output = document.getElementById('feedback-output');
    output.innerHTML = '<div class="loading">Evaluating your answer...</div>';
    try {
        const response = await fetch('/evaluate-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question, answer: answer })
        });
        const data = await response.json();
        output.innerHTML = `<h3>Feedback:</h3><div>${data.feedback.replace(/\n/g, '<br>')}</div>`;
    } catch (error) {
        output.innerHTML = '<p style="color: red;">Error evaluating answer. Please try again.</p>';
    }
});

document.getElementById('user-answer')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') { sendAnswer(); }
});
