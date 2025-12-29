from flask import Flask, request, render_template, redirect, url_for, session
from script import Questions

app = Flask(__name__)
brain = Questions()


@app.route("/", methods= ["GET", "POST"])
def index():
    topics = brain.fetch_quiz_topics()
    return render_template("index.html", topics=topics)


@app.route("/quiz", methods= ["POST"])
def quiz():
    data = brain.get_questions(topic= request.form.get("topic"), 
                               limit= int(request.form.get("limit")),
                               difficulty= request.form.get("difficulty"))
    
    session['quiz_data'] = data
    
    return render_template("quiz.html", data=data)

@app.route("/result", methods= ["POST"])
def result():
    pass


@app.route("/history", methods=["GET"])
def history():
    pass


if __name__ == "__main__":
    app.run(debug=True)