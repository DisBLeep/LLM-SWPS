document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keypress', function(e) {
    if(e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById('upload-btn').addEventListener('click', function() {
    document.getElementById('file-input').click(); 
});

document.getElementById('file-input').addEventListener('change', function() {
    var file = this.files[0];
    if (file) {
        console.log("Wybrano plik:", file.name);
        displayMessage(`Dodano plik: ${file.name}`, 'user');
    }
});

function sendMessage() {
    var input = document.getElementById('chat-input');
    var message = input.value.trim();
    if(message !== "") {
        displayMessage(message, 'user');
        input.value = ''; 
    }
}

function displayMessage(message, sender) {
    var chatBox = document.getElementById('chat-box');
    var msgDiv = document.createElement('div');
    msgDiv.textContent = message;
    msgDiv.className = sender;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
// Obsługa przesyłania plików PDF
document.getElementById('file-input').addEventListener('change', function() {
    var file = this.files[0];
    if (file) {
        console.log("Wybrano plik:", file.name);
        displayMessage(`Dodano plik: ${file.name}`, 'user');
        addPdfLink(file.name); 
    }
});

// Funkcja do dodawania linków do PDFów
function addPdfLink(fileName) {
    var pdfSidebar = document.getElementById('pdf-sidebar');
    var link = document.createElement('a');
    link.textContent = fileName;
    link.href = '#'; 
    link.className = 'pdf-link';
    pdfSidebar.appendChild(link);

    link.addEventListener('click', function(e) {
        e.preventDefault();
        // Tu możemy dodać funkcjonalność otwierającą PDF, np. w nowej zakładce
        console.log("Kliknięto PDF:", fileName);
    });
}