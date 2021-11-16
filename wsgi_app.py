from fichabot import app


@app.route('/heartbeat')
def heartbeat():
    return "{'response': 'OK'}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
