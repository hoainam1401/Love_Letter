class Player:
    # new player mode?
    name: str = ""
    # one player can have up to 2 cards at a time
    handCard: list = []

    # track various stats of player during the round
    isKO: bool = False  # KO = is knocked out of the round
    hasHandmaid: bool = False

    # these are in extended edition
    # hasConstable: bool = False
    # hasAssassin: bool = False
    # hasCount: int = 0

    finalPoint: int = 0  # to compare with other players when game ends

    # track winning points of this player
    winningTokenCount = 0

    def __init__(self, name):
        self.name = name
        self.handCard = []
        self.isKO = False
        self.hasHandmaid = False
        # self.hasConstable = False
        # self.hasAssassin = False
        # self.hasCount = 0
        self.finalPoint = 0
        self.winningTokenCount = 0
