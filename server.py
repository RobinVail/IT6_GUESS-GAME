import socket
import random
import json
import os
"------------------------------------"
host = ""
port = 7777
banner = """
== Guessing Game v1.1 ==
Choose difficulty:
a. easy (1-50)
b. medium (1-100)
c. hard (1-500)
Enter your choice: """

"------------------------------------"

score_file = "scores.json"

def generate_random_int(low, high):
    return random.randint(low, high)

def load_scores():
    if os.path.exists(score_file):
        with open(score_file, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(score_file, "w") as f:
        json.dump(scores, f)

def update_leaderboard(scores):
    leaderboard = "\n== Leaderboard ==\n"
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'])
    for name, info in sorted_scores:
        leaderboard += f"{name}: {info['score']} tries (last difficulty: {info['difficulty']})\n"
    return leaderboard
"------------------------------------"



scores = load_scores()

# initialize the socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print(f"Server is listening on port {port}")

conn = None
guessme = 0
tries = 0
current_user = ""
current_difficulty = "easy"
difficulty_ranges = {
    "a": (1, 50),
    "b": (1, 100),
    "c": (1, 500)
}


"------------------------------------"



while True:
    if conn is None:
        print("Waiting for connection...")
        conn, addr = s.accept()
        print(f"New client: {addr[0]}")
        conn.sendall(banner.encode())
        current_user = ""
    else:
        client_input = conn.recv(1024).decode().strip()
        if not current_user:
            current_user = client_input
            if current_user not in scores:
                scores[current_user] = {"score": float('inf'), "difficulty": "a"}
            leaderboard = update_leaderboard(scores)
            conn.sendall(f"Welcome, {current_user}! {leaderboard}\nChoose difficulty: ".encode())
        elif current_user and current_difficulty == "easy":
            if client_input in difficulty_ranges:
                low, high = difficulty_ranges[client_input]
                guessme = generate_random_int(low, high)
                current_difficulty = client_input
                tries = 0
                conn.sendall(f"Difficulty set to {client_input}. Guess a number between {low} and {high}: ".encode())
            else:
                conn.sendall(b"Invalid choice. Choose difficulty: ")
        else:
            try:
                guess = int(client_input)
                tries += 1
                if guess == guessme:
                    if tries < scores[current_user]["score"]:
                        scores[current_user]["score"] = tries
                        scores[current_user]["difficulty"] = current_difficulty
                        save_scores(scores)
                    conn.sendall(f"Correct! It took you {tries} tries. Play again? (yes/no): ".encode())
                    current_difficulty = "easy"
                elif guess > guessme:
                    conn.sendall(b"Guess Lower! Enter guess: ")
                elif guess < guessme:
                    conn.sendall(b"Guess Higher! Enter guess: ")
            except ValueError:
                if client_input.lower() == "yes":
                    conn.sendall(banner.encode())
                    current_user = ""
                elif client_input.lower() == "no":
                    leaderboard = update_leaderboard(scores)
                    conn.sendall(f"Goodbye! {leaderboard}".encode())
                    conn.close()
                    conn = None
                else:
                    conn.sendall(b"Invalid input. Play again? (yes/no): ")

