import keyboard
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import re
import os
import pygame
pygame.init()
pygame.mixer.init()

current_folder = None
current_files = []
bindings = {}

def clear_bindings():
    bindings.clear()
    update_bindings_view()
    print("All bindings cleared.")


# Load audio files from folder
def load_audio_files():
    global current_folder, current_files
    folder = filedialog.askdirectory(title="Select Audio Folder")
    if not folder:
        return
    current_folder = folder
    current_files = [f for f in os.listdir(folder) if f.lower().endswith(('.wav', '.mp3', '.ogg',))]
    audio_list.delete(0, tk.END)
    for f in current_files:
        audio_list.insert(tk.END, f)
        
print(f"Loaded {len(current_files)} files: {current_files}")
        

def clear_binding_for_selected():
    selected = audio_list.curselection()
    if not selected:
        messagebox.showinfo("No file", "Please select an audio file to clear its binding.")
        return
    file_to_clear = audio_list.get(selected[0])
    keys_to_remove = [k for k, f in bindings.items() if f == file_to_clear]
    for k in keys_to_remove:
        del bindings[k]
    update_bindings_view()
    print(f"Cleared binding(s) for '{file_to_clear}'.")


# Bind key to selected audio
def start_binding():
    selected = audio_list.curselection()
    if not selected:
        messagebox.showinfo("No file", "Please select an audio file.")
        return
    key_label.config(text="Press a key to bind...")
    window.bind("<Key>", on_key_press)

def on_key_press(event):
    def normalize_key(key):
        key = key.lower()
        if key in ['control_l', 'control_r', 'ctrl']:
            return 'ctrl'
        if key in ['shift_l', 'shift_r', 'shift']:
            return 'shift'
        if key in ['alt_l', 'alt_r', 'alt']:
            return 'alt'
        return key
    selected = audio_list.curselection()
    if selected:
        file = audio_list.get(selected[0])
        key = normalize_key(event.keysym)
        bindings[key] = file
        print(f"Bound '{key}' to '{file}'")
        update_bindings_view()
    key_label.config(text="Key bind mode (idle)")
    window.unbind("<Key>")
    
    


def start_key_listener():
    def on_key(event):
        def normalize_key(key):
            key = key.lower()
            if key in ['left ctrl', 'right ctrl', 'ctrl']:
                return 'ctrl'
            if key in ['left shift', 'right shift', 'shift']:
                return 'shift'
            if key in ['left alt', 'right alt', 'alt']:
                return 'alt'
            return key
        key = normalize_key(event.name)
        if key in bindings and current_folder:
            file = bindings[key]
            path = os.path.join(current_folder, file)
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                print(f"Playing {file}")
            except Exception as e:
                print(f"Failed to play {file}: {e}")
    keyboard.on_press(on_key)
    
    

# GUI
window = tk.Tk()
window.title("Keybind Audio Player")

frame = tk.Frame(window)
frame.pack()

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

audio_list = tk.Listbox(frame, width=50, height=15, yscrollcommand=scrollbar.set)
audio_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=audio_list.yview)

load_button = tk.Button(window, text="Load Audio Folder", command=load_audio_files)
load_button.pack(pady=5)

bind_button = tk.Button(window, text="Bind Selected File to Key", command=start_binding)
bind_button.pack(pady=5)

clear_selected_button = tk.Button(window, text="Clear Binding for Selected Audio", command=clear_binding_for_selected)
clear_selected_button.pack(pady=5)

clear_button = tk.Button(window, text="Clear Bindings", command=clear_bindings)
clear_button.pack(pady=5)

key_label = tk.Label(window, text="Key bind mode (idle)")
key_label.pack(pady=5)

bindings_view = tk.Text(window, height=5, width=50)
bindings_view.pack()

def update_bindings_view():
    bindings_view.delete(1.0, tk.END)
    for k, f in bindings.items():
        bindings_view.insert(tk.END, f"{k} → {f}\n")


start_key_listener()
window.mainloop()