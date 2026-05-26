from flask import Flask, jsonify, Response
import requests

app = Flask(__name__)

LOGIN='1154880'


@app.route("/login")
def login():

    return jsonify({
        "author":LOGIN
    })


@app.route("/makeimage_alt")
def proxy():

    response = requests.get(
        "http://127.0.0.1:8001/makeimage_alt/",
        params={
            "width":500,
            "height":300,
            "text":"From Django"
        }
    )

    return Response(
        response.content,
        content_type=response.headers["Content-Type"]
    )


if __name__=="__main__":
    app.run(debug=True)