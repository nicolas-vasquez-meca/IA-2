import os
import uuid
import pygame

class ImageCapture:

    def __init__(self, screen_spawn_position):
        self.screen_spawn_position = screen_spawn_position

        os.makedirs("images/up", exist_ok=True)
        os.makedirs("images/down", exist_ok=True)
        os.makedirs("images/right", exist_ok=True)
        os.makedirs("images/live", exist_ok=True)

        self.frame_skip = 0

        # región de captura por defecto (ajustar según resolución)
        # x, y, width, height — enfocada hacia adelante del dino
        self.capture_rect = pygame.Rect(40, 180, 640, 240)

    def save_surface(self, surface, key):
        filename = f"images/{key}/{uuid.uuid4()}.png"
        pygame.image.save(surface, filename)

    def capture(self, userInput, surface):
        self.frame_skip += 1
        if self.frame_skip % 5 != 0:
            return
        # recortar la región útil hacia adelante del dinosaurio
        try:
            sub = surface.subsurface(self.capture_rect).copy()
        except Exception:
            sub = surface

        if userInput[pygame.K_UP]:
            self.save_surface(sub, "up")
        elif userInput[pygame.K_DOWN]:
            self.save_surface(sub, "down")
        else:
            self.save_surface(sub, "right")

    def capture_live(self):
        surface = pygame.display.get_surface()
        try:
            sub = surface.subsurface(self.capture_rect).copy()
            pygame.image.save(sub, "./images/live/temp.png")
        except Exception:
            if surface is not None:
                pygame.image.save(surface, "./images/live/temp.png")
