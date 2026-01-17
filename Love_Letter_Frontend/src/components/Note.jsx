import React from "react";

export default function Note(props) {
    const formattedDate = new Date(props.note.created_at).toLocaleDateString("en-GB")
    return <div className="note-container">
        <p className="note-title">{props.note.title}</p>
        <p className="note-content">{props.note.content}</p>
        <p className="note-date">{formattedDate}</p>
        <button className="delete-button" onClick={() => props.onDelete(props.note.id)}>
            Delete
        </button>
    </div>
}