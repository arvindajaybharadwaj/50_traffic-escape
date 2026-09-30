import pygame
import random
from game.player import Player,LANE_W
from game.traffic import Car,make_car
from game.raft import Raft
from game.high_scores import HighScores

LANES=8
WIDTH=LANES*LANE_W
HEIGHT=600
FPS=60
BG=(60,60,60)
NIGHT_BG=(18,22,38)
WATER_TOP=250
WATER_BOTTOM=330
DAY_LENGTH_MS=30000

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Traffic Escape")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("monospace",24,bold=True)
        self.hud_font=pygame.font.SysFont("monospace",18,bold=True)
        self.big_font=pygame.font.SysFont("monospace",44,bold=True)
        self.high_scores=HighScores()
        self.reset()

    def reset(self):
        self.player=Player(WIDTH//2+LANE_W//2,HEIGHT-80)
        self.raft=Raft(WIDTH//2-110,WATER_TOP,220,WATER_BOTTOM-WATER_TOP)
        self.cars=[]
        self.timer=0
        self.spawn_interval=50
        self.speed=3
        self.score=0
        self.lives=3
        self.invulnerable_frames=0
        self.game_over=False
        self.won=False
        self.score_recorded=False
        self.cycle_started_at=pygame.time.get_ticks()
        self.is_night=False

    def _record_score(self):
        if self.score_recorded: return
        self.score_recorded=True
        final_score=self.score//10
        if final_score>0:
            self.high_scores.add(final_score)

    def _in_water(self):
        return WATER_TOP <= self.player.rect.centery < WATER_BOTTOM

    def _lose_life(self):
        self.lives-=1
        if self.lives==0:
            self.game_over=True
            self.invulnerable_frames=0
            self._record_score()
        else:
            self.player=Player(WIDTH//2+LANE_W//2,HEIGHT-80)
            self.invulnerable_frames=FPS

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self._record_score()
                return False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_r:
                self._record_score()
                self.reset()
        return True

    def update(self):
        elapsed=pygame.time.get_ticks()-self.cycle_started_at
        self.is_night=(elapsed//DAY_LENGTH_MS)%2==1
        if self.game_over or self.won: return
        keys=pygame.key.get_pressed()
        self.player.move(keys,0,WIDTH,HEIGHT)
        on_raft=self._in_water() and self.raft.supports(self.player.rect)
        raft_dx=self.raft.update(WIDTH)
        if on_raft:
            self.player.rect.x=max(0,min(WIDTH-self.player.rect.width,self.player.rect.x+raft_dx))
        if self._in_water() and not self.raft.supports(self.player.rect):
            self._lose_life()
            return
        if self.invulnerable_frames>0:
            self.invulnerable_frames-=1
        self.timer+=1
        if self.timer>=self.spawn_interval:
            lane=random.randint(0,LANES-1)
            self.cars.append(make_car(lane,HEIGHT,self.speed))
            self.timer=0
            self.spawn_interval=max(22,self.spawn_interval-0.2)
        for c in self.cars:
            c.update()
            if not self._in_water() and self.invulnerable_frames==0 and c.rect.colliderect(self.player.rect):
                self._lose_life()
                return
        self.cars=[c for c in self.cars if not c.off_screen(HEIGHT)]
        self.score+=1
        if self.score%300==0: self.speed=min(10,self.speed+0.5)
        if self.player.rect.top<=10:
            self.won=True
            self._record_score()

    def draw(self):
        self.screen.fill(NIGHT_BG if self.is_night else BG)
        line_color=(52,58,77) if self.is_night else (100,100,100)
        marking_color=(110,105,65) if self.is_night else (200,200,100)
        sidewalk_color=(72,70,78) if self.is_night else (150,130,110)
        water_color=(15,45,80) if self.is_night else (40,105,155)
        wave_color=(30,75,110) if self.is_night else (75,140,185)
        # road markings
        for i in range(LANES+1):
            pygame.draw.line(self.screen,line_color,(i*LANE_W,0),(i*LANE_W,HEIGHT),2)
        for y in range(0,HEIGHT,60):
            for i in range(LANES):
                pygame.draw.rect(self.screen,marking_color,pygame.Rect(i*LANE_W+LANE_W//2-3,y,6,30))
        # sidewalks
        pygame.draw.rect(self.screen,sidewalk_color,pygame.Rect(0,HEIGHT-50,WIDTH,50))
        pygame.draw.rect(self.screen,sidewalk_color,pygame.Rect(0,0,WIDTH,30))
        for c in self.cars: c.draw(self.screen,self.is_night)
        pygame.draw.rect(self.screen,water_color,pygame.Rect(0,WATER_TOP,WIDTH,WATER_BOTTOM-WATER_TOP))
        for y in range(WATER_TOP+12,WATER_BOTTOM,24):
            pygame.draw.line(self.screen,wave_color,(0,y),(WIDTH,y),2)
        self.raft.draw(self.screen,self.is_night)
        if self.invulnerable_frames==0 or self.invulnerable_frames//6%2==0:
            self.player.draw(self.screen)
        hud=pygame.Rect(0,0,WIDTH,30)
        pygame.draw.rect(self.screen,(20,20,20),hud)
        best=self.high_scores.scores[0] if self.high_scores.scores else 0
        phase="NIGHT" if self.is_night else "DAY"
        s=self.hud_font.render(f"Score: {self.score//10}  Lives: {self.lives}  Best: {best}  {phase}  R=Restart",True,(220,220,220))
        self.screen.blit(s,(6,4))
        if self.game_over:
            self._msg("GAME OVER!",(220,60,60))
        if self.won:
            self._msg("YOU MADE IT!",(80,220,80))
        pygame.display.flip()

    def _msg(self,text,color):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,150))
        self.screen.blit(ov,(0,0))
        pygame.draw.rect(self.screen,(14,18,28),pygame.Rect(WIDTH//2-170,HEIGHT//2-65,340,330),border_radius=14)
        m=self.big_font.render(text,True,color)
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(m,(WIDTH//2-m.get_width()//2,HEIGHT//2-40))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,HEIGHT//2+20))
        heading=self.font.render("TOP 5 SCORES",True,(230,210,130))
        self.screen.blit(heading,(WIDTH//2-heading.get_width()//2,HEIGHT//2+58))
        for rank in range(5):
            score=self.high_scores.scores[rank] if rank<len(self.high_scores.scores) else "-"
            row=self.font.render(f"{rank+1}.  {score}",True,(230,230,230))
            self.screen.blit(row,(WIDTH//2-row.get_width()//2,HEIGHT//2+90+rank*30))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            if not running: break
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
