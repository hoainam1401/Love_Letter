export default function Header() {
    return (
        <header>
            <div className="left-block">
                <button><img src="src\assets\logo.png" className="home-logo"></img></button>
                <button>Leaderboard</button>
                <button>How to play</button>
            </div>
            <div className="log-block">
                <button>Register</button>
                <button>Log in</button>
            </div>
        </header >
    )
}