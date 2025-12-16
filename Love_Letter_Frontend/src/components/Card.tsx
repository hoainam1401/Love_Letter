export type CardInfo = {
    value: number;
    img: string;
    name: string;
    max: number;
    description: string;
}
export default function Card(props: CardInfo) {
    return (
        <article className="card-article">
            <img src={`src/assets/images/${props.img}.png`}></img>
            <div className="card-info">
                <div className="card-title">
                    <span>{props.value}. {props.name}</span>
                    <span>Max copies: {props.max}</span>
                </div>
                <p>{props.description}</p>
            </div>
        </article >
    )
}