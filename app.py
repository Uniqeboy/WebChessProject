from flask import Flask, jsonify, render_template, request
from chess_engine import create_game, is_valid_move, make_move, check_game_status

app = Flask(__name__)

# single source of truth for game state
game = create_game()
game["turn"] = "white"
game["history"] = [] 

@app.route("/")
def home():
    return render_template("index.html")

def determine_sound(is_capture, status):
    if status == "checkmate":
        return "checkmate"
    if status == "stalemate":
        return "stalemate"
    if status in ("check_white", "check_black"):
        return "check"
    if is_capture:
        return "capture"
    return "move"


@app.route("/state")
def get_state():
    return jsonify({
        "board": game["board"],
        "turn": game["turn"]
    })


@app.route("/move", methods=["POST"])
def make_move_api():
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
    result = make_move(game, r1, c1, r2, c2)
    is_capture = result["is_capture"]

    # 🔐 SAFETY: ensure history always exists
    if "history" not in game:
        game["history"] = []

    move_notation = f"{chr(c1 + 97)}{8 - r1} → {chr(c2 + 97)}{8 - r2}"
    game["history"].append(move_notation)

    # 🔥 switch turn ONLY here
    game["turn"] = "black" if game["turn"] == "white" else "white"

    status = check_game_status(game, game["turn"])
    sound = determine_sound(is_capture, status)

    # 🔊 STEP 4 HAPPENS HERE
    sound = determine_sound(is_capture, status)
    return jsonify({
        "board": game["board"],
        "turn": game["turn"],
        "status": status,
        "history": game["history"],
        "sound": sound      # 👈 THIS IS NEW
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


@app.route("/game-over")
def game_over():
    return render_template("game_over.html")


@app.route("/reset", methods=["POST"])
def reset_game():
    global game
    game = create_game()
    game["turn"] = "white"
    game["history"] = []   # ✅ ADD THIS

    return jsonify({
        "board": game["board"],
        "turn": game["turn"],
        "status": "ok",
        "history": game["history"]
    })

if __name__ == "__main__":
    app.run(debug=True)