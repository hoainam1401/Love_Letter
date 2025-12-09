class Card:
    name: str = ""
    val: int = 0


def __init__(self, name):
    self.name = name
    if self.name == "Guard":
        self.val = 1
    elif self.name == "Priest":
        self.val = 2
    elif self.name == "Baron":
        self.val = 3
    elif self.name == "Handmaid":
        self.val = 4
    elif self.name == "Prince":
        self.val = 5
    elif self.name == "King":
        self.val = 6
    elif self.name == "Countess":
        self.val = 7
    elif self.name == "Princess":
        self.val = 8
