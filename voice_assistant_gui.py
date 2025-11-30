"""
Friday Voice Assistant - Tkinter GUI Client
Connects to LiveKit sandbox and provides a voice assistant interface
"""

import asyncio
import tkinter as tk
from tkinter import ttk, scrolledtext
import os
from datetime import datetime
from dotenv import load_dotenv
from livekit import rtc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Friday - Voice Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # LiveKit connection variables
        self.room = None
        self.audio_source = None
        self.is_connected = False
        self.is_speaking = False
        
        # Get sandbox credentials
        self.sandbox_id = "digital-syscall-116ehj"
        self.livekit_url = os.getenv("LIVEKIT_URL")
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the GUI components"""
        # Title
        title_frame = tk.Frame(self.root, bg='#1a1a1a')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="F.R.I.D.A.Y.",
            font=("Arial", 32, "bold"),
            fg='#00d4ff',
            bg='#1a1a1a'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Female Replacement Intelligent Digital Assistant Youth",
            font=("Arial", 10, "italic"),
            fg='#888888',
            bg='#1a1a1a'
        )
        subtitle_label.pack()
        
        # Status indicator
        status_frame = tk.Frame(self.root, bg='#1a1a1a')
        status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Disconnected",
            font=("Arial", 12),
            fg='#ff4444',
            bg='#1a1a1a'
        )
        self.status_label.pack()
        
        # Conversation log
        log_frame = tk.Frame(self.root, bg='#1a1a1a')
        log_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="Conversation Log",
            font=("Arial", 12, "bold"),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        log_label.pack(anchor='w')
        
        self.conversation_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=15,
            font=("Consolas", 10),
            bg='#2a2a2a',
            fg='#00ff00',
            insertbackground='#00ff00',
            state='disabled'
        )
        self.conversation_log.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#1a1a1a')
        button_frame.pack(pady=20)
        
        self.connect_button = tk.Button(
            button_frame,
            text="Connect to Friday",
            command=self.toggle_connection,
            font=("Arial", 12, "bold"),
            bg='#00d4ff',
            fg='#000000',
            activebackground='#00a8cc',
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        self.connect_button.pack(side=tk.LEFT, padx=10)
        
        self.speak_button = tk.Button(
            button_frame,
            text="🎤 Push to Talk",
            command=self.toggle_speaking,
            font=("Arial", 12, "bold"),
            bg='#444444',
            fg='#ffffff',
            activebackground='#666666',
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            state='disabled'
        )
        self.speak_button.pack(side=tk.LEFT, padx=10)
        
        # Info label
        info_label = tk.Label(
            self.root,
            text=f"Sandbox: {self.sandbox_id}",
            font=("Arial", 8),
            fg='#666666',
            bg='#1a1a1a'
        )
        info_label.pack(pady=5)
        
    def log_message(self, message, sender="System"):
        """Add a message to the conversation log"""
        self.conversation_log.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "System":
            color_tag = "system"
            self.conversation_log.tag_config("system", foreground="#00d4ff")
        elif sender == "User":
            color_tag = "user"
            self.conversation_log.tag_config("user", foreground="#ffff00")
        elif sender == "Friday":
            color_tag = "friday"
            self.conversation_log.tag_config("friday", foreground="#00ff00")
        else:
            color_tag = "default"
            
        self.conversation_log.insert(tk.END, f"[{timestamp}] {sender}: ", color_tag)
        self.conversation_log.insert(tk.END, f"{message}\n")
        self.conversation_log.see(tk.END)
        self.conversation_log.configure(state='disabled')
        
    def update_status(self, status, color):
        """Update the status indicator"""
        self.status_label.config(text=f"● {status}", fg=color)
        
    async def get_token(self):
        """Get connection token from LiveKit sandbox"""
        try:
            import requests
            
            token_endpoint = "https://cloud-api.livekit.io/api/sandbox/connection-details"
            headers = {"X-Sandbox-ID": self.sandbox_id}
            
            response = requests.get(token_endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data['serverUrl'], data['participantToken']
            else:
                logger.error(f"Failed to get token: {response.status_code}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error getting token: {e}")
            return None, None
            
    async def connect_to_room(self):
        """Connect to LiveKit room"""
        try:
            self.log_message("Connecting to Friday...", "System")
            self.update_status("Connecting...", "#ffaa00")
            
            # Get token from sandbox
            server_url, token = await self.get_token()
            
            if not server_url or not token:
                self.log_message("Failed to get connection token", "System")
                self.update_status("Connection Failed", "#ff4444")
                return False
            
            # Create room instance
            self.room = rtc.Room()
            
            # Setup event handlers
            @self.room.on("participant_connected")
            def on_participant_connected(participant: rtc.RemoteParticipant):
                self.log_message(f"Agent joined: {participant.identity}", "System")
                
            @self.room.on("track_subscribed")
            def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    self.log_message("Receiving audio from Friday", "System")
                    # Play the audio track
                    audio_stream = rtc.AudioStream(track)
                    asyncio.create_task(self.play_audio(audio_stream))
                    
            @self.room.on("data_received")
            def on_data_received(data: rtc.DataPacket):
                message = data.data.decode('utf-8')
                self.log_message(message, "Friday")
            
            # Connect to room
            await self.room.connect(server_url, token)
            
            self.is_connected = True
            self.update_status("Connected", "#00ff00")
            self.log_message("Connected successfully! Say 'Hi' to start.", "System")
            
            # Enable speak button
            self.speak_button.config(state='normal', bg='#00ff00', fg='#000000')
            
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.log_message(f"Connection error: {str(e)}", "System")
            self.update_status("Connection Failed", "#ff4444")
            return False
            
    async def disconnect_from_room(self):
        """Disconnect from LiveKit room"""
        try:
            if self.room:
                await self.room.disconnect()
                self.room = None
                
            self.is_connected = False
            self.update_status("Disconnected", "#ff4444")
            self.log_message("Disconnected from Friday", "System")
            
            # Disable speak button
            self.speak_button.config(state='disabled', bg='#444444', fg='#ffffff')
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            
    async def play_audio(self, audio_stream: rtc.AudioStream):
        """Play audio from the agent"""
        try:
            async for frame in audio_stream:
                # Audio playback handled by LiveKit SDK
                pass
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            
    async def start_speaking(self):
        """Start capturing and sending audio"""
        try:
            if not self.room or not self.is_connected:
                return
                
            self.log_message("Listening...", "User")
            self.speak_button.config(bg='#ff0000', text='🎤 Speaking...')
            
            # Create audio source
            self.audio_source = rtc.AudioSource(48000, 1)
            track = rtc.LocalAudioTrack.create_audio_track("microphone", self.audio_source)
            
            # Publish track
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            
            await self.room.local_participant.publish_track(track, options)
            
        except Exception as e:
            logger.error(f"Error starting audio: {e}")
            self.log_message(f"Error: {str(e)}", "System")
            
    async def stop_speaking(self):
        """Stop capturing audio"""
        try:
            self.speak_button.config(bg='#00ff00', text='🎤 Push to Talk')
            
            # Unpublish audio track
            if self.room and self.room.local_participant:
                for publication in self.room.local_participant.track_publications.values():
                    if publication.source == rtc.TrackSource.SOURCE_MICROPHONE:
                        await self.room.local_participant.unpublish_track(publication.sid)
                        
            self.audio_source = None
            
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
            
    def toggle_connection(self):
        """Toggle connection to LiveKit room"""
        if self.is_connected:
            asyncio.create_task(self.disconnect_from_room())
            self.connect_button.config(text="Connect to Friday", bg='#00d4ff')
        else:
            asyncio.create_task(self.connect_to_room())
            self.connect_button.config(text="Disconnect", bg='#ff4444')
            
    def toggle_speaking(self):
        """Toggle push-to-talk"""
        if not self.is_speaking:
            self.is_speaking = True
            asyncio.create_task(self.start_speaking())
        else:
            self.is_speaking = False
            asyncio.create_task(self.stop_speaking())


async def main():
    """Main entry point"""
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    
    # Run tkinter event loop with asyncio
    while True:
        root.update()
        await asyncio.sleep(0.01)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application closed by user")
