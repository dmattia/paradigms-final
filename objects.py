import pygame
import random

class Player(pygame.sprite.Sprite):
	""" One of the two players in a game of pong
	"""
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
		""" Called to move a paddle up by @toMove pixels
		"""
		toMove = self.cpu_movementAmount if self.is_cpu else self.movementAmount
		if self.y_pos > self.height / 2.0:
			self.y_pos -= toMove
		
	def moveDown(self):
		""" Called to move a paddle down by @toMove pixels
		"""
		toMove = self.cpu_movementAmount if self.is_cpu else self.movementAmount
		if self.y_pos < self.gameState.height - self.height / 2.0:
			self.y_pos += toMove

	def getTop(self):
		""" Returns: the top y_value of this player's paddle
		"""
		return self.y_pos + self.height / 2.0

	def getBottom(self):
		""" Returns: the bottom y_value of this player's paddle
		"""
		return self.y_pos - self.height / 2.0

	def to_dict(self):
		""" Returns: A dictionary containing all information necessary to display a player
		"""
		dict = {
			"score": self.score,
			"x_pos": self.x_pos,
			"y_pos": self.y_pos,
			"height": self.height,
			"width": self.width
		}
		return dict
		
	def tick(self, ball_y_pos):
		""" Moves the player if it is a CPU
		"""
		if self.is_cpu:
			if ball_y_pos > self.y_pos:
				self.moveDown()
			elif ball_y_pos < self.y_pos:
				self.moveUp()
			
	def getRect(self):
		""" Returns: the rect to display this player in
		"""
		return pygame.Rect(self.x_pos - self.width / 2, self.y_pos - self.height / 2, self.width, self.height)

class Ball(pygame.sprite.Sprite):
	""" The ball of pong
	"""
	def __init__(self, mult):
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
		""" Returns: the rect to display this ball in
		"""
		dict = {
			"x_pos": self.x_pos,			
			"y_pos": self.y_pos,			
			"radius": self.radius
		}
		return dict
		
	def hitWall(self):
		""" Changes a ball's movement when it hits a wall
		"""
		self.y_speed *= -1.0
		
	def hitPlayer(self,playerY,playerHeight):
		""" Changes a ball's movement when it hits a player
		"""
		self.x_speed *= -1.0
		self.y_speed = (self.y_pos - playerY) / playerHeight
		
	def tick(self):
		""" Accelerates the ball over the first 100 frames
				to make the initial hit after a point a bit easier
		"""
		self.ticks_since_created += 1
		if self.ticks_since_created < 100:
			self.x_pos += self.x_speed * self.speed_multiplier * (self.ticks_since_created / 100.0)
			self.y_pos += self.y_speed * self.speed_multiplier * (self.ticks_since_created / 100.0)
		else:
			self.x_pos += self.x_speed * self.speed_multiplier
			self.y_pos += self.y_speed * self.speed_multiplier

		# Apply gravity
		height_in_pixels = 480 - self.y_pos
		pixels_per_meter = 30
		height_in_meters = height_in_pixels / pixels_per_meter
		self.y_speed += (9.8 * height_in_meters) / 7000
		
	def getPos(self):
		""" Returns: A tuple of the x and y center positions of the ball
		"""
		return (int(self.x_pos),int(self.y_pos))
