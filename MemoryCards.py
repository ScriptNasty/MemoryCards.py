# My 5x5 memory card game variant based on rcruz63's "Cards.py" Pythonista script
# Source: https://gist.github.com/rcruz63/5195131

from scene import *
from random import shuffle
from functools import partial
from sound import play_effect


class Game(Scene):
	def setup(self):
		self.root_layer = Layer(self.bounds)
		front_images = ('Angry Astonished Smiling_6 Cold_Sweat_2 Confounded Smirking'
						' Crying_2 Disappointed Dizzy Fear_2 Flushed Tears_Of_Joy')
		self.front_images = ['emj:' + image for image in front_images.split() * 2]
		self.imp_image = 'emj:Imp'
		self.front_images.append(self.imp_image)
		self.deal()
	
	def draw(self):
		background(0.0, 0.2, 0.3)
		self.root_layer.update(self.dt)
		self.root_layer.draw()

	def deal(self):
		shuffle(self.front_images)
		self.root_layer.sublayers = []
		self.cards = []
		self.selected = []
		card_size = 106 if self.size.w > 700 else 63
		gameboard_width = (card_size + 5) * 5
		offset = Point(
			(self.size.w - gameboard_width) / 2,
			(self.size.h - gameboard_width) / 2)
		for i, front_image in enumerate(self.front_images):
			x, y = i%5, i/5
			card = Layer(Rect(
				offset.x + x * (card_size + 10),
				offset.y + y * (card_size + 10),
				card_size, card_size))
			card.background = Color(0.95, 0.95, 0.95, 1)
			card.stroke = Color(1, 1, 1, 1)
			card.stroke_weight = 5.0
			card.back_image = 'card:BackBlue3'
			card.front_image = front_image
			card.image = card.back_image
			self.add_layer(card)
			self.cards.append(card)
		self.touch_disabled = False

	def touch_began(self, touch):
		if self.touch_disabled or len(self.cards) == 0:
			return
		if len(self.selected) == 1 and self.selected[0].front_image == self.imp_image:
			self.discard_selection()
			return
		elif len(self.selected) == 2:
			self.discard_selection()
			return
		for card in self.cards:
			if card in self.selected or len(self.selected) == 2:
				continue
			if touch.location in card.frame:
				def reveal_card():
					card.image = card.front_image
					card.animate('scale_x', 1.0, 0.15, completion=self.check_selection)
				self.selected.append(card)
				self.touch_disabled = True
				card.animate('scale_x', 0.0, 0.15, completion=reveal_card)
				card.animate('scale_y', 0.9, 0.15, autoreverse=True)
				play_effect('ui:click1')
				break

	def discard_selection(self):
		play_effect('ui:click2')
		for card in self.selected:
			def conceal(card):
				card.image = card.back_image
				card.animate('scale_x', 1.0, 0.15)
			card.animate('scale_x', 0.0, 0.15, completion=partial(conceal, card))
			card.animate('scale_y', 0.9, 0.15, autoreverse=True)
			card.animate('background', Color(0.8, 0.8, 0.8, 1), duration=0.1)
		self.selected = []

	def check_selection(self):
		self.touch_disabled = False
		if len(self.selected) == 1 and self.selected[0].front_image == self.imp_image:
			play_effect('game:Bleep', volume=0.1)
			self.selected[0].animate('background', Color(0.5, 0.5, 1.0, 1), duration=0.05)
		if len(self.selected) == 2 and self.selected[1].front_image == self.imp_image:
			play_effect('game:Bleep', volume=0.1)
			for c in self.selected:
				c.background = Color(0.5, 0.5, 1.0, 1)
		elif len(self.selected) == 2:
			card_img1 = self.selected[0].front_image
			card_img2 = self.selected[1].front_image
			if card_img1 == card_img2:
				play_effect('arcade:Coin_3', volume=0.4)
				for c in self.selected:
					c.animate('background', Color(0.5, 1.0, 0.5, 1))
					self.cards.remove(c)
					self.selected = []
					if len(self.cards) == 1:
						self.win_game()
			elif card_img1 != card_img2:
				play_effect('game:Error', volume=0.4)
				for c in self.selected:
					c.animate('background', Color(1.0, 0.5, 0.5, 1), duration=0.05)

	def new_game(self):
		play_effect('arcade:Coin_2', volume=0.7)
		self.deal()
		self.root_layer.animate('scale_x', 1.0)
		self.root_layer.animate('scale_y', 1.0)

	def win_game(self):
		self.delay(0.5, partial(play_effect, 'Powerup_2'))
		font_size = 100 if self.size.w > 700 else 50
		win_text = TextLayer('Well Done!', 'Futura', font_size)
		win_text.frame.center(self.bounds.center())
		overlay = Layer(self.bounds)
		overlay.background = Color(0, 0, 0, 0)
		overlay.add_layer(win_text)
		self.add_layer(overlay)
		overlay.animate('background', Color(0.0, 0.2, 0.3, 0.7))
		win_text.animate('scale_x', 1.3, 0.3, autoreverse=True)
		win_text.animate('scale_y', 1.3, 0.3, autoreverse=True)
		self.touch_disabled = True
		self.root_layer.animate('scale_x', 0.0, delay=2.0, curve=curve_ease_back_in)
		self.root_layer.animate('scale_y', 0.0, delay=2.0, curve=curve_ease_back_in, completion=self.new_game)


if __name__ == '__main__':
	run(Game())
