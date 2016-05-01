import pygame
import random

class Player(pygame.sprite.Sprite):
	def __init__(self, xpos, gs, is_cpu):
		pygame.sprite.Sprite.__init__(self)
		self.x_pos = xpos
		self.y_pos = 240
		self.height = 70
		self.width = 10
		self.score = 0
		self.gameState = gs
		self.movementAmount = 7.0
		self.cpu_movementAmount = 3.0
		self.is_cpu = is_cpu

	def moveUp(self):
		toMove = self.cpu_movementAmount if self.is_cpu else self.movementAmount
		if self.y_pos > self.height / 2.0:
			self.y_pos -= toMove
		
	def moveDown(self):
		toMove = self.cpu_movementAmount if self.is_cpu else self.movementAmount
		if self.y_pos < self.gameState.height - self.height / 2.0:
			self.y_pos += toMove

	def getTop(self):
		return y_pos + height / 2.0

	def getBottom(self):
		return y_pos - height / 2.0

	def to_dict(self):
		dict = {
			"score": self.score,
			"x_pos": self.x_pos,
			"y_pos": self.y_pos,
			"height": self.height,
			"width": self.width
		}
		return dict
		
	def tick(self, ball_y_pos):
		if self.is_cpu:
			if ball_y_pos > self.y_pos:
				self.moveDown()
			elif ball_y_pos < self.y_pos:
				self.moveUp()
			
	def getRect(self):
		return pygame.Rect(self.x_pos - self.width / 2, self.y_pos - self.height / 2, self.width, self.height)

class Ball(pygame.sprite.Sprite):
	def __init__(self,mult):
		self.ticks_since_created = 0
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

	def to_dict(self):
		dict = {
			"x_pos": self.x_pos,			
			"y_pos": self.y_pos,			
			"radius": self.radius
		}
		return dict
		
	def hitWall(self):
		self.y_speed *= -1.0
		
	def hitPlayer(self,playerY,playerHeight):
		self.x_speed *= -1.0
		self.y_speed = (self.y_pos - playerY) / playerHeight
		
	def tick(self):
		self.ticks_since_created += 1
		if self.ticks_since_created < 100:
			self.x_pos += self.x_speed * self.speed_multiplier * (self.ticks_since_created / 100.0)
			self.y_pos += self.y_speed * self.speed_multiplier * (self.ticks_since_created / 100.0)
		else:
			self.x_pos += self.x_speed * self.speed_multiplier
			self.y_pos += self.y_speed * self.speed_multiplier
		
	def getPos(self):
		return (int(self.x_pos),int(self.y_pos))

if __name__ == '__main__':
	p1 = Player(40)
	p2 = Player(600)
	ball = Ball(5.0)
