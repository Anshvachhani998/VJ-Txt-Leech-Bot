from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Tech VJ'

@app.route('/play')
def play_video():
    video_url = request.args.get('url')
    if not video_url:
        return "Video URL missing!", 400
    return render_template('video.html', video_url=video_url)

if __name__ == "__main__":
    app.run()
