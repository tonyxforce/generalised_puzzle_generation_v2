from generator import UrjoBoard

import time
import json
import os

ts = round(time.time())

if not "output" in os.listdir("."):
    os.mkdir("./output")

generated = []

while True:
        board = UrjoBoard()
        board.create_puzzle(8,8, number_of_numbers=5, contradiction_count=2)
        generated.append([board.to_url_format(), board.contradiction_count])

        with (open(f"output/{ts}.json", "x" if not f"{ts}.json" in os.listdir("./output") else "w")) as file:
            file.write(json.dumps(generated, indent=4))

        print(board.to_url_format(), board.contradiction_count)
        
        board.true_check()