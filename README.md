# Rasa + LLaMA Chatbot
A conversational AI chatbot powered by **Rasa** for dialogue management and **Meta’s LLaMA** for natural language responses.

## ** Features**
 **Conversational AI** using Rasa’s intent-based dialogue management  
 **LLaMA 1B Instruct Model** for high-quality responses  
 **Context Awareness** with persistent chat history  
 **Cloudflare Tunnel Support** for remote access  
 **FastAPI Backend** for easy API communication  

---

## ** Installation & Setup**
### **1️ Clone the Repository**
```bash
git clone https://github.com/your-repo/rasa-llama-chatbot.git
cd rasa-llama-chatbot
```

### **2️ Setup Python Environment**
Ensure **Python 3.9+** is installed, then create a Conda environment:
```bash
conda create --name rasa-llama python=3.9 -y
conda activate rasa-llama
```

### **3️ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️ Setup Environment Variables**
Create a `.env` file and add your **Hugging Face API token**:
```bash
echo "HUGGINGFACE_TOKEN=your_token_here" > .env
```

### **5️ Download LLaMA Model**
Before running the chatbot, authenticate with Hugging Face and download the model:
```bash
python -c "from huggingface_hub import login; login()"
```

---

## ** Running the Chatbot**
### ** Start All Services Using `run.sh`**
```bash
chmod +x run.sh
./run.sh start
```

### ** Stop All Services**
```bash
./run.sh stop
```

This script:
- Starts **Rasa**
- Launches the **LLaMA API**
- Runs **Rasa Actions**
- Starts **Cloudflare Tunnel**
- Boots the **React Frontend**
- Launches **Nginx** for static hosting

---

## ** Manual Startup (If Needed)**
### **1️ Start the LLaMA API**
```bash
uvicorn llama.llama_server:app --host 0.0.0.0 --port 8000 --reload
```

### **2️ Start Rasa Actions**
```bash
rasa run actions --debug
```

### **3️ Start Rasa Core**
```bash
rasa run --enable-api --debug
```

### **4️ Test LLaMA API**
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": [{"role": "user", "content": "Hello!"}]}'
```

Expected output:
```json
{"response": "Hello! How can I assist you today?"}
```

### **5️ Test Rasa Chatbot**
```bash
curl -X POST "http://localhost:5005/webhooks/rest/webhook" \
     -H "Content-Type: application/json" \
     -d '{"sender": "test_user", "message": "Tell me about Mexico."}'
```
Expected output:
```json
[
    {
        "recipient_id": "test_user",
        "text": "Mexico is a country located in North America..."
    }
]
```

---

## ** Troubleshooting**
### **1️ LLaMA API Not Responding?**
Check if the **LLaMA API is running**:
```bash
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '{"prompt": [{"role": "user", "content": "Hi."}]}'
```
If it fails, restart the API:
```bash
uvicorn llama.llama_server:app --host 0.0.0.0 --port 8000 --reload
```

### **2️ Rasa Actions Not Running?**
Check if the **actions server is running**:
```bash
curl -X POST "http://localhost:5005/webhooks/rest/webhook" -H "Content-Type: application/json" -d '{"sender": "test_user", "message": "Hello"}'
```
If it fails, restart actions:
```bash
rasa run actions --debug
```

### **3 Issues with Ports?**
Kill any processes blocking ports:
```bash
sudo lsof -i :8000   # Find process using port 8000
sudo kill -9 <PID>   # Replace <PID> with the actual process ID
```
Then restart the services:
```bash
./run.sh start
```
