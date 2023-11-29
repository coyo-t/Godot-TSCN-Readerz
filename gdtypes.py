from dataclasses import dataclass

class GDNull:
	pass


@dataclass
class Vector2:
	x: float
	y: float


@dataclass
class Rect2:
	x: float
	y: float
	wide: float
	tall: float

