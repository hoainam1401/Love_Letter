from abc import abstractmethod


class Card:
    name: str = ""
    val: int = 0
    img: str = ""

    def __init__(self, name):
        self.name = name
        match self.name:
            case "Guard":
                self.val = 1
                self.img = f"images/{self.name}.png"
            case "Priest":
                self.val = 2
                self.img = f"images/{self.name}.png"
            case "Baron":
                self.val = 3
                self.img = f"images/{self.name}.png"
            case "Handmaid":
                self.val = 4
                self.img = f"images/{self.name}.png"
            case "Prince":
                self.val = 5
                self.img = f"images/{self.name}.png"
            case "King":
                self.val = 6
                self.img = f"images/{self.name}.png"
            case "Countess":
                self.val = 7
                self.img = f"images/{self.name}.png"
            case "Princess":
                self.val = 8
                self.img = f"images/{self.name}.png"
