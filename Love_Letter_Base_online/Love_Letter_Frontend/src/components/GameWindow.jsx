export default function GameWindow() {
    return (
        <div style={{ width: '800px', height: '600px' }}>
            <iframe
                src="build_offline/web/index.html"
                width="800"
                height="600"
                style={{ border: 'none' }}
            ></iframe>
        </div>
    )
}