"""
Friday Voice Assistant - Automatic Voice Activity Detection
Continuous conversation with interruption support (like a phone call)
"""

import asyncio
import tkinter as tk
from tkinter import scrolledtext
import os
from datetime import datetime
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
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
        self.is_connected = False
        self.local_audio_track = None
        self.audio_source = None
        
        # Get sandbox credentials
        self.sandbox_id = "digital-syscall-116ehj"
        
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
            text="Continuous Voice Conversation with Interruption Support",
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
        
        # Voice activity indicator
        self.vad_label = tk.Label(
            status_frame,
            text="🎤 Listening...",
            font=("Arial", 10),
            fg='#00ff00',
            bg='#1a1a1a'
        )
        
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
            text="Start Call",
            command=self.toggle_connection,
            font=("Arial", 14, "bold"),
            bg='#00d4ff',
            fg='#000000',
            activebackground='#00a8cc',
            width=25,
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        self.connect_button.pack()
        
        # Info label
        info_label = tk.Label(
            self.root,
            text=f"Sandbox: {self.sandbox_id} | Auto Voice Detection | Interruption Enabled",
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
        
    def show_vad_indicator(self):
        """Show voice activity indicator"""
        self.vad_label.pack()
        
    def hide_vad_indicator(self):
        """Hide voice activity indicator"""
        self.vad_label.pack_forget()
        
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
        """Connect to LiveKit room with continuous audio"""
        try:
            self.log_message("Initiating call to Friday...", "System")
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
                self.log_message(f"Friday joined the call", "System")
                
            @self.room.on("participant_disconnected")
            def on_participant_disconnected(participant: rtc.RemoteParticipant):
                self.log_message(f"Friday left the call", "System")
                
            @self.room.on("track_subscribed")
            def on_track_subscribed(
                track: rtc.Track,
                publication: rtc.RemoteTrackPublication,
                participant: rtc.RemoteParticipant
            ):
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    self.log_message("Receiving audio from Friday", "System")
                    # Audio will automatically play through default output
                    audio_stream = rtc.AudioStream(track)
                    asyncio.create_task(self.play_audio_stream(audio_stream))
                    
            @self.room.on("track_unsubscribed")
            def on_track_unsubscribed(
                track: rtc.Track,
                publication: rtc.RemoteTrackPublication,
                participant: rtc.RemoteParticipant
            ):
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    self.log_message("Friday stopped speaking", "System")
                    
            @self.room.on("data_received")
            def on_data_received(data_packet: rtc.DataPacket):
                try:
                    message = data_packet.data.decode('utf-8')
                    self.log_message(message, "Friday")
                except:
                    pass
            
            # Connect to room
            await self.room.connect(server_url, token)
            
            self.is_connected = True
            self.update_status("Call Active", "#00ff00")
            self.log_message("Connected! Speak naturally, Friday can hear you.", "System")
            self.show_vad_indicator()
            
            # Start publishing microphone audio continuously
            await self.start_microphone()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.log_message(f"Connection error: {str(e)}", "System")
            self.update_status("Connection Failed", "#ff4444")
            return False
            
    async def play_audio_stream(self, audio_stream: rtc.AudioStream):
        """Play incoming audio from agent"""
        try:
            async for frame in audio_stream:
                # Audio frames are automatically played by LiveKit SDK
                pass
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            
    async def start_microphone(self):
        """Start continuous microphone capture and streaming"""
        try:
            if not self.room or not self.is_connected:
                return
            
            self.log_message("Microphone active - speak anytime", "System")
            
            # Create audio source from microphone
            # 48kHz sample rate, 1 channel (mono)
            self.audio_source = rtc.AudioSource(48000, 1)
            
            # Create local audio track
            self.local_audio_track = rtc.LocalAudioTrack.create_audio_track(
                "microphone",
                self.audio_source
            )
            
            # Publish track with source set to microphone
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            
            publication = await self.room.local_participant.publish_track(
                self.local_audio_track,
                options
            )
            
            logger.info(f"Microphone track published: {publication.sid}")
            
            # Start capturing audio from system microphone
            asyncio.create_task(self.capture_microphone_audio())
            
        except Exception as e:
            logger.error(f"Error starting microphone: {e}")
            self.log_message(f"Microphone error: {str(e)}", "System")
            
    async def capture_microphone_audio(self):
        """Capture audio from microphone and push to audio source"""
        try:
            import pyaudio
            import numpy as np
            
            # PyAudio setup
            p = pyaudio.PyAudio()
            
            # Open microphone stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                input=True,
                frames_per_buffer=480  # 10ms at 48kHz
            )
            
            self.log_message("Microphone capturing started", "System")
            
            while self.is_connected:
                # Read audio data
                data = stream.read(480, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_array = np.frombuffer(data, dtype=np.int16)
                
                # Create audio frame for LiveKit
                frame = rtc.AudioFrame(
                    data=audio_array.tobytes(),
                    sample_rate=48000,
                    num_channels=1,
                    samples_per_channel=480
                )
                
                # Push frame to audio source
                await self.audio_source.capture_frame(frame)
                
            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except ImportError:
            logger.error("PyAudio not installed. Run: pip install pyaudio")
            self.log_message("Error: PyAudio not installed. Run: pip install pyaudio", "System")
        except Exception as e:
            logger.error(f"Microphone capture error: {e}")
            self.log_message(f"Microphone capture error: {str(e)}", "System")
            
    async def disconnect_from_room(self):
        """Disconnect from LiveKit room"""
        try:
            self.is_connected = False
            self.hide_vad_indicator()
            
            if self.room:
                await self.room.disconnect()
                self.room = None
                
            self.local_audio_track = None
            self.audio_source = None
                
            self.update_status("Call Ended", "#ff4444")
            self.log_message("Disconnected from Friday", "System")
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            
    def toggle_connection(self):
        """Toggle connection to LiveKit room"""
        if self.is_connected:
            asyncio.create_task(self.disconnect_from_room())
            self.connect_button.config(text="Start Call", bg='#00d4ff')
        else:
            asyncio.create_task(self.connect_to_room())
            self.connect_button.config(text="End Call", bg='#ff4444')


async def main():
    """Main entry point"""
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    
    # Run tkinter event loop with asyncio
    while True:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            # Window closed
            if app.is_connected:
                await app.disconnect_from_room()
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application closed by user")
