import json
import keyboard
from typing import Dict
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pygame
pygame.init()
pygame.mixer.init()

current_folder = None
current_files = []
bindings: Dict[str, str] = {}

def play_file(file):
    
    if not current_folder:
        print("No folder loaded.")
        return
    path = os.path.join(current_folder, file)
    if not os.path.isfile(path):
        print(f"File does not exist: {path}")
    return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print(f"Playing {file}")
    except Exception as e:
        print(f"Failed to play {file}: {e}")


def save_bindings():
    try:
        with open("keybinds.json", "w", encoding="utf-8") as f:
            json.dump(bindings, f)
        print("Bindings saved.")
    except Exception as e:
        print(f"Error saving bindings: {e}")

def load_bindings():
    try:
        with open("keybinds.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for combo, file in data.items():
                bindings[combo] = file
                keyboard.add_hotkey(combo, lambda f=file: play_file(f), suppress=False)
        print("Bindings loaded from keybinds.json")
        update_bindings_view()
    except FileNotFoundError:
        print("No saved bindings found.")
    except Exception as e:
        print(f"Error loading bindings: {e}")


def clear_bindings():
    for combo in list(bindings):
        keyboard.remove_hotkey(combo)
    bindings.clear()
    update_bindings_view()
    save_bindings()
    print("All bindings cleared.")


# Load audio files from folder
def load_audio_files(folder=None):
    global current_folder, current_files
    if folder is None:
        folder = filedialog.askdirectory(title="Select Audio Folder")
    if not folder or not os.path.isdir(folder):
        return
    current_folder = folder
    current_files = [f for f in os.listdir(folder) if f.lower().endswith(('.wav', '.mp3', '.ogg',))]
    audio_list.delete(0, tk.END)
    for f in current_files:
        audio_list.insert(tk.END, f)
    print(f"Loaded {len(current_files)} files: {current_files}")
        
        
def clear_binding_for_selected():
    sel = audio_list.curselection()
    if not sel:
        messagebox.showinfo("No file", "Select a file first.")
        return
    file = audio_list.get(sel[0])
    to_remove = [c for c,f in bindings.items() if f==file]
    for combo in to_remove:
        keyboard.remove_hotkey(combo)
        del bindings[combo]
    update_bindings_view()
    save_bindings()
    print(f"Cleared binding(s) for '{file}'.")


# Bind key to selected audio
def start_binding():
    sel = audio_list.curselection()
    if not sel:
        messagebox.showinfo("No file", "Please select an audio file first.")
        return
    file = audio_list.get(sel[0])
    messagebox.showinfo("Bind", "Now press the key combo you want to bind,\nthen release all keys.")
    combo = keyboard.read_hotkey(suppress=False)
    keyboard.add_hotkey(combo, lambda f=file: play_file(f), suppress=False)
    bindings[combo] = file
    update_bindings_view()
    save_bindings()
    print(f"Bound {combo} → {file}")


def on_key_press(event):
    pressed_keys = keyboard._pressed_events.keys()
    combo = set()
    for key_code in pressed_keys:
        try:
            name = keyboard.keycode_to_name(key_code)
            if name:
                combo.add(name.lower())
        except:
            pass
    combo.add(event.keysym.lower())
    combo_str = '+'.join(sorted(combo))
    selected = audio_list.curselection()
    if selected:
        file = audio_list.get(selected[0])
        bindings[combo_str] = file
        print(f"Bound {combo_str} to '{file}'")
        update_bindings_view()
    window.unbind("<Key>")


# GUI
window = tk.Tk()
window.title("Micspam Software")

frame = tk.Frame(window)
frame.pack()

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

audio_list = tk.Listbox(frame, width=50, height=15, yscrollcommand=scrollbar.set)
audio_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=audio_list.yview)

bind_button = tk.Button(window, text="Bind Selected File to Key(s)", command=start_binding)
bind_button.pack(pady=5)

clear_selected_button = tk.Button(window, text="Clear Binding for Selected Audio", command=clear_binding_for_selected)
clear_selected_button.pack(pady=5)

clear_button = tk.Button(window, text="Clear Bindings", command=clear_bindings)
clear_button.pack(pady=5)

load_button = tk.Button(window, text="Load Audio Folder", command=load_audio_files)
load_button.pack(pady=5)

bindings_view = tk.Text(window, height=5, width=50)
bindings_view.pack()

def update_bindings_view():
    bindings_view.delete("1.0", tk.END)
    for combo, f in bindings.items():
        bindings_view.insert(tk.END, f"{combo} → {f}\n")


load_audio_files('./audio')
load_bindings()
window.mainloop()