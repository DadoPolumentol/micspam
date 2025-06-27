import re
import os
import pygame
pygame.init()
screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Micspam software")
pygame.mixer.init()


#Bind button

button_rect = pygame.Rect(150, 80, 100, 40)  # x, y, width, height
button_color = (0, 128, 255)
button_text_color = (255, 255, 255)
font = pygame.font.Font(None, 36)






# Code for parsing audio files list 
files=os.listdir("./audio")
number_list=[]

for f in files:
    match = re.match(r"(\d+)", f)
    if match:
        number_list.append(int(match.group(1)))
print(number_list)



# Code for playing audio files

def play_audio_by_number(number):
    for file in files:
        if file.startswith(str(number)):
            pygame.mixer.music.load(f"./audio/{file}")
            pygame.mixer.music.play()
            print(f"Playing audio {number}...")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            print("Playback finished.")
            break

        



#Draw button
def draw_button():
    pygame.draw.rect(screen, button_color, button_rect)
    text = font.render("Bind", True, button_text_color)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

#Draw button status
def draw_status():
    if binding_mode:
        status_text = "Press a key to bind..."
    elif bound_key is not None:
        status_text = f"Bound key: {pygame.key.name(bound_key)}"
    else:
        status_text = "No key bound"
    text = font.render(status_text, True, (255, 255, 255))
    screen.blit(text, (20, 20))    




# Bind and play by bind logic
chosen_file=1
binding_mode = False
bound_key = None
while True:
    screen.fill((30, 30, 30))

    draw_button()
    draw_status()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if not binding_mode:
                if bound_key is not None and event.key == bound_key:
                    play_audio_by_number(chosen_file)
            else:
                bound_key = event.key
                print(f"Key bound: {pygame.key.name(bound_key)}. Press this key anytime to play audio 1.")
                binding_mode = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("Binding mode started! Press the key you want to bind to play audio 1.")
                binding_mode = True

        elif event.type == pygame.QUIT:
            pygame.quit()
            exit()


    pygame.display.flip()