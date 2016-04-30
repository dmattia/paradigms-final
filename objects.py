import pygame
import random

class Player(pygame.sprite.Sprite):
	def __init__(self, xpos):
		pygame.sprite.Sprite.__init__(self)
		self.x_pos = xpos
		self.y_pos = 240
		self.height = 60

	def moveUp(self):
		self.y_pos += 2
		
	def moveDown(self):
		self.y_pos -= 2
		
	def tick(self, dir):
		if dir == 'U':
			moveUp()
		elif dir == 'D':
			moveDown()
		
		
class Ball(pygame.sprite.Sprite):
	def __init__(self,mult):
		self.x_pos = 320.0
		self.y_pos = 240.0
		self.y_speed = random.randrange(-1,1)
		xRand = random.randrange(-1,1)
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
		return (self.x_pos,self.y_pos)

if __name__ == '__main__':
	p1 = Player(40)
	p2 = Player(600)
	ball = Ball(5.0)