#!/bin/bash

# 🚀 Activate Conda Environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate rasa-llama || { echo "❌ Failed to activate Conda environment"; exit 1; }

# Function to check if a port is in use and kill the process
function check_port {
    lsof -i :$1 > /dev/null && echo "❌ Port $1 is in use! Killing process..." && kill -9 $(lsof -ti :$1) || echo "✅ Port $1 is available."
}

# Function to start all chatbot services
start_services() {
    echo "🔹 Checking if required ports are available..."
    check_port 5005  # Rasa Main Server
    check_port 5055  # Rasa Actions Server
    check_port 8000  # LLaMA API

    echo "🔹 Starting LLaMA API..."
    nohup uvicorn llama_server:app --host 0.0.0.0 --port 8000 --app-dir llama > logs/llama.log 2>&1 &

    echo "🔹 Starting Rasa Actions..."
    nohup rasa run actions > logs/actions.log 2>&1 &

    echo "🔹 Starting Rasa Chatbot..."
    nohup rasa run --enable-api --cors "*" > logs/rasa.log 2>&1 &

    echo "🔹 Starting Cloudflare Tunnel..."
    nohup cloudflared tunnel run rasa-chatbot > logs/cloudflare.log 2>&1 &

    echo "🎉 Chatbot services started! Test with:"
    echo "👉 curl -X POST 'https://chat.ramon-services.com/webhooks/rest/webhook' -H 'Content-Type: application/json' -d '{\"sender\": \"test_user\", \"message\": \"Hello\"}'"
}

# Function to stop all chatbot services
stop_services() {
    echo "🔹 Stopping all chatbot services..."
    pkill -f rasa
    pkill -f uvicorn
    pkill -f cloudflared
    echo "✅ All services stopped!"
}

# Check user input
if [[ "$1" == "start" ]]; then
    start_services
elif [[ "$1" == "stop" ]]; then
    stop_services
else
    echo "❌ Invalid argument!"
    echo "Usage: $0 {start|stop}"
    exit 1
fi
