'''The classic "Snake" game remade in Python. Only supports the Windows shell.'''

import sys
import asyncio
import msvcrt
import random
import time

__author__ = 'kaga'

class Snake:

	def __init__(self, head, start_size):
		self.head = head
		self.segments = [head] * (start_size - 1)
		for i in range(len(self.segments)):
			self.segments[i] = head[0] + i + 1, head[1]	#the segments trail to the right of the head at the start
		self.facing = 'left'

	def __len__(self):
		return len(self.segments) + 1

	def set_direction(self, direction):
		if self.facing == direction or set((self.facing, direction)) in [{'left', 'right'}, {'up', 'down'}]:
			self.move(self.facing)
		else:
			self.move(direction)
			self.facing = direction

	def move(self, direction):
		self.old_segment = self.head
		self.head = self.head[0] + {'right':1, 'left':-1}.get(direction, 0), self.head[1] + {'up':-1, 'down':1}.get(direction, 0)
		for i, segment in enumerate(self.segments):
			self.segments[i] = self.old_segment
			self.old_segment = segment

	def add_segment(self):
		self.segments.append(self.old_segment)
			

class SnakeGame:
	dimensions = 40, 20
	start_size = 3
	empty_char = '-'
	wall_char = 'X'
	head_char = 'O'
	segment_char = 'o'
	food_char = '@'
	title = 'SNAKE\n\n(press "q" to quit)'

	def __init__(self):
		head = self.dimensions[0]//2, self.dimensions[1]//2
		self.snake = Snake(head, self.start_size)
		self.food = self.snake.head[0] - 6, self.snake.head[1]
		self.screen = self.new_screen()

	def __str__(self):
		return '{0}{1}\n\n{2}\n{3}\n{2}'.format('\n' * 100, self.title,
						self.wall_char * (self.dimensions[0] + 2),
						'\n'.join(self.wall_char + ''.join(row) + self.wall_char for row in self.screen))

	def spawn_food(self):
		while self.food in [self.snake.head] + self.snake.segments:
			self.food = random.randrange(self.dimensions[0]), random.randrange(self.dimensions[1])

	def update(self, keycode):
		if keycode in ('up', 'left', 'down', 'right'):
			self.snake.set_direction(keycode)
		else:
			self.snake.move(self.snake.facing)
		if self.snake.head == self.food:
			self.snake.add_segment()
			self.spawn_food()
		if self.snake.head in self.snake.segments:	#Game Over
			return True
		if not 0 <= self.snake.head[0] < self.dimensions[0] or not 0 <= self.snake.head[1] < self.dimensions[1]:	#Game Over
			return True
		self.new_screen()
		self.screen[self.snake.head[1]][self.snake.head[0]] = self.head_char
		for segment in self.snake.segments:
			self.screen[segment[1]][segment[0]] = self.segment_char
		self.screen[self.food[1]][self.food[0]] = self.food_char
		return False

	def new_screen(self):
		self.screen = [[self.empty_char]*(self.dimensions[0]) for _ in range(self.dimensions[1])]

	@property
	def score(self):
		return len(self.snake) - self.start_size


class IOController:
	initial_refresh_rate = .5
	poll_rate = .01
	keycodes = {
		b'q':'quit',
		b'w':'up',
		b'a':'left',
		b's':'down',
		b'd':'right',
		b'H':'up',	#H, K, P, and M are the up, left, down, and right arrow keys
		b'K':'left',
		b'P':'down',
		b'M':'right',
		
	}

	def __init__(self, game=None):
		self.loop = asyncio.get_event_loop()
		self.tasks = [self.loop.create_task(self.refresh()),
				self.loop.create_task(self.listen())]
		self.current_key = b''
		self.game = game if game else SnakeGame()
		self.game_over = False
		self.refresh_rate = self.initial_refresh_rate

	def run(self):
		self.loop.run_until_complete(asyncio.wait(self.tasks))

	def close(self):
		self.loop.close()
		print('\n\n{0}Thanks for playing!\n'.format(
		      'You died! Your score is {0} point(s).\n\n'.format(self.game.score) if self.game_over else ''))
		time.sleep(5)
		sys.exit()

	def break_check(self):
		return True if self.game_over or self.keycodes.get(self.current_key) == 'quit' else False

	@asyncio.coroutine
	async def refresh(self):
		while True:
			self.game_over = self.game.update(self.keycodes.get(self.current_key))
			if self.break_check():
				break	
			print(self.game, end='')
			if self.refresh_rate > .1:
				self.refresh_rate = self.initial_refresh_rate - (self.game.score / 30)
			await asyncio.sleep(self.refresh_rate)
	
	@asyncio.coroutine
	async def listen(self):
		while True:
			if self.break_check():
				break
			if msvcrt.kbhit():
				self.current_key = (msvcrt.getch() + msvcrt.getch()).replace(b'\xe0', b'').replace(b'\x00', b'')
	
			await asyncio.sleep(self.poll_rate)


if __name__ == '__main__':
	ioc = IOController()
	ioc.run()
	ioc.close()
