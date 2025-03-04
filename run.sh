#!/bin/bash

# 🚀 Activate Conda Environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate rasa-llama || { echo "❌ Failed to activate Conda environment"; exit 1; }

# Ensure logs directory exists
mkdir -p logs

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
    check_port 80    # Nginx
    check_port 5173  # React Frontend

    echo "🔹 Starting Nginx..."
    sudo rm -f /opt/homebrew/var/run/nginx.pid  # Ensure clean restart
    sudo nginx || { echo "❌ Failed to start Nginx"; exit 1; }

    echo "🔹 Starting LLaMA API..."
    nohup uvicorn llama_server:app --host 0.0.0.0 --port 8000 --app-dir llama > logs/llama.log 2>&1 &

    echo "🔹 Starting Rasa Actions..."
    nohup rasa run actions > logs/actions.log 2>&1 &

    echo "🔹 Starting Rasa Chatbot..."
    nohup rasa run --enable-api --cors "*" > logs/rasa.log 2>&1 &

    echo "🔹 Starting Cloudflare Tunnel..."
    nohup cloudflared tunnel run rasa-chatbot > logs/cloudflare.log 2>&1 &

    echo "🔹 Starting React Frontend..."
    cd chatbot-app
    nohup serve -s build > ../logs/frontend.log 2>&1 &  # No rebuild unless needed
    cd ..

    echo "🎉 Chatbot services started!"
}

# Function to stop all chatbot services
stop_services() {
    echo "🔹 Stopping all chatbot services..."
    sudo pkill -f rasa
    sudo pkill -f uvicorn
    sudo pkill -f cloudflared
    sudo pkill -f nginx
    sudo pkill -f serve
    sudo rm -f /opt/homebrew/var/run/nginx.pid  # Ensure clean restart for next time
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
