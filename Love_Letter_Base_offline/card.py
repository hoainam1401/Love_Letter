CARD_VALUES = {
    "Assassin": 0,
    "Jester": 0,
    "Guard": 1,
    "Priest": 2,
    "Cardinal": 2,
    "Baron": 3,
    "Baroness": 3,
    "Handmaid": 4,
    "Sycophant": 4,
    "Prince": 5,
    "Count": 5,
    "King": 6,
    "Constable": 6,
    "Countess": 7,
    "Queen": 7,
    "Princess": 8,
    "Bishop": 9,
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
