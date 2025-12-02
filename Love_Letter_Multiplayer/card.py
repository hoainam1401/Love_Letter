from abc import abstractmethod


class Card:
    name: str = ""
    val: int = 0
    img: str = ""

    def __init__(self, name):
        self.name = name
        if self.name == "Guard":
            self.val = 1
            self.img = f"images/{self.name}.png"
        elif self.name == "Priest":
            self.val = 2
            self.img = f"images/{self.name}.png"
        elif self.name == "Baron":
            self.val = 3
            self.img = f"images/{self.name}.png"
        elif self.name == "Handmaid":
            self.val = 4
            self.img = f"images/{self.name}.png"
        elif self.name == "Prince":
            self.val = 5
            self.img = f"images/{self.name}.png"
        elif self.name == "King":
            self.val = 6
            self.img = f"images/{self.name}.png"
        elif self.name == "Countess":
            self.val = 7
            self.img = f"images/{self.name}.png"
        elif self.name == "Princess":
            self.val = 8
            self.img = f"images/{self.name}.png"
