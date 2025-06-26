import os
import pygame
pygame.mixer.init()

high_power_mode=bool(None)
audio_num=None

files=os.listdir("./audio")
number_list=[None]
for f in files:
    x=0
    for a in f:
        is_digit=0
        print(f[x])
        is_digit=f[x].isdigit()
        if is_digit != True:
            break
        number_list.append(x)
        x+=1

for list in number_list:
    print(list)