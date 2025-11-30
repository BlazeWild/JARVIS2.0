# 🎙️ JARVIS 2.0 - Voice Assistant

AI-powered voice assistant with continuous conversation, interruption support, and real-time audio processing using LiveKit and Google Realtime AI.

## ✨ Features

- 🎤 **Continuous Voice Conversation** - Just talk, no buttons needed
- 🔊 **Real-time Audio Visualization** - See your voice and JARVIS's response in real-time
- 🚫 **Interruption Support** - Interrupt JARVIS anytime during conversation
- 🛠️ **Built-in Tools** - Weather lookup, web search, email sending
- ☁️ **Cloud-hosted Agent** - Runs on LiveKit's servers (FREE)
- 🎨 **Desktop UI** - Clean Tkinter interface

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required credentials:

- **LiveKit** - Get from [LiveKit Cloud](https://cloud.livekit.io/)
- **Google API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gmail** (optional) - For email sending tool

### 3. Start the Agent

In terminal 1:

```bash
python agent.py start
```

Wait for: `"message": "registered worker"`

### 4. Launch Desktop UI

In terminal 2:

```bash
python friday.py
```

The UI will auto-connect and you can start talking immediately!

## 🎯 Usage

1. Window opens and auto-connects to JARVIS
2. Speak naturally - no buttons to press
3. Green bar shows your voice level
4. Cyan bar shows JARVIS's response
5. You can interrupt JARVIS anytime

## 🛠️ Available Tools

```bash
# Weather
"What's the weather in Tokyo?"

# Web Search
"Search for latest AI news"

# Email
"Send an email to someone@example.com with subject Hello"
```

## 📁 Project Structure

```
JARVIS_MOBILE/
├── agent.py              # Backend AI agent
├── friday.py             # Desktop UI client
├── tools.py              # Weather, search, email tools
├── prompts.py            # JARVIS personality
├── requirements.txt      # Python dependencies
├── .env                  # Your credentials (not in git)
├── .env.example          # Template for credentials
└── README.md            # This file
```

## 🎭 Customization

### Change Voice

Edit `agent.py`:

```python
voice="Aoede"  # Options: Charon, Kore, Fenrir, Puck
```

### Change Personality

Edit `prompts.py`:

```python
AGENT_INSTRUCTION = """Your custom personality"""
```

### Add Custom Tools

1. Create function in `tools.py`:

```python
@function_tool()
async def my_tool(context: RunContext, param: str) -> str:
    """Tool description"""
    # Your code
    return "result"
```

2. Add to `agent.py`:

```python
tools=[
    get_weather,
    search_web,
    send_email,
    my_tool  # Add here
]
```

## 🔧 Troubleshooting

### Microphone Not Working

The app uses audio device index 2 by default. To change:

1. List devices:

```bash
python agent.py console --list-devices
```

2. Edit `friday.py` line with `device_index = 2` to your device number

### Agent Not Responding

1. Make sure agent is running: `python agent.py start`
2. Check for "registered worker" message
3. Verify GOOGLE_API_KEY in `.env`

### No Audio Output

1. Check speaker volume
2. Verify default audio output in Windows Sound settings
3. Look for cyan bar movement (indicates audio received)

## 🏗️ Architecture

```
[Your Mic] --WebRTC--> [LiveKit Cloud] ---> [Agent Worker]
    ↑                       ↕                     ↓
  Green Bar            Duplex Audio      [Google Realtime AI]
    ↓                       ↕                     ↓
[Your Speaker] <-WebRTC-- [LiveKit Cloud] <--- [Response]
    ↑
  Cyan Bar
```

## 📋 Requirements

- Python 3.9+
- PyAudio
- LiveKit account (free tier available)
- Google API key
- Windows/Mac/Linux

## 🔐 Security

- Never commit `.env` file
- Use Gmail App Passwords (not regular password)
- LiveKit sandbox is for development only
- Rotate API keys periodically

## 📚 Resources

- [LiveKit Docs](https://docs.livekit.io/)
- [LiveKit Agents](https://docs.livekit.io/agents/)
- [Google Realtime AI](https://ai.google.dev/)
- [LiveKit Cloud](https://cloud.livekit.io/)

## 📄 License

MIT License - Feel free to use and modify

## 🤝 Contributing

Issues and pull requests welcome!

---

**Made with ❤️ using LiveKit and Google AI**
