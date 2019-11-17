import random

board = [
    [0, 5, 4, 0, 0, 0, 0, 0, 5, 5],
    [0, 0, 0, 3, 0, 0, 0, 0, 0, 1],
    [0, 2, 0, 0, 0, 0, 5, 4, 0, 0],
    [0, 0, 0, 0, 0, 0, 5, 0, 0, 0],
    [0, 0, 0, 2, 1, 0, 0, 0, 0, 5],
    [0, 0, 0, 0, 0, 0, 4, 0, 0, 0],
    [0, 3, 0, 4, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 0, 0, 2],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 0, 5, 0, 4]
]

# czas przejścia z kratki do kratki
t = 10
# max czas zwiedzania
T = 200  # Th
# liczba kategorii
N = 5

# liczba wszystkich atrakcji w danych kategoriach
# c = [3,4,3,5,3]
# funkcja wagi dla danych kategorii
w = [1, 2, 3, 4, 5]
# min liczba odwiedzaonych atrakcji w danych kategoriach
g = [1, 1, 1, 1, 3]

MAX_NEIGHBOURHOOD_SEARCH_SIZE = 3
ITERATION_NUMBER = 10
BEE_RANDOM_SEARCHER_NUMBER = 5
SEARCH_NEIGHBOURHOOD_ITERATION_NUMBER = 100

best_solution_of_all = []

# liczba odwiedzonych atrakcji dla danych kategorii
v = []


class Bee:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def find_random_path(starting_x, starting_y):
        path = [[starting_x, starting_y]]
        directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        time = 0
        last_x = starting_x
        last_y = starting_y

        while time <= T:
            r = random.randint(0, 3)
            x = directions[r][0] + last_x
            y = directions[r][1] + last_y
            last_x = x
            last_y = y
            if 0 <= x < len(board) and 0 <= y < len(board):
                if board[x][y] != 0 and [x, y] not in path:
                    path.append([x, y])
                    time = calculate_distance(path)
            else:
                last_x = path[-1][0]
                last_y = path[-1][1]

        path = path[:-1]
        # print("RANDOM PATH: ", path)
        # print("TIME: ", calculate_distance(path))
        return path

    def search_neighbourhood(self, solution):
        x = self.x
        y = self.y
        dfs_queue = [[x, y]]
        attractions = []
        used = []

        while dfs_queue:
            point_x, point_y = dfs_queue[0]
            dfs_queue.pop(0)
            search_size = abs(point_x - x) + abs(point_y - y)
            if search_size > MAX_NEIGHBOURHOOD_SEARCH_SIZE:
                break

            for i, j in [[-1, 0], [0, 1], [1, 0], [0, -1]]:
                if 0 <= point_x + i < len(board) and 0 <= point_y + j < len(board) \
                        and [point_x + i, point_y + j] not in used \
                        and [point_x + i, point_y + j] not in dfs_queue \
                        and [point_x + i, point_y + j] not in solution:
                    if board[point_x + i][point_y + j] != 0:
                        attractions.append([point_x + i, point_y + j])
                    dfs_queue.append([point_x + i, point_y + j])
            used.append([point_x, point_y])

        return attractions

    @staticmethod
    def fly_from_some_point(path):
        x = 0
        y = 0
        if path:
            x = path[-1][0]
            y = path[-1][1]
        time = calculate_distance(path)
        while time <= T:
            x, y = get_nearest(x, y, path, range(1, 6))
            path.append([x, y])
            time = calculate_distance(path)

        path = path[:-1]
        return path


def create_new_solution(old_solution, start_pos, new_attractions):
    new_solution = []

    for position in old_solution:
        new_solution.append(position)
        if position == start_pos:
            new_solution = new_solution + new_attractions

    # print("ATTRACTIONS: ", new_attractions)
    # print("NEW SOLUTION: ", new_solution)

    distance = calculate_distance(new_solution)
    while distance > T:
        new_solution = new_solution[:-1]
        distance = calculate_distance(new_solution)
        # print("SEC NEW: ", new_solution)
    return new_solution


