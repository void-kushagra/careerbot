async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const userText = input.value.trim();
  if (!userText) return;

  // Add user message
  const userMsg = document.createElement("div");
  userMsg.className = "chat-message user";
  userMsg.textContent = userText;
  chatBox.appendChild(userMsg);

  // Add loading bot message
  const botMsg = document.createElement("div");
  botMsg.className = "chat-message bot";
  botMsg.textContent = "Typing...";
  chatBox.appendChild(botMsg);
  chatBox.scrollTop = chatBox.scrollHeight;

  // Fetch response from Flask
  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: userText })
    });

    const data = await response.json();
    botMsg.textContent = data.answer;
  } catch (err) {
    botMsg.textContent = "Oops! Something went wrong.";
  }

  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
}
