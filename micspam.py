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
file_volumes: Dict[str, float] = {}

def play_file(file):
    if not current_folder:
        print("No folder loaded.")
        return
    path = os.path.join(current_folder, file)
    if not os.path.isfile(path):
        print(f"File does not exist: {path}")
        return
    try:
        sound = pygame.mixer.Sound(path)
        per_file_volume = file_volumes.get(file)
        master_volume = master_volume_slider.get() / 100.0
        final_volume = per_file_volume if per_file_volume is not None else master_volume
        sound.set_volume(final_volume)
        sound.play()
        print(f"Playing {file} at volume {final_volume}")
        print(f"Master volume: {master_volume}, Per-file override: {per_file_volume}")
    except Exception as e:
        print(f"Failed to play {file}: {e}")


def on_audio_select(event):
    sel = audio_list.curselection()
    if not sel:
        return
    file = audio_list.get(sel[0])
    volume = file_volumes.get(file, master_volume_slider.get() / 100.0)
    print(f"Selected {file} with volume {volume}")
    file_volume_slider.set(int(volume * 100))

def save_bindings():
    try:
        volumes_to_save = {f: v for f, v in file_volumes.items() if v != 1.0}
        data = {
            "bindings": bindings,
            "volumes": volumes_to_save,
            "master_volume": master_volume_slider.get() / 100.0
        }
        with open("keybinds.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
        print("Bindings and volumes saved.")
    except Exception as e:
        print(f"Error saving bindings: {e}")
        

def load_bindings():
    try:
        with open("keybinds.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            bindings.clear()
            bindings.update(data.get("bindings", {}))
            file_volumes.clear()
            volumes_raw = data.get("volumes", {})
            for f, v in volumes_raw.items():
                try:
                    file_volumes[f] = float(v)
                except:
                    pass
            master_vol = data.get("master_volume", 1.0)
            master_volume_slider.set(int(master_vol * 100))
            for combo, file in bindings.items():
                keyboard.add_hotkey(combo, lambda f=file: play_file(f), suppress=False)
            update_bindings_view()
        print("Bindings and volumes loaded from keybinds.json")
    except FileNotFoundError:
        print("No saved bindings found.")
    except Exception as e:
        print(f"Error loading bindings: {e}")
    print("Loaded file volumes:", file_volumes)
    print("Master volume:", master_volume_slider.get())


def clear_bindings():
    for combo in list(bindings):
        keyboard.remove_hotkey(combo)
    bindings.clear()
    update_bindings_view()
    save_bindings()
    print("All bindings cleared.")


    
def set_file_volume(val):
    volume = float(val) / 100.0
    sel = audio_list.curselection()
    if sel:
        file = audio_list.get(sel[0])
        if volume == 1.0:
            if file in file_volumes:
                del file_volumes[file]
        else:
            file_volumes[file] = volume
        print(f"Set volume for {file} to {int(volume * 100)}%")


# Load audio files from folder
def load_audio_files(folder=None):
    global current_folder, current_files
    if folder is None:
        folder = filedialog.askdirectory(title="Select Audio Folder")
    if not folder or not os.path.isdir(folder):
        return
    current_folder = folder
    current_files = [f for f in os.listdir(folder) if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
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

audio_list.bind("<<ListboxSelect>>", on_audio_select)

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

def clamp_volume(val_str):
    try:
        val = int(val_str)
        if val < 0:
            return "0"
        elif val > 100:
            return "100"
        else:
            return str(val)
    except:
        return ""

master_volume_frame = tk.Frame(window)
master_volume_frame.pack(pady=5, fill=tk.X)
master_volume_label = tk.Label(master_volume_frame, text="Master Volume")
master_volume_label.grid(row=0, column=0, sticky="w", padx=(0,10))
master_volume_var = tk.StringVar(value="100")

def on_master_entry_change(*args):
    val_str = master_volume_var.get()
    clamped = clamp_volume(val_str)
    if clamped != val_str:
        master_volume_var.set(clamped)
        return
    if clamped != "":
        master_volume_slider.set(int(clamped))
        save_bindings()

master_volume_var.trace_add('write', on_master_entry_change)

master_volume_slider = tk.Scale(master_volume_frame, from_=0, to=100, resolution=1,
                               orient=tk.HORIZONTAL, length=200)

def on_master_volume_change(val):
    val_int = int(float(val))
    master_volume_var.set(str(val_int))
    print(f"Master volume set to {val_int}%")
    save_bindings()

master_volume_slider.config(command=on_master_volume_change)
master_volume_slider.set(100)
master_volume_slider.grid(row=0, column=1, sticky="ew")
master_volume_entry = tk.Entry(master_volume_frame, width=5, textvariable=master_volume_var, justify='right')
master_volume_entry.grid(row=0, column=2, padx=(10,0))
master_volume_percent_label = tk.Label(master_volume_frame, text="%")
master_volume_percent_label.grid(row=0, column=3, sticky="w", padx=(5,0))

master_volume_frame.grid_columnconfigure(1, weight=1)


file_volume_frame = tk.Frame(window)
file_volume_frame.pack(pady=5, fill=tk.X)
file_volume_label = tk.Label(file_volume_frame, text="Selected File Volume")
file_volume_label.grid(row=0, column=0, sticky="w", padx=(0,10))
file_volume_var = tk.StringVar(value="100")

def on_file_entry_change(*args):
    val_str = file_volume_var.get()
    clamped = clamp_volume(val_str)
    if clamped != val_str:
        file_volume_var.set(clamped)
        return
    if clamped != "":
        file_volume_slider.set(int(clamped))
        save_bindings()

file_volume_var.trace_add('write', on_file_entry_change)
file_volume_slider = tk.Scale(file_volume_frame, from_=0, to=100, resolution=1,
                             orient=tk.HORIZONTAL, length=200)

def on_file_volume_change(val):
    val_int = int(float(val))
    file_volume_var.set(str(val_int))
    set_file_volume(val)
    print(f"File volume set to {val_int}%")
    save_bindings()

file_volume_slider.config(command=on_file_volume_change)
file_volume_slider.set(100)
file_volume_slider.grid(row=0, column=1, sticky="ew")
file_volume_entry = tk.Entry(file_volume_frame, width=5, textvariable=file_volume_var, justify='right')
file_volume_entry.grid(row=0, column=2, padx=(10,0))
file_volume_percent_label = tk.Label(file_volume_frame, text="%")
file_volume_percent_label.grid(row=0, column=3, sticky="w", padx=(5,0))
file_volume_frame.grid_columnconfigure(1, weight=1)




def update_bindings_view():
    bindings_view.delete("1.0", tk.END)
    for combo, f in bindings.items():
        bindings_view.insert(tk.END, f"{combo} → {f}\n")


load_audio_files('./audio')
load_bindings()
window.mainloop()