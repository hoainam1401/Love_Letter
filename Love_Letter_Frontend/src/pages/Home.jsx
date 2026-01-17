import { useState, useEffect } from "react"
import api from "../api"
// import Note from "../components/Note"
import GameWindow from "../components/GameWindow"

export default function Home() {
    const [notes, setNotes] = useState([])
    const [content, setContent] = useState("")
    const [title, setTitle] = useState("")

    useEffect(() => {
        getNotes("useEffect")
    }, [])
    function getNotes() {
        api.get("/api/notes/")
            .then((res) => res.data)
            .then((data) => { setNotes(data); console.log(data) })
            .catch((err) => alert(err))
    }

    const deleteNode = (id) => {
        api.delete(`/api/notes/delete/${id}`)
            .then((res) => {
                if (res.status === 204) alert("Note deleted!")
                else alert("Failed to delete node.")
                getNotes()
            })
            .catch((err) => alert(err))
    }

    const createNote = (e) => {
        e.preventDefault()
        api.post("/api/notes/", { content, title })
            .then((res) => {
                if (res.status === 201) alert("Note created!")
                else alert("Failed to make note.")
                getNotes()
            })
            .catch((err) => alert(err))
    }
    return <>
        <GameWindow />
        {/* <div>
            <h2>Notes</h2>
            {notes.map((note) => <Note note={note} onDelete={deleteNode} key={note.id} />)}
        </div>
        <h2>Create a Note</h2>
        <form onSubmit={createNote}>
            <label htmlFor="title">Title:</label>
            <br />
            <input
                type="text"
                id="title"
                name="title"
                required
                onChange={(e) => setTitle(e.target.value)}
                value={title} />
            <label htmlFor="content">Content:</label>
            <br />
            <textarea
                type="text"
                id="content"
                name="content"
                required
                onChange={(e) => setContent(e.target.value)}
                value={content} />
            <input type="submit" value="Submit"></input>
        </form> */}
    </>
}