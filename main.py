from flask import Flask, send_file
from controller.resume_controller import resume_controller

app = Flask(__name__)
app.register_blueprint(resume_controller)

@app.route('/')
def index():
    return send_file('static/index.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
