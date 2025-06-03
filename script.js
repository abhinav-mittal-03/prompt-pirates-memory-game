$(document).ready(function() {
    let gameBoard = $('#game-board');
    let status = $('#status');
    let matchedCards = [];  // Track all matched cards
    let cardColors = [];
    let gridSize = 4;
    let numPlayers = 1;
    let currentlyFlipped = [];
    let isProcessing = false;
    let bestScore = null;

    function renderBoard(colors, size) {
        gameBoard.empty();
        gameBoard.css('grid-template-columns', `repeat(${size}, 1fr)`);
        for (let i = 0; i < size * size; i++) {
            gameBoard.append(`<div class="card" data-index="${i}"></div>`);
        }
        cardColors = colors;
        matchedCards = [];
        currentlyFlipped = [];
        isProcessing = false;
    }

    function showGameOverDialog(moves, winner, bestScore, isSinglePlayer) {
        let msg = '';
        if (isSinglePlayer) {
            msg = `Game Over!\nYour Moves: ${moves[0]}\nBest Score: ${bestScore || moves[0]}`;
        } else {
            if (typeof winner === 'string' && winner.startsWith('Tie')) {
                msg = `Game Over!\n${winner}\nMoves: ${moves.join(', ')}`;
            } else {
                msg = `Game Over!\nPlayer ${winner} wins!\nMoves: ${moves.join(', ')}`;
            }
        }
        if (confirm(msg + '\n\nPlay again?')) {
            restartGame();
        }
    }

    function restartGame() {
        $.ajax({
            url: '/restart',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ grid_size: gridSize, num_players: numPlayers }),
            success: function(response) {
                $.get('/get-cards', function(data) {
                    renderBoard(data.cards, gridSize);
                    bestScore = response.best_score;
                    status.text('Game restarted!' + (numPlayers == 1 && bestScore ? ` | Best Score: ${bestScore}` : ''));
                });
            }
        });
    }

    $('#start-game').click(function() {
        gridSize = $('#grid-size').val();
        numPlayers = $('#num-players').val();

        $.ajax({
            url: '/start',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ grid_size: gridSize, num_players: numPlayers }),
            success: function(response) {
                // Fetch the shuffled card colors from the backend
                $.get('/get-cards', function(data) {
                    renderBoard(data.cards, gridSize);
                    bestScore = response.best_score;
                    status.text(response.message + (numPlayers == 1 && bestScore ? ` | Best Score: ${bestScore}` : ''));
                });
            }
        });
    });

    gameBoard.on('click', '.card', function() {
        if (isProcessing) return;
        
        let index = $(this).data('index');
        
        // Don't allow clicking already matched cards
        if (matchedCards.includes(index)) return;
        
        // Don't allow clicking already flipped cards
        if (currentlyFlipped.includes(index)) return;

        // Flip the card visually
        $(this).css('background', cardColors[index]);
        currentlyFlipped.push(index);

        if (currentlyFlipped.length === 2) {
            isProcessing = true;
        }

        $.ajax({
            url: '/flip',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ index: index }),
            success: function(response) {
                if (response.error) {
                    status.text(response.error);
                    isProcessing = false;
                } else {
                    if (currentlyFlipped.length === 2) {
                        setTimeout(function() {
                            if (response.match_result === true) {
                                if (response.matched_indices && response.matched_indices.length === 2) {
                                    matchedCards.push(response.matched_indices[0]);
                                    matchedCards.push(response.matched_indices[1]);
                                }
                            } else {
                                $(`.card[data-index="${currentlyFlipped[0]}"]`).css('background', '#fff');
                                $(`.card[data-index="${currentlyFlipped[1]}"]`).css('background', '#fff');
                            }
                            currentlyFlipped = [];
                            isProcessing = false;
                            status.text(`Moves: ${response.moves.join(', ')}`);
                            if (response.game_over) {
                                bestScore = response.best_score;
                                showGameOverDialog(response.moves, response.winner, bestScore, numPlayers == 1);
                            }
                        }, 1000);
                    }
                }
            }
        });
    });
});
