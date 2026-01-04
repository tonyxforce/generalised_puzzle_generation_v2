from generator import UrjoGenerator

import time
import json
import os

ts = round(time.time())

if not "output" in os.listdir("."):
    os.mkdir("./output")

generated = []

while True:
        generator = UrjoGenerator()
        generated_board = generator.create_puzzle(8, 8, number_of_numbers=5, contradiction_count=2)
        generated.append([generated_board.to_url_format(), generated_board.contradiction_count])

        with (open(f"output/{ts}.json", "x" if not f"{ts}.json" in os.listdir("./output") else "w")) as file:
            file.write(json.dumps(generated, indent=4))

        print(generated_board.to_url_format(), generated_board.contradiction_count)
        
        generator.true_check()