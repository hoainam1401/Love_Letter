import "../styles/Card.css"
// import Assassin from "../assets/images/Assassin.png";
// import Jester from "../assets/images/Jester.png";
// import Guard from "../assets/images/Guard.png";
// import Priest from "../assets/images/Priest.png";
// import Cardinal from "../assets/images/Cardinal.png";
// import Baron from "../assets/images/Baron.png";
// import Baroness from "../assets/images/Baroness.png";
// import Handmaid from "../assets/images/Handmaid.png";
// import Sycophant from "../assets/images/Sycophant.png";
// import Prince from "../assets/images/Prince.png";
// import Count from "../assets/images/Count.png";
// import King from "../assets/images/King.png";
// import Constable from "../assets/images/Constable.png";
// import Countess from "../assets/images/Countess.png";
// import Dowager from "../assets/images/Dowager.png";
// import Princess from "../assets/images/Princess.png";
// import Bishop from "../assets/images/Bishop.png";
// const CardImages = {
//     Assassin,
//     Jester,
//     Guard,
//     Priest,
//     Cardinal,
//     Baron,
//     Baroness,
//     Handmaid,
//     Sycophant,
//     Prince,
//     Count,
//     King,
//     Constable,
//     Countess,
//     Dowager,
//     Princess,
//     Bishop,
// };
export default function Card(props) {
    return (
        <article className="card-article">
            {/* <img src={CardImages[props.img]}></img> */}
            <img src={`/src/assets/images/${props.img}.png`}></img>
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