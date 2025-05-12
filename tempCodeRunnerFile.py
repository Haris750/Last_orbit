import sys
import pygame
from settings import Settings
from ship import Ship
from bullets import Bullet
from alienfactory import Alien
from time import sleep
from game_stats import Gamestats
from button import Button
from scoreboard import Scoreboard

class Alien_Invasion:

    def __init__(self):
        pygame.init()
        self.settings=Settings()
        self.screen=pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        self.bullets=pygame.sprite.Group()
        self.shooting=False
        self.aliens=pygame.sprite.Group()
        self.stats=Gamestats(self)
        self.sb=Scoreboard(self)
        self.ship=Ship(self)
        self._create_fleet()
        self.game_active=False
        
        pygame.display.set_caption("Alien Invasion")
        self.clock=pygame.time.Clock()
        
        self.last_shot_time=0
        self.play_button=Button(self,"play")
        


    def run_game(self):

        while True:

            
            self._update_screen() 
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._upadate_bullets()
                self._update_aliens()           
             
            self.clock.tick(60)
    
    def _check_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type==pygame.KEYDOWN:
                    self._check_keydown_events(event)
                    
                elif event.type==pygame.KEYUP:
                    self._check_keyup_events(event)

                elif event.type==pygame.MOUSEBUTTONDOWN:
                    mouse_pos=pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)


    def _check_play_button(self,mouse_pos):
        button_clicked=self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings._initialize_dynamic_settings()
            self.stats.reset_stats()
            self.game_active=True
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)
                    
                
    def _check_keydown_events(self,event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key==pygame.K_q:
            sys.exit()
        elif event.key==pygame.K_SPACE:
            self._fire_bullet()
            self.shooting=True

    
    def _upadate_bullets(self):
        current_time = pygame.time.get_ticks()
        if self.shooting and current_time - self.last_shot_time > 150:  # 150ms delay
            self._fire_bullet()
            self.last_shot_time = current_time

    
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_aliens_collisions()   

        

    def _check_bullet_aliens_collisions(self):
        collisions=pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
        

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()  

        self._check_alien_bottom()

    
    def _fire_bullet(self):
        if len(self.bullets)<self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)       
    
    def _check_keyup_events(self,event):  
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        if event.key==pygame.K_LEFT:
            self.ship.moving_left=False
        if event.key==pygame.K_SPACE:
            self.shooting=False

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

    # Calculate number of aliens in a row
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

    # Calculate number of rows that fit
        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                x_position = alien_width + 2 * alien_width * alien_number
                y_position = alien_height + 2 * alien_height * row_number
                self._create_alien(x_position, y_position)


    def _create_alien(self, x_position,y_position):
        new_alien=Alien(self)
        new_alien.rect.x=x_position
        new_alien.rect.y = y_position
        new_alien.x = float(new_alien.rect.x)
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites(): 
            alien.rect.y += self.settings.fleet_dropspeed
        self.settings.fleet_direction*=-1

    
    def  _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _ship_hit(self):
        if self.stats.ship_left>0:
            self.stats.ship_left-=1
            self.bullets.empty()
            self.aliens.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(.5)  
        else:
            self.game_active=False 
            pygame.mouse.set_visible(True)

    def _check_alien_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom>=self.settings.screen_height:
                self._ship_hit()
                break      

if __name__ == '__main__':
    ai=Alien_Invasion()
    ai.run_game()                