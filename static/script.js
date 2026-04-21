async function sendMessage() {
    let input = document.getElementById("user-input");
    let message = input.value.trim();

    if (!message) return;

    let chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `<div class="user-msg">${message}</div>`;

    let res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: message})
    });

    let data = await res.json();

    chatBox.innerHTML += `<div class="bot-msg">${data.response}</div>`;

    if (data.events) {
        data.events.forEach(e => {
            chatBox.innerHTML += `<div class="event-msg">👉 ${e}</div>`;
        });
    }

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("user-input").addEventListener("keypress", function(e){
    if(e.key === "Enter") sendMessage();
});