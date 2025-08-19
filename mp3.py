# Author:Dhruv 
# prerequistes:
# 1. python 3.10
# 2. tkinter
# 3. pygame
# 4. mutagen
# 5. os
# 6. threading
# 7. time
# 8. math
# 9. os
# 10. threading
# 11. time
# 12. math

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
import threading
import time
from mutagen.mp3 import MP3
import math

class MP3Player:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Player - Simple but Solid")
        self.root.geometry("400x500")
        self.root.configure(bg='#2c3e50')  # Dark theme, looks pro ya
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Player state variables
        self.current_song = None
        self.song_list = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        
        # Create the UI components
        self.create_widgets()
        
        # Start the progress update thread
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()
        
        print("MP3 Player initialized successfully! Ready to rock some tunes 🎵")
    
    def create_widgets(self):
        """Create all the UI elements - keeping it clean and functional"""
        
        # Main title - simple but effective
        title_label = tk.Label(
            self.root, 
            text="MP3 Player", 
            font=("Arial", 20, "bold"), 
            bg='#2c3e50', 
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Song info display
        self.song_info = tk.Label(
            self.root, 
            text="No song loaded", 
            font=("Arial", 12), 
            bg='#2c3e50', 
            fg='#ecf0f1',
            wraplength=350
        )
        self.song_info.pack(pady=5)
        
        # Progress bar frame
        progress_frame = tk.Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=10, padx=20, fill='x')
        
        # Time labels
        self.current_time = tk.Label(progress_frame, text="0:00", bg='#2c3e50', fg='white')
        self.current_time.pack(side='left')
        
        self.total_time = tk.Label(progress_frame, text="0:00", bg='#2c3e50', fg='white')
        self.total_time.pack(side='right')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient='horizontal', 
            length=300, 
            mode='determinate'
        )
        self.progress_bar.pack(pady=5, fill='x')
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(pady=20)
        
        # Previous button
        self.prev_btn = tk.Button(
            control_frame, 
            text="⏮", 
            font=("Arial", 16), 
            command=self.previous_song,
            bg='#34495e', 
            fg='white',
            width=3
        )
        self.prev_btn.pack(side='left', padx=5)
        
        # Play/Pause button
        self.play_btn = tk.Button(
            control_frame, 
            text="▶", 
            font=("Arial", 16), 
            command=self.play_pause,
            bg='#27ae60', 
            fg='white',
            width=3
        )
        self.play_btn.pack(side='left', padx=5)
        
        # Next button
        self.next_btn = tk.Button(
            control_frame, 
            text="⏭", 
            font=("Arial", 16), 
            command=self.next_song,
            bg='#34495e', 
            fg='white',
            width=3
        )
        self.next_btn.pack(side='left', padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            control_frame, 
            text="⏹", 
            font=("Arial", 16), 
            command=self.stop_song,
            bg='#e74c3c', 
            fg='white',
            width=3
        )
        self.stop_btn.pack(side='left', padx=5)
        
        # Volume control frame
        volume_frame = tk.Frame(self.root, bg='#2c3e50')
        volume_frame.pack(pady=10)
        
        volume_label = tk.Label(volume_frame, text="Volume:", bg='#2c3e50', fg='white')
        volume_label.pack(side='left')
        
        self.volume_scale = tk.Scale(
            volume_frame, 
            from_=0, 
            to=100, 
            orient='horizontal', 
            command=self.change_volume,
            bg='#2c3e50', 
            fg='white',
            highlightbackground='#2c3e50'
        )
        self.volume_scale.set(70)  # Default volume
        self.volume_scale.pack(side='left', padx=10)
        
        # File operations frame
        file_frame = tk.Frame(self.root, bg='#2c3e50')
        file_frame.pack(pady=20)
        
        # Load file button - handles both single files and folders
        self.load_btn = tk.Button(
            file_frame, 
            text="Load File", 
            command=self.load_file,
            bg='#3498db', 
            fg='white',
            font=("Arial", 12)
        )
        self.load_btn.pack(pady=5)
        
        # Playlist frame
        playlist_frame = tk.Frame(self.root, bg='#2c3e50')
        playlist_frame.pack(pady=10, fill='both', expand=True)
        
        playlist_label = tk.Label(playlist_frame, text="Playlist:", bg='#2c3e50', fg='white', font=("Arial", 12, "bold"))
        playlist_label.pack()
        
        # Playlist listbox with scrollbar
        listbox_frame = tk.Frame(playlist_frame, bg='#2c3e50')
        listbox_frame.pack(fill='both', expand=True, padx=20)
        
        self.playlist_box = tk.Listbox(
            listbox_frame, 
            bg='#34495e', 
            fg='white', 
            selectbackground='#3498db',
            font=("Arial", 10)
        )
        self.playlist_box.pack(side='left', fill='both', expand=True)
        
        playlist_scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=self.playlist_box.yview)
        playlist_scrollbar.pack(side='right', fill='y')
        self.playlist_box.config(yscrollcommand=playlist_scrollbar.set)
        
        # Bind double-click to playlist items
        self.playlist_box.bind('<Double-Button-1>', self.playlist_double_click)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root, 
            text="Ready to play some music!", 
            bg='#34495e', 
            fg='white',
            font=("Arial", 10)
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def load_file(self):
        """Load MP3 files - handles both single files and folders intelligently"""
        # Ask user what they want to load
        choice = messagebox.askyesno(
            "Load Option", 
            "Do you want to load a folder?\n\nYes = Load entire folder\nNo = Load single file"
        )
        
        if choice:
            # Load folder
            folder_path = filedialog.askdirectory(title="Choose folder with MP3 files")
            
            if folder_path:
                mp3_files = []
                for file in os.listdir(folder_path):
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(os.path.join(folder_path, file))
                
                if mp3_files:
                    self.song_list = sorted(mp3_files)  # Sort alphabetically
                    self.current_index = 0
                    self.current_song = self.song_list[0]
                    self.update_playlist_display()
                    self.load_song_info()
                    self.status_bar.config(text=f"Loaded {len(mp3_files)} songs from folder")
                    print(f"Loaded {len(mp3_files)} songs from folder")
                else:
                    messagebox.showinfo("No MP3 files", "No MP3 files found in the selected folder!")
        else:
            # Load single file
            file_path = filedialog.askopenfilename(
                title="Choose an MP3 file",
                filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
            )
            
            if file_path:
                self.song_list = [file_path]
                self.current_index = 0
                self.current_song = file_path
                self.update_playlist_display()
                self.load_song_info()
                self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
                print(f"Song loaded: {os.path.basename(file_path)}")
    
    def update_playlist_display(self):
        """Update the playlist display with current songs"""
        self.playlist_box.delete(0, tk.END)
        for i, song in enumerate(self.song_list):
            song_name = os.path.basename(song)
            if i == self.current_index:
                song_name = f"▶ {song_name}"  # Show current song with indicator
            self.playlist_box.insert(tk.END, song_name)
    
    def load_song_info(self):
        """Load and display song information"""
        if self.current_song and os.path.exists(self.current_song):
            try:
                # Get song duration using mutagen
                audio = MP3(self.current_song)
                duration = audio.info.length
                self.song_duration = duration
                
                # Update song info display
                song_name = os.path.basename(self.current_song)
                self.song_info.config(text=song_name)
                self.total_time.config(text=self.format_time(duration))
                
                # Reset progress
                self.progress_bar['value'] = 0
                self.current_time.config(text="0:00")
                
                print(f"Song info loaded: {song_name} - Duration: {self.format_time(duration)}")
                
            except Exception as e:
                print(f"Error loading song info: {e}")
                self.song_info.config(text="Error loading song info")
    
    def play_pause(self):
        """Toggle between play and pause - the core functionality"""
        if not self.current_song:
            messagebox.showinfo("No Song", "Please load a song first!")
            return
        
        if not self.is_playing:
            # Start playing
            try:
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volume)
                
                self.is_playing = True
                self.is_paused = False
                self.play_btn.config(text="⏸")
                self.status_bar.config(text="Playing...")
                print("Started playing music!")
                
            except Exception as e:
                print(f"Error playing song: {e}")
                messagebox.showerror("Playback Error", f"Could not play the song: {e}")
                
        else:
            # Pause or resume
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_btn.config(text="⏸")
                self.status_bar.config(text="Playing...")
                print("Resumed playback")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.config(text="▶")
                self.status_bar.config(text="Paused")
                print("Paused playback")
    
    def stop_song(self):
        """Stop the current song and reset everything"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.play_btn.config(text="▶")
            self.progress_bar['value'] = 0
            self.current_time.config(text="0:00")
            self.status_bar.config(text="Stopped")
            print("Stopped playback")
    
    def next_song(self):
        """Go to next song in playlist"""
        if len(self.song_list) > 1:
            self.current_index = (self.current_index + 1) % len(self.song_list)
            self.current_song = self.song_list[self.current_index]
            self.load_song_info()
            self.update_playlist_display()
            
            if self.is_playing:
                self.stop_song()
                self.play_pause()  # Auto-play next song
            
            self.status_bar.config(text=f"Next song: {os.path.basename(self.current_song)}")
            print(f"Switched to next song: {os.path.basename(self.current_song)}")
    
    def previous_song(self):
        """Go to previous song in playlist"""
        if len(self.song_list) > 1:
            self.current_index = (self.current_index - 1) % len(self.song_list)
            self.current_song = self.song_list[self.current_index]
            self.load_song_info()
            self.update_playlist_display()
            
            if self.is_playing:
                self.stop_song()
                self.play_pause()  # Auto-play previous song
            
            self.status_bar.config(text=f"Previous song: {os.path.basename(self.current_song)}")
            print(f"Switched to previous song: {os.path.basename(self.current_song)}")
    
    def change_volume(self, value):
        """Change volume - simple volume control"""
        self.volume = float(value) / 100.0
        if self.is_playing:
            pygame.mixer.music.set_volume(self.volume)
        print(f"Volume changed to: {value}%")
    
    def playlist_double_click(self, event):
        """Handle double-click on playlist items"""
        selection = self.playlist_box.curselection()
        if selection:
            self.current_index = selection[0]
            self.current_song = self.song_list[self.current_index]
            self.load_song_info()
            self.update_playlist_display()
            
            if self.is_playing:
                self.stop_song()
                self.play_pause()  # Auto-play selected song
            
            self.status_bar.config(text=f"Playing: {os.path.basename(self.current_song)}")
            print(f"Double-clicked song: {os.path.basename(self.current_song)}")
    
    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def update_progress(self):
        """Update progress bar and time display - runs in separate thread"""
        while True:
            if self.is_playing and not self.is_paused and self.current_song:
                try:
                    # Get current position
                    current_pos = pygame.mixer.music.get_pos() / 1000.0
                    
                    if current_pos > 0 and hasattr(self, 'song_duration'):
                        # Update progress bar
                        progress = (current_pos / self.song_duration) * 100
                        self.progress_bar['value'] = progress
                        
                        # Update current time
                        self.current_time.config(text=self.format_time(current_pos))
                        
                        # Check if song ended
                        if current_pos >= self.song_duration:
                            self.next_song()
                    
                except Exception as e:
                    # Sometimes pygame throws errors, just ignore them
                    pass
            
            time.sleep(0.1)  # Update every 100ms
    
    def on_closing(self):
        """Clean up when closing the application"""
        try:
            pygame.mixer.quit()
            pygame.quit()
        except:
            pass
        self.root.destroy()

def main():
    """Main function to start the MP3 player"""
    print("Starting MP3 Player...")
    
    root = tk.Tk()
    app = MP3Player(root)
    
    # Set up closing protocol
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the main loop
    print("MP3 Player is ready! Load some songs and enjoy the music 🎶")
    root.mainloop()

if __name__ == "__main__":
    main()
