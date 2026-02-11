Voice AI Agent — Tool-Using Conversational Assistant

📌 Overview

This project is a real-time voice-controlled AI agent that listens to spoken input, reasons step-by-step using structured planning, optionally calls external tools, and responds using synthesized speech.

It demonstrates how to build a tool-augmented LLM agent with:

Speech recognition
Structured reasoning
Tool execution
Streaming text-to-speech
Continuous conversation loop

🧠 Core Concept — Structured Agent Reasoning

Unlike standard chatbots, this agent follows a strict reasoning architecture:

START → PLAN → TOOL → OBSERVE → OUTPUT

Each response from the model is forced into a JSON schema so that the program can:

Understand what the model is doing
Decide when to run tools
Control execution flow safely

⚙️ Features

🎤 Real-time microphone input
🔊 Voice response playback
🧩 Tool-calling system
📜 JSON-structured reasoning
🔁 Continuous listening loop
🧠 Step-by-step planning logic
⚡ Async streaming TTS
🛠 Extensible tool architecture

🏗 System Architecture
Input Layer

Speech captured using:

speech_recognition
Reasoning Engine

The LLM is forced to respond in structured format using a Pydantic schema:

class MyOutputFormat(BaseModel):
    step: str
    content: Optional[str]
    tool: Optional[str]
    input: Optional[str]

This guarantees predictable execution logic.

Tool Execution Layer

Tools are registered dynamically:

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}

If the model requests a tool call, the program executes it and feeds the result back.

Output Layer

Responses are spoken using streaming TTS:

Model: gpt-4o-mini-tts
Voice: coral

🛠 Built-in Tools
🌤 Weather Tool

Gets live weather using wttr.in:

get_weather(city)

💻 Command Execution Tool

Runs system commands:

run_command(cmd)

⚠️ Security Warning
This executes commands on your machine. Only run locally and never expose publicly.

📦 Installation
git clone https://github.com/yourusername/voice-ai-agent.git
cd voice-ai-agent
pip install -r requirements.txt

🔑 Environment Variables

Create .env

OPENAI_API_KEY=your_api_key_here

▶️ Run the Assistant
python main.py

Then speak into your microphone.

💬 Example Interaction

User:

What's the weather in Karachi?

Agent reasoning steps

PLAN → User wants weather
PLAN → Weather tool available
TOOL → get_weather("karachi")
OBSERVE → Cloudy 20°C
OUTPUT → The weather in Karachi is 20°C and cloudy.

📂 Project Structure
voice-ai-agent/
│
├── main.py
├── .env.example
├── README.md
└── requirements.txt

➕ Adding Custom Tools

You can easily extend the assistant:

def get_time(city):
    return "12:00 PM"

available_tools["get_time"] = get_time

The agent will automatically learn when to use it.

🔐 Security Best Practices

If deploying or sharing:

Remove system command tool
Sandbox execution
Validate tool inputs
Add authentication

🎯 Use Cases

Voice assistants
AI copilots
Dev automation
Accessibility interfaces
Smart home control
Interactive demos
AI agent experimentation

🧠 Concepts Demonstrated

This project showcases real-world AI engineering concepts:

Tool-calling LLM agents
Structured outputs
Voice interfaces
Async programming
Model orchestration

Human-AI interaction design

🤝 Contributing

Contributions are welcome.

Steps:

Fork repo

Create feature branch

Commit changes

Submit PR
