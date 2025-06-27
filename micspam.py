import re
import os
import pygame
pygame.mixer.init()

high_power_mode=bool(None)
audio_num=None

files=os.listdir("./audio")
number_list=[]

for f in files:
    match = re.match(r"(\d+)", f)
    if match:
        number_list.append(int(match.group(1)))
print(number_list)
# Code for parsing audio files list ^
chosen_file=0
for file in files:
    if file.startswith(str(chosen_file)):
        pygame.mixer.music.load(f"./audio/{file}")
        pygame.mixer.music.play()
        print("Playing audio...")
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print("Playback finished.")
            
        break
        
# Code for playing audio files ^
print("Press ENTER to bind a key...")