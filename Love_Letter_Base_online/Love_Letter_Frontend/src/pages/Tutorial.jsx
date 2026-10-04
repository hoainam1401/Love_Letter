import cardJSON from '../data/cards.json'
import Card from '../components/Card'

let cardList = cardJSON
export default function Tutorial() {
    return (
        <main>
            <h1>Cards Overview</h1>
            {cardList.map((card, index) =>
                <Card key={index} value={card.value} img={card.img} name={card.name} max={card.max} description={card.description} />
            )}
        </main>
    )
}