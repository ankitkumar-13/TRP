from flask import Flask, render_template, request, jsonify
import itertools
import math
import time
from functools import lru_cache

from db_setup import getAllCities

app = Flask(__name__)

cities = getAllCities()
cities = {city.name : city for city in cities}


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371  # Earth's radius
    return round(c * r, 2)

def get_distance(city1, city2):
    lat1, lon1 = cities[city1].lat, cities[city1].long
    lat2, lon2 = cities[city2].lat, cities[city2].long
    return round(haversine(lat1, lon1, lat2, lon2) * 1.3, 2)

def calculate_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += get_distance(route[i], route[i+1])
    return round(total_distance, 2)

def tsp_brute_force(cities_list, start_city):
    if len(cities_list) > 8:
        return [], 0, []
    
    shortest_route = None
    shortest_distance = float('inf')
    all_routes = []
    
    cities_to_permute = [city for city in cities_list if city != start_city]

    for perm in itertools.permutations(cities_to_permute):
        route = (start_city,) + perm + (start_city,)
        try:
            distance = calculate_distance(route)
            all_routes.append({"route": route, "distance": distance})
            if distance < shortest_distance:
                shortest_distance = distance
                shortest_route = route
        except KeyError as e:
            print(f"Skipping route due to missing distance data: {route}")
            continue

    return shortest_route, shortest_distance, all_routes

def tsp_dp(cities_list, start_city):
    if len(cities_list) > 15:
        return [], 0, []
    
    unique_cities = sorted(list(set(cities_list + [start_city])))
    n = len(unique_cities)
    city_index = {city: idx for idx, city in enumerate(unique_cities)}
    distance_matrix = [[0]*n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            distance_matrix[i][j] = get_distance(unique_cities[i], unique_cities[j])
    
    start_idx = city_index[start_city]
    
    @lru_cache(maxsize=None)
    def dp(mask, pos):
        if mask == (1 << n) - 1:
            return distance_matrix[pos][start_idx], [pos, start_idx]
        
        min_dist = float('inf')
        best_path = []
        
        for city in sorted(range(n), key=lambda x: unique_cities[x]):
            if not (mask & (1 << city)):
                new_mask = mask | (1 << city)
                dist, path = dp(new_mask, city)
                total_dist = distance_matrix[pos][city] + dist
                
                if total_dist < min_dist or (total_dist == min_dist and unique_cities[city] < unique_cities[best_path[0]]):
                    min_dist = total_dist
                    best_path = [pos] + path
        
        return min_dist, best_path
    
    initial_mask = 1 << start_idx
    min_distance, best_path_indices = dp(initial_mask, start_idx)
    best_route = [unique_cities[i] for i in best_path_indices]
    
    return best_route, min_distance, []

@app.route("/")
def index():
    return render_template("index.html", cities=list(cities.keys()))

@app.route("/plan", methods=["POST"])
def plan():
    data = request.json
    selected_cities = data.get("cities", [])
    start_city = data.get("start_city")

    if not selected_cities or len(selected_cities) < 2:
        return jsonify({"error": "Please select at least 2 cities."}), 400
    if not start_city:
        return jsonify({"error": "Please select a starting city."}), 400
    if len(selected_cities) > 15:
        return jsonify({"error": "Please select 15 or fewer cities for performance reasons."}), 400
    
    cities[start_city]._setLatLong()
    for i in selected_cities:
        cities[i]._setLatLong()
    
    start_time = time.time()
    bf_route, bf_distance, bf_all_routes = tsp_brute_force(selected_cities, start_city)
    bf_time = time.time() - start_time
    
    start_time = time.time()
    dp_route, dp_distance, _ = tsp_dp(selected_cities, start_city)
    dp_time = time.time() - start_time
    
    if not bf_route and not dp_route:
        return jsonify({"error": "Could not calculate a route with the selected cities."}), 400

    return jsonify({
        "brute_force": {
            "route": bf_route,
            "distance": bf_distance,
            "time": round(bf_time, 4),
            "all_routes": bf_all_routes,
        },
        "dynamic_programming": {
            "route": dp_route,
            "distance": dp_distance,
            "time": round(dp_time, 4),
        },
        "coordinates": [{"city": cities[city].name, "lat": cities[city].lat, "lon": cities[city].long} for city in dp_route],
        "comparison": {
            "distance_diff": round(abs(bf_distance - dp_distance), 2),
            "time_diff": round(abs(bf_time - dp_time), 4),
            "time_ratio": round(bf_time / dp_time, 2) if dp_time > 0 else "N/A"
        }
    })

@app.route("/get_city_info")
def get_city_info():
    city = request.args.get("city")
    if city not in cities:
        return jsonify({"error": "City not found"}), 404
    return jsonify({
        "culture": (cities[city].culture if(cities[city].culture != None) else "No cultural information available.")  ,
        "unique": (cities[city].unique if(cities[city].unique != None) else "No unique feature information available.")
    })

if __name__ == "__main__":
    app.run(debug=True)


    
