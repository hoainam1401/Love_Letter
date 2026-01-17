import { useNavigate } from "react-router-dom"
import "../styles/Header.css"
import logo from "../assets/logo.png"

export default function Header() {
    const navigate = useNavigate()
    const handleSubmit = (e) => {
        let buttonText = e.target.innerHTML
        let method
        switch (buttonText) {
            case "Leaderboard":
                method = "leaderboard"
                break
            case "How to play":
                method = "tutorial"
                break
            case "Register":
                method = "register"
                break
            case "Log in":
                method = "login"
                break
            default:
                break
        }
        navigate(`/${method}/`)
    }
    return (
        <header>
            <div className="left-block">
                <button onClick={handleSubmit} ><img src={logo} className="home-logo"></img></button>
                <button onClick={handleSubmit}>Leaderboard</button>
                <button onClick={handleSubmit}>How to play</button>
            </div>
            <div className="log-block">
                <button onClick={handleSubmit}>Register</button>
                <button onClick={handleSubmit}>Log in</button>
            </div>
        </header >
    )
}