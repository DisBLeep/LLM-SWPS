document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
document.getElementById('file-input').addEventListener('change', function() {
    var file = this.files[0];
    if (file) {
        console.log("Selected file:", file.name);
        displayMessage(`Added file: ${file.name}`, 'user');
        sendFile(file); 
    }
});

// Function to handle sending messages to the server
function sendMessage() {
    var input = document.getElementById('chat-input');
    var message = input.value.trim();
    if (message !== "") {
        displayMessage(message, 'user');
        input.value = '';

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:5000/send-message", true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.responseType = 'text';
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    displayMessage(xhr.response, 'bot');
                } else {
                    console.error("Error sending message:", xhr.statusText);
                }
            }
        };
        xhr.send(JSON.stringify({ message: message }));
    }
}


// Function to send files to the server
function sendFile(file) {
}

// Function to display messages in the chat box
function displayMessage(message, sender) {
    var chatBox = document.getElementById('chat-box');
    var msgDiv = document.createElement('div');
    msgDiv.textContent = message;
    msgDiv.className = sender;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
