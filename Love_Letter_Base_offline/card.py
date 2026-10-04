CARD_VALUES = {
    "Guard": 1,
    "Priest": 2,
    "Baron": 3,
    "Handmaid": 4,
    "Prince": 5,
    "King": 6,
    "Countess": 7,
    "Princess": 8,
}


class Card:
    name: str = ""
    val: int = 0
    img: str = ""

    def __init__(self, name):
        if name not in CARD_VALUES:
            raise ValueError(f"Unknown card: {name}")
        self.name = name
        self.val = CARD_VALUES[name]
        self.img = f"images/{self.name}.png"
