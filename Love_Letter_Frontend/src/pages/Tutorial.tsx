import cardJSON from '../components/cards.json'
import type { CardInfo } from '../components/Card'
import Card from '../components/Card'
let cardList: CardInfo[] = cardJSON as CardInfo[]
export default function Tutorial() {
    return (
        <main>
            <h1>Cards Overview</h1>
            {cardList.map(card =>
                <Card value={card.value} img={card.img} name={card.name} max={card.max} description={card.description} />
            )}
        </main>
    )
}