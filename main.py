from board import UrjoBoard

while True:
    board = UrjoBoard()
    board.create_puzzle(8,8, number_of_numbers=5, contradiction_count=2)
    print(board.to_url_format(), board.contradiction_count)

    #if urjo.contradiction_count > 5 :
    #    print(urjo.to_url_format(), urjo.contradiction_count)
    #if urjo.removed_by_identical > 0:
    #    print(urjo.to_url_format(), urjo.removed_by_identical)
    board.true_check()