def optimize(start_solution):
    optimized_solutions = []
    all_random_solutions = []
    optimized_solutions.append(start_solution)

    print("\nBEFORE OPTIMIZE: ", start_solution, get_score(start_solution))
    for i in range(ITERATION_NUMBER):
        random_solutions = []
        some_new_solutions = []

        for j in range(BEE_RANDOM_SEARCHER_NUMBER):
            bee = Bee(0, 0)
            solution = bee.find_random_path(bee.x, bee.y)
            while solution in all_random_solutions:
                solution = bee.find_random_path(bee.x, bee.y)
            all_random_solutions.append(solution)
            random_solutions.append(solution)

        for k in range(SEARCH_NEIGHBOURHOOD_ITERATION_NUMBER):
            # jeśli nic nie zostało zoptymalizowane w poprzednich iteracjach to break
            if not optimized_solutions:
                break

            solution = optimized_solutions[0]
            optimized_solutions.pop()
            neighbourhood_size = len(solution) - 1

            for j in range(neighbourhood_size):
                # pozycja atrakcji wokół której przeszukujemy sąsiedztwo
                start_searching_pos = solution[j]
                start_searching_pos_index = j
                bee = Bee(solution[j][0], solution[j][1])
                new_attractions = bee.search_neighbourhood(solution)

                if new_attractions:
                    new_solution = create_new_solution(solution, start_searching_pos, new_attractions)
                    optimized_solutions.append(new_solution)
                    index = start_searching_pos_index + len(new_attractions) + 1
                    new_path = bee.fly_from_some_point(new_solution[:index])
                    some_new_solutions.append(new_path)

        optimized_solutions.append(start_solution)
        best_optimized_solutions = get_n_best_solutions(optimized_solutions, 3)

        for index, path in enumerate(best_optimized_solutions):
            print("\nBEST: ", index, path, get_score(path))

        if start_solution in best_optimized_solutions:
            best_optimized_solutions.remove(start_solution)
        optimized_solutions = best_optimized_solutions + random_solutions + some_new_solutions

    return optimized_solutions


def get_score(solution):
    return sum([w[board[pos[0]][pos[1]] - 1] for pos in solution])


def get_n_best_solutions(solutions_list, n):
    solutions_with_scores = []
    global best_solution_of_all

    for solution in solutions_list:
        score = get_score(solution)
        solutions_with_scores.append((solution, score))

    solutions_with_scores.sort(key=lambda tup: tup[1])
    solutions_with_scores = solutions_with_scores[::-1]

    for solution, score in solutions_with_scores:
        if validate_solution(solution):
            if score > get_score(best_solution_of_all):
                best_solution_of_all = solution
            break

    return [path for path, score in solutions_with_scores[:n]]


def validate_solution(path):
    min_per_category = g
    for pos in path:
        x = pos[0]
        y = pos[1]
        min_per_category[board[x][y] - 1] = min_per_category[board[x][y] - 1] - 1

    if not [val for val in min_per_category if val > 0]:
        print("VALID")
        return True

    print("NOT VALID")
    return False


def get_nearest(x, y, path, searched_categories):
    dfs_queue = [[x, y]]
    used = [[x, y]]

    while True:
        point_x, point_y = dfs_queue[0]
        dfs_queue.pop(0)

        if board[point_x][point_y] in searched_categories and [point_x, point_y] != [x, y] \
                and [point_x, point_y] not in path:
            return point_x, point_y

        for i, j in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
            if 0 <= point_x + i < len(board) and 0 <= point_y + j < len(board) and [point_x + i,
                                                                                    point_y + j] not in used:
                dfs_queue.append([point_x + i, point_y + j])
                used.append([point_x + i, point_y + j])


def find_first_solution(x, y):
    # searched_categories = [index+1 for index, i in enumerate(g) if i != 0]
    path = []
    time = 0
    while True:
        searched_point_x, searched_point_y = get_nearest(x, y, path, range(1, 6))
        time = time + (abs(x - searched_point_x) + abs(y - searched_point_y)) * t
        if time > T:
            break
        path.append([searched_point_x, searched_point_y])
        x, y = searched_point_x, searched_point_y
    return path


def calculate_distance(path):
    distance = 0
    for index, i in enumerate(path):
        if index != len(path) - 1:
            distance += abs(i[0] - path[index + 1][0]) + abs(i[1] - path[index + 1][1])
    return distance * t


def main():
    first_path = find_first_solution(0, 0)
    global best_solution_of_all
    print("\nFIRST: ", first_path)
    if validate_solution(first_path):
        best_solution_of_all = first_path
    optimize(first_path)
    print(best_solution_of_all)


if __name__ == "__main__":
    main()
