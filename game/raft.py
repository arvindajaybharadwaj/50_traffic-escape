import pygame


class Raft:
    def __init__(self, x, y, width, height):
        self.rect=pygame.Rect(x,y,width,height)
        self.speed=2

    def update(self, screen_width):
        old_x=self.rect.x
        self.rect.x+=self.speed
        if self.rect.left<0:
            self.rect.left=0
            self.speed=abs(self.speed)
        elif self.rect.right>screen_width:
            self.rect.right=screen_width
            self.speed=-abs(self.speed)
        return self.rect.x-old_x

    def supports(self, player_rect):
        return self.rect.left<=player_rect.centerx<self.rect.right

    def draw(self, screen, night=False):
        pygame.draw.rect(screen,(75,50,35) if night else (120,75,35),self.rect,border_radius=16)
        pygame.draw.rect(screen,(110,75,50) if night else (175,115,55),self.rect.inflate(-12,-12),border_radius=12)
        for y in range(self.rect.top+20,self.rect.bottom,20):
            pygame.draw.line(screen,(70,45,30) if night else (100,60,30),(self.rect.left+10,y),(self.rect.right-10,y),3)
