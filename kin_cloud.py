from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OPENROUTER_API_KEY = "PASTE_YOUR_KEY_HERE"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>K.I.N</title>

<style>
:root {
  --blue: #3b82f6;
  --yellow: #facc15;
  --glass: rgba(255,255,255,0.15);
}

body {
  margin:0;
  font-family:Segoe UI, sans-serif;
  background: linear-gradient(135deg, var(--blue), var(--yellow));
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
}

#container {
  width:95%;
  max-width:900px;
  height:90vh;
  background:var(--glass);
  backdrop-filter: blur(15px);
  border-radius:20px;
  padding:20px;
  display:flex;
  flex-direction:column;
}

h1 { color:white; text-align:center; }

#chat { flex:1; overflow-y:auto; color:white; }

.message { margin-bottom:12px; }

img.chat-img {
  max-width:220px;
  border-radius:10px;
  margin-top:6px;
  display:block;
}

#input-area { display:flex; gap:8px; }

input[type=text] {
  flex:1;
  padding:12px;
  border-radius:12px;
  border:none;
}

button {
  padding:12px;
  border-radius:12px;
  border:none;
  background:#2563eb;
  color:white;
}
</style>
</head>

<body>
<div id="container">
<h1>K.I.N</h1>
<div id="chat"></div>

<div id="input-area">
<input id="textInput" placeholder="Talk to K.I.N">
<input type="file" id="imageInput" accept="image/*">
<button onclick="sendMessage()">Send</button>
</div>
</div>

<script>
const chat = document.getElementById("chat");

function addMessage(sender,text,image=null){
 let div=document.createElement("div");
 div.className="message";
 div.innerHTML="<b>"+sender+":</b> "+text;

 if(image){
   let img=document.createElement("img");
   img.src=image;
   img.className="chat-img";
   div.appendChild(img);
 }

 chat.appendChild(div);
 chat.scrollTop=chat.scrollHeight;
}

async function sendMessage(){
 let text=document.getElementById("textInput").value;
 let imgInput=document.getElementById("imageInput");

 addMessage("You",text);

 let base64=null;

 if(imgInput.files.length>0){
   let reader=new FileReader();
   reader.onload=async ()=>{
     base64=reader.result;
     await sendToServer(text,base64);
   }
   reader.readAsDataURL(imgInput.files[0]);
 } else {
   await sendToServer(text,null);
 }

 document.getElementById("textInput").value="";
 imgInput.value="";
}

async function sendToServer(message,image){
 let res=await fetch("/ask",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({message,image})
 });
 let data=await res.json();
 addMessage("K.I.N",data.response);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_PAGE

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_message = data.get("message", "")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are K.I.N, a friendly AI companion."},
                {"role": "user", "content": user_message}
            ]
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
