import heapq
import json
import os


def load_campus_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "campus_data.json")

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


campus_data = load_campus_data()

nodes = campus_data["nodes"]
edges = campus_data["edges"]

id_to_name = {}
name_to_id = {}
location_details = {}

for node in nodes:
    id_to_name[node["id"]] = node["name"]
    name_to_id[node["name"].lower()] = node["id"]
    location_details[node["name"]] = node


def build_graph():
    graph = {}

    for node in nodes:
        graph[node["id"]] = []

    for edge in edges:
        start = edge["from"]
        end = edge["to"]
        distance = edge["distance"]

        graph[start].append((end, distance))
        graph[end].append((start, distance))

    return graph


campus_graph = build_graph()


def normalize_location(location):
    if not location:
        return None

    location = location.strip().lower()

    aliases = {
        "gate": "Main Entrance",
        "main gate": "Main Entrance",
        "entrance": "Main Entrance",
        "main entrance": "Main Entrance",

        "lobby": "Ground Floor Entrance Lobby",
        "entrance lobby": "Ground Floor Entrance Lobby",
        "ground floor lobby": "Ground Floor Entrance Lobby",

        "library": "Central Library",
        "central library": "Central Library",
        "digital library": "Digital Library",

        "telepresence": "Telepresence Lab",
        "telepresence lab": "Telepresence Lab",

        "rnd": "R&D Centre",
        "r&d": "R&D Centre",
        "r and d": "R&D Centre",
        "r&d centre": "R&D Centre",
        "r&d center": "R&D Centre",

        "eee lab": "EEE Lab",
        "department of maths": "Department Of Maths",
        "dept of maths": "Department Of Maths",

        "physics": "Physics Lab",
        "physics lab": "Physics Lab",
        "chemistry": "Chemistry Lab",
        "chemistry lab": "Chemistry Lab",

        "programming lab": "Programming Lab 1",
        "programming lab 1": "Programming Lab 1",
        "programming lab 3": "Programming Lab 3",

        "cse first year section a": "CSE 1st Year Section A",
        "cse 1st year section a": "CSE 1st Year Section A",
        "section a": "CSE 1st Year Section A",

        "cse first year section b": "CSE 1st Year Section B",
        "cse 1st year section b": "CSE 1st Year Section B",
        "section b": "CSE 1st Year Section B",

        "cse first year section c": "CSE 1st Year Section C",
        "cse 1st year section c": "CSE 1st Year Section C",
        "section c": "CSE 1st Year Section C",

        "cse project lab": "CSE Project Lab",
        "eee project room": "EEE Project Room",
        "electrical lab": "Electrical Lab",
        "eee computer lab": "EEE Computer Lab",

        "basic electrical lab": "Basic Electrical Lab",
        "advanced electrical lab": "Advanced Electrical Lab",
        "power electronics lab": "Power Electronics Lab",

        "seminar hall": "Seminar Hall",
        "environmental lab": "Environmental Research Lab",
        "environmental research lab": "Environmental Research Lab",

        "lift": "Lift Upper Ground",
        "elevator": "Lift Upper Ground",

        "staircase": "Ground Floor Staircase East",
        "stairs": "Ground Floor Staircase East"
    }

    if location in aliases:
        return aliases[location]

    for name in name_to_id:
        if name == location:
            return id_to_name[name_to_id[name]]

    for name in name_to_id:
        if location in name:
            return id_to_name[name_to_id[name]]

    return None


def dijkstra(start_name, end_name):
    start_name = normalize_location(start_name)
    end_name = normalize_location(end_name)

    if start_name is None or end_name is None:
        return [], 0

    start_id = name_to_id.get(start_name.lower())
    end_id = name_to_id.get(end_name.lower())

    if start_id is None or end_id is None:
        return [], 0

    distances = {}
    previous = {}

    for node in campus_graph:
        distances[node] = float("inf")

    distances[start_id] = 0

    priority_queue = [(0, start_id)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == end_id:
            break

        for neighbor, weight in campus_graph[current_node]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    if distances[end_id] == float("inf"):
        return [], 0

    path_ids = []
    current = end_id

    while current != start_id:
        path_ids.append(current)
        current = previous[current]

    path_ids.append(start_id)
    path_ids.reverse()

    path_names = [id_to_name[node_id] for node_id in path_ids]

    return path_names, distances[end_id]


def get_edge_distance(from_name, to_name):
    from_id = name_to_id[from_name.lower()]
    to_id = name_to_id[to_name.lower()]

    for neighbor, distance in campus_graph[from_id]:
        if neighbor == to_id:
            return distance

    return 0


def generate_instructions(path):
    instructions = []

    for i in range(len(path) - 1):
        current = path[i]
        next_location = path[i + 1]

        distance = get_edge_distance(current, next_location)
        next_type = location_details[next_location]["type"]
        next_floor = location_details[next_location]["floor"]

        if next_type == "staircase":
            text = f"Walk {distance} meters from {current} to {next_location}. Use the staircase."
        elif next_type == "lift":
            text = f"Walk {distance} meters from {current} to {next_location}. Use the lift."
        elif next_type == "corridor":
            text = f"Walk {distance} meters from {current} to {next_location} through the corridor."
        else:
            text = f"Walk {distance} meters from {current} to {next_location} on {next_floor}."

        instructions.append({
            "step": i + 1,
            "from": current,
            "to": next_location,
            "distance": distance,
            "instruction": text
        })

    return instructions


def get_turn_by_turn(start, end):
    path, distance = dijkstra(start, end)

    if not path:
        return [], [], 0, 0

    instructions = generate_instructions(path)

    estimated_time = round(distance / 1.4)

    return path, instructions, distance, estimated_time


if __name__ == "__main__":
    start = "Main Entrance"
    end = "Chemistry Lab"

    path, instructions, distance, estimated_time = get_turn_by_turn(start, end)

    print("Shortest Path:")
    print(" -> ".join(path))

    print("Total Distance:", distance, "meters")
    print("Estimated Time:", estimated_time, "seconds")

    print("\nInstructions:")
    for item in instructions:
        print(item["step"], item["instruction"])