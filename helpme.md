# Friday Voice Assistant - Setup Guide

## Overview

Friday is an AI voice assistant powered by LiveKit and Google's Realtime AI. It runs as both a backend agent and a Python Tkinter GUI client.

## Architecture

- **Backend Agent** (`agent.py`): Runs on LiveKit, handles AI logic, tools, and voice processing
- **GUI Client** (`voice_assistant_gui.py`): Tkinter-based desktop app for user interaction
- **LiveKit Sandbox**: Cloud infrastructure connecting client and agent

## Prerequisites

1. Python 3.9 or higher
2. LiveKit account with sandbox setup
3. Google API key for Realtime AI
4. Gmail credentials (for email tool)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

The `.env` file contains all necessary credentials:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://jarvis-20-mlty1z78.livekit.cloud
LIVEKIT_API_KEY=APIH5fxsxuqvE2N
LIVEKIT_API_SECRET=DNxmFcb27VPGXyWGUHeufDSXrc25GBLrJsmZOJLAaBi

# Google API (for Realtime AI)
GOOGLE_API_KEY=AIzaSyDuImBTFxzPPOEA_4qrlxGGh6iRv1FHUQA

# Gmail Configuration (for email tool)
GMAIL_USER=ashokbk215@gmail.com
GMAIL_APP_PASSWORD=xlrhzjfyvrgrmpiq
```

**Important**: Never commit this file to public repositories!

### 3. Sandbox Configuration

The sandbox ID is hardcoded in `voice_assistant_gui.py`:

```python
self.sandbox_id = "digital-syscall-116ehj"
```

## Running the Application

### Step 1: Start the Backend Agent

Open a terminal and run:

```bash
python agent.py
```

This starts the LiveKit agent worker that will:

- Connect to your LiveKit cloud instance
- Wait for client connections
- Handle voice processing and AI responses
- Execute tools (weather, web search, email)

You should see output like:

```
INFO:livekit:Connecting to ws://...
INFO:livekit:Worker started, waiting for jobs...
```

### Step 2: Launch the GUI Client

Open another terminal and run:

```bash
python voice_assistant_gui.py
```

This opens the Friday voice assistant GUI.

### Step 3: Connect and Talk

1. Click **"Connect to Friday"** button
2. Wait for status to show "● Connected" (green)
3. Click and hold **"🎤 Push to Talk"** button
4. Speak your request
5. Release button when done
6. Friday will respond with voice and text

## Features

### Available Tools

Friday can:

1. **Get Weather**: "What's the weather in New York?"
2. **Search Web**: "Search for latest AI news"
3. **Send Email**: "Send an email to john@example.com with subject 'Meeting' and message 'Let's meet tomorrow'"

### GUI Features

- Real-time connection status indicator
- Conversation log showing all interactions
- Push-to-talk voice input
- Visual feedback for all states

## Console Mode (Alternative)

If you don't want to use the GUI, you can run in console mode:

```bash
# List audio devices
python agent.py console --list-devices

# Run with specific microphone (e.g., headphone mic)
python agent.py console --input-device 2
```

## Troubleshooting

### Connection Issues

**Problem**: "Failed to get connection token"
**Solution**:

- Verify sandbox ID is correct
- Check internet connection
- Ensure LiveKit sandbox is active

**Problem**: Agent doesn't respond
**Solution**:

- Make sure `agent.py` is running in a separate terminal
- Check agent terminal for errors
- Verify GOOGLE_API_KEY is valid

### Audio Issues

**Problem**: Can't hear Friday's responses
**Solution**:

- Check system audio settings
- Ensure default audio output is correct
- Try reconnecting

**Problem**: Friday can't hear you
**Solution**:

- Check microphone permissions
- Verify default input device
- Hold push-to-talk button while speaking

### Tool Errors

**Problem**: Email sending fails
**Solution**:

- Use Gmail App Password (not regular password)
- Enable 2FA on Gmail account
- Generate App Password in Google Account settings

**Problem**: Weather/Search not working
**Solution**:

- Check internet connection
- APIs might be rate-limited, wait and retry

## Advanced Configuration

### Customizing Friday's Personality

Edit `prompts.py`:

```python
AGENT_INSTRUCTION = """
# Persona
Change this to modify Friday's behavior and tone
"""
```

### Adding New Tools

1. Create function in `tools.py`:

```python
@function_tool()
async def my_new_tool(context: RunContext, param: str) -> str:
    """Tool description"""
    # Your code here
    return "Result"
```

2. Add to agent in `agent.py`:

```python
tools=[
    get_weather,
    search_web,
    send_email,
    my_new_tool  # Add here
],
```

### Changing Voice

Edit `agent.py`:

```python
llm=google.beta.realtime.RealtimeModel(
    voice="Aoede",  # Change to: Charon, Kore, Fenrir, Puck
    temperature=0.8,
),
```

## Architecture Details

### How It Works

1. **Client Connects**: GUI requests token from LiveKit sandbox
2. **Room Created**: Both client and agent join same room
3. **Voice Flow**:
   - User speaks → Audio sent to LiveKit → Agent receives
   - Agent processes with Google Realtime AI
   - Response sent back → Client plays audio

### Data Flow

```
[User] → [Microphone] → [LiveKit Cloud] → [Agent.py]
                                              ↓
                                         [Google AI]
                                              ↓
                                         [Tools Execute]
                                              ↓
[Speaker] ← [LiveKit Cloud] ← [Response + Audio]
```

## Security Notes

- Never share your `.env` file
- Use App Passwords for Gmail
- Rotate API keys periodically
- Sandbox is for development only
- For production, use LiveKit self-hosted or enterprise

## Resources

- LiveKit Docs: https://docs.livekit.io/
- LiveKit Agents: https://docs.livekit.io/agents/overview/
- Google Realtime AI: https://ai.google.dev/
- LiveKit Sandbox: https://cloud.livekit.io/
- Tutorial Video: https://www.youtube.com/watch?v=CVkpsWpM3c0

## Support

- LiveKit Slack: https://livekit.io/join-slack
- GitHub Issues: https://github.com/livekit/livekit
