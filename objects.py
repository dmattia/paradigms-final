import pygame
import random

class Player(pygame.sprite.Sprite):
	def __init__(self, xpos, gs):
		pygame.sprite.Sprite.__init__(self)
		self.x_pos = xpos
		self.y_pos = 240
		self.height = 70
		self.width = 10
		self.score = 0
		self.gameState = gs

	def moveUp(self):
		if self.y_pos > self.height / 2.0:
			self.y_pos -= 4.0
		
	def moveDown(self):
		if self.y_pos < self.gameState.height - self.height / 2.0:
			self.y_pos += 4.0
		
	def tick(self):
		pass
			
	def getRect(self):
		return pygame.Rect(self.x_pos - self.width / 2, self.y_pos - self.height / 2, self.width, self.height)
		
class Ball(pygame.sprite.Sprite):
	def __init__(self,mult):
		self.x_pos = 320.0
		self.y_pos = 240.0
		self.y_speed = random.random() * 2 - 1
		xRand = random.randrange(-1.0,1.0)
		if xRand < 0:
			self.x_speed = -1.0
		else:
			self.x_speed = 1.0
		self.speed_multiplier = mult
		self.radius = 5
		
	def hitWall(self):
		self.y_speed *= -1.0
		
	def hitPlayer(self,playerY,playerHeight):
		self.x_speed *= -1.0
		self.y_speed = (self.y_pos - playerY) / playerHeight
		
	def tick(self):
		self.x_pos += self.x_speed * self.speed_multiplier
		self.y_pos += self.y_speed * self.speed_multiplier
		
	def getPos(self):
		return (int(self.x_pos),int(self.y_pos))

if __name__ == '__main__':
	p1 = Player(40)
	p2 = Player(600)
	ball = Ball(5.0)
