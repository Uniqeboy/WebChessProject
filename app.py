from flask import Flask, jsonify, render_template, request
from chess_engine import create_game, is_valid_move, make_move, check_game_status

app = Flask(__name__)

# single source of truth for game state
game = create_game()
game["turn"] = "white"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/state")
def get_state():
    return jsonify({
        "board": game["board"],
        "turn": game["turn"]
    })


@app.route("/move", methods=["POST"])
def make_move_api():
    print("BEFORE MOVE, backend turn =", game["turn"])

    data = request.json
    r1 = data["r1"]
    c1 = data["c1"]
    r2 = data["r2"]
    c2 = data["c2"]

    # 🔥 BACKEND is the only source of truth
    turn = game["turn"]

    # validate move
    if not is_valid_move(game, r1, c1, r2, c2, turn):
        return jsonify({"error": "illegal move"}), 400

    # apply move
    make_move(game, r1, c1, r2, c2)

    # 🔥 switch turn ONLY here
    game["turn"] = "black" if game["turn"] == "white" else "white"

    status = check_game_status(game, game["turn"])

    return jsonify({
        "board": game["board"],
        "turn": game["turn"],      # ⬅ frontend must use this
        "status": status
    })


@app.route("/legal-moves", methods=["POST"])
def legal_moves_api():
    data = request.json
    r = data["r"]
    c = data["c"]

    # 🔥 BACKEND is the only source of truth
    turn = game["turn"]

    moves = []

    for r2 in range(8):
        for c2 in range(8):
            if is_valid_move(game, r, c, r2, c2, turn):
                moves.append({"r": r2, "c": c2})

    return jsonify(moves)


if __name__ == "__main__":
    app.run(debug=True)
