from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

colors = [
    "red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan",
    "brown", "lime", "magenta", "navy", "teal", "gold", "silver", "maroon",
    "olive", "coral"
]

game_state = {
    "grid_size": 4,
    "num_players": 1,
    "cards": [],
    "flipped_cards": [],
    "matched_pairs": 0,
    "current_player": 1,
    "moves": [0],
    "scores": [0],
    "best_score": None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    data = request.json
    grid_size = int(data['grid_size'])
    num_players = int(data['num_players'])

    required_pairs = (grid_size ** 2) // 2
    selected_colors = random.sample(colors, required_pairs)
    cards = selected_colors * 2
    random.shuffle(cards)

    game_state.update({
        "grid_size": grid_size,
        "num_players": num_players,
        "cards": cards,
        "flipped_cards": [],
        "matched_pairs": 0,
        "current_player": 1,
        "moves": [0] * num_players,
        "scores": [0] * num_players
    })

    return jsonify({"message": "Game started!", "grid_size": grid_size, "num_players": num_players})

@app.route('/flip', methods=['POST'])
def flip_card():
    data = request.json
    index = int(data['index'])

    if len(game_state['flipped_cards']) == 2:
        return jsonify({"error": "Wait for match/no match resolution."})

    if index in game_state['flipped_cards']:
        return jsonify({"error": "Card already flipped."})

    game_state['flipped_cards'].append(index)
    game_state['moves'][game_state['current_player'] - 1] += 1

    match_result = None
    matched_indices = []
    game_over = False
    best_score = game_state.get('best_score')
    winner = None

    if len(game_state['flipped_cards']) == 2:
        card1, card2 = game_state['flipped_cards']
        if card1 == card2:
            match_result = False
            game_state['flipped_cards'] = []
        elif game_state['cards'][card1] == game_state['cards'][card2]:
            game_state['matched_pairs'] += 1
            game_state['scores'][game_state['current_player'] - 1] += 1
            match_result = True
            matched_indices = [card1, card2]
            game_state['flipped_cards'] = []
        else:
            match_result = False
            game_state['flipped_cards'] = []
        game_state['current_player'] = (game_state['current_player'] % game_state['num_players']) + 1

    # Check for game over
    if game_state['matched_pairs'] == (game_state['grid_size'] ** 2) // 2:
        game_over = True
        if game_state['num_players'] == 1:
            moves = game_state['moves'][0]
            if best_score is None or moves < best_score:
                best_score = moves
                game_state['best_score'] = best_score
        else:
            min_moves = min(game_state['moves'])
            # If both players have the same minimum moves, it's a tie
            winners = [i+1 for i, m in enumerate(game_state['moves']) if m == min_moves]
            if len(winners) == 1:
                winner = winners[0]
            else:
                winner = 'Tie: ' + ', '.join(f'Player {w}' for w in winners)

    return jsonify({
        "flipped_cards": game_state['flipped_cards'],
        "matched_indices": matched_indices,
        "moves": game_state['moves'],
        "match_result": match_result,
        "game_over": game_over,
        "best_score": game_state.get('best_score'),
        "winner": winner
    })

@app.route('/restart', methods=['POST'])
def restart_game():
    data = request.json
    grid_size = int(data['grid_size'])
    num_players = int(data['num_players'])
    required_pairs = (grid_size ** 2) // 2
    selected_colors = random.sample(colors, required_pairs)
    cards = selected_colors * 2
    random.shuffle(cards)
    best_score = game_state.get('best_score') if num_players == 1 else None
    game_state.update({
        "grid_size": grid_size,
        "num_players": num_players,
        "cards": cards,
        "flipped_cards": [],
        "matched_pairs": 0,
        "current_player": 1,
        "moves": [0] * num_players,
        "scores": [0] * num_players,
        "best_score": best_score
    })
    return jsonify({"message": "Game restarted!", "grid_size": grid_size, "num_players": num_players, "best_score": best_score})

@app.route('/get-cards')
def get_cards():
    return jsonify({'cards': game_state['cards']})

if __name__ == '__main__':
    app.run(debug=True)
