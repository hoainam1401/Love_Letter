import random

from card import CARD_VALUES
from card_pile import CARD_COUNTS


class AiController:
    def __init__(self, playerCount, rng=random):
        self.rng = rng
        self.reset(playerCount)

    def reset(self, playerCount):
        self.knownCards = {index: {} for index in range(1, playerCount)}

    def chooseCard(self, game, actorIndex):
        player = game.currPlayer
        if player.hasCountess and (player.hasPrince or player.hasKing):
            for index, card in enumerate(player.hand):
                if card.name == "Countess":
                    return index

        knowledge = self.knownCards[actorIndex]
        scores = []
        for index, card in enumerate(player.hand):
            otherCard = player.hand[1 - index]
            if card.name == "Princess":
                score = -100
            elif card.name == "Handmaid":
                score = 9
            elif card.name == "Guard":
                knownTarget = any(
                    name != "Guard" and game.isValidTarget(targetIndex)
                    for targetIndex, name in knowledge.items()
                )
                score = 12 if knownTarget else 6
            elif card.name == "Priest":
                score = 7
            elif card.name == "Baron":
                score = 8 if otherCard.val >= 5 else 2
            elif card.name == "Prince":
                knownPrincessTarget = any(
                    name == "Princess" and game.isValidTarget(targetIndex)
                    for targetIndex, name in knowledge.items()
                )
                score = 11 if knownPrincessTarget else 7
            elif card.name == "King":
                score = 8 if otherCard.val <= 3 else 3
            else:
                score = 1
            scores.append(score)

        bestScore = max(scores)
        choices = [index for index, score in enumerate(scores) if score == bestScore]
        return self.rng.choice(choices)

    def chooseTarget(self, game, actorIndex, cardName, targets):
        knowledge = self.knownCards[actorIndex]
        selectedCardIndex = game.selectedCardIndex
        remainingCard = game.currPlayer.hand[1 - selectedCardIndex]
        scores = {}
        for targetIndex in targets:
            knownCard = knowledge.get(targetIndex)
            score = self.rng.random()
            if cardName == "Guard" and knownCard not in (None, "Guard"):
                score += 100
            elif cardName == "Priest" and knownCard is None:
                score += 20
            elif cardName == "Baron" and knownCard is not None:
                difference = remainingCard.val - CARD_VALUES[knownCard]
                score += 30 if difference > 0 else -30 if difference < 0 else 0
            elif cardName == "Prince":
                if targetIndex == actorIndex:
                    score -= 25
                    if remainingCard.name == "Princess":
                        score -= 100
                if knownCard == "Princess":
                    score += 100
                elif knownCard is not None:
                    score += CARD_VALUES[knownCard]
            elif cardName == "King" and knownCard is not None:
                score += (CARD_VALUES[knownCard] - remainingCard.val) * 5
            scores[targetIndex] = score
        return max(scores, key=scores.get)

    def chooseGuess(self, game, actorIndex, targetIndex):
        knownCard = self.knownCards[actorIndex].get(targetIndex)
        if knownCard is not None and knownCard != "Guard":
            return CARD_VALUES[knownCard]

        remaining = dict(CARD_COUNTS)
        for card in game.removedCards:
            remaining[card.name] -= 1
        for player in game.playerList:
            for card in player.discardPile:
                remaining[card.name] -= 1
        for card in game.currPlayer.hand:
            remaining[card.name] -= 1

        bestCount = max(remaining[name] for name in remaining if name != "Guard")
        guesses = [
            CARD_VALUES[name]
            for name, count in remaining.items()
            if name != "Guard" and count == bestCount
        ]
        return self.rng.choice(guesses)

    def observeResolvedAction(self, game, actorIndex, cardName, targetIndex):
        for knowledge in self.knownCards.values():
            if cardName == "King":
                knowledge.pop(actorIndex, None)
                knowledge.pop(targetIndex, None)
            elif knowledge.get(actorIndex) == cardName:
                knowledge.pop(actorIndex, None)
            if cardName == "Prince":
                knowledge.pop(targetIndex, None)
            for playerIndex, player in enumerate(game.playerList):
                if player.isKO:
                    knowledge.pop(playerIndex, None)

        if actorIndex != 0 and targetIndex is not None:
            target = game.playerList[targetIndex]
            if cardName == "Priest" and target.hand:
                self.knownCards[actorIndex][targetIndex] = target.hand[0].name
            elif cardName == "King" and target.hand:
                self.knownCards[actorIndex][targetIndex] = target.hand[0].name

        if (
            cardName == "King"
            and targetIndex not in (None, 0)
            and game.playerList[actorIndex].hand
        ):
            self.knownCards[targetIndex][actorIndex] = game.playerList[actorIndex].hand[
                0
            ].name
