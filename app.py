from flask import Flask, render_template, request, jsonify
import itertools
import math
import time
from functools import lru_cache

app = Flask(__name__)

cities = {
    # Dehradun District
    "Dehradun": {
        "lat": 30.3165, "lon": 78.0322,
        "distances": {"Mussoorie": 35, "Haridwar": 55, "Rishikesh": 45, "Sahastradhara": 15, "Tehri": 90},
        "culture": "Capital city known for its Basmati rice and the Indian Military Academy. Mix of Garhwali culture and modern influences.",
        "unique": "Robber's Cave (Guchhupani) and Forest Research Institute."
    },
    "Mussoorie": {
        "lat": 30.4598, "lon": 78.0644,
        "distances": {"Dehradun": 35, "Dhanaulti": 25, "Kempty Falls": 15, "Tehri": 60},
        "culture": "Queen of Hills with colonial heritage and beautiful churches.",
        "unique": "Camel's Back Road and Lal Tibba (highest point)."
    },
    # Haridwar District
    "Haridwar": {
        "lat": 29.9457, "lon": 78.1642,
        "distances": {"Rishikesh": 25, "Dehradun": 55, "Rajaji National Park": 10, "Tehri": 120},
        "culture": "One of Hinduism's seven holiest places, known for Kumbh Mela.",
        "unique": "Har Ki Pauri Ganga Aarti and gateway to Char Dham."
    },

    # Tehri Garhwal District
    "Tehri": {
        "lat": 30.3838, "lon": 78.4801,
        "distances": {"Dehradun": 90, "Ghansali": 45, "Chamba": 30, "Mussoorie": 60, "Haridwar": 120, "Uttarkashi": 80},
        "culture": "Famous for Tehri Dam and traditional Garhwali folk culture.",
        "unique": "Asia's highest hydroelectric dam and New Tehri township."
    },

    # Uttarkashi District
    "Uttarkashi": {
        "lat": 30.7296, "lon": 78.4434,
        "distances": {"Gangotri": 100, "Yamunotri": 130, "Harsil": 70, "Tehri": 80},
        "culture": "Spiritual town known as 'Kashi of the North' with ancient temples.",
        "unique": "Nehru Institute of Mountaineering and Vishwanath Temple."
    },

    # Chamoli District
    "Joshimath": {
        "lat": 30.5555, "lon": 79.5606,
        "distances": {"Auli": 15, "Badrinath": 45, "Valley of Flowers": 50, "Rudraprayag": 70},
        "culture": "Winter seat of Badrinath deity with strong pilgrimage traditions.",
        "unique": "Gateway to Auli ski destination and India's highest cable car."
    },

    # Rudraprayag District
    "Rudraprayag": {
        "lat": 30.2848, "lon": 78.9839,
        "distances": {"Kedarnath": 90, "Srinagar": 35, "Guptkashi": 25, "Joshimath": 70},
        "culture": "Confluence of Alaknanda and Mandakini rivers, sacred pilgrimage stop.",
        "unique": "Ancient temples and stunning Himalayan views."
    },

    # Pauri Garhwal District
    "Pauri": {
        "lat": 30.1518, "lon": 78.7779,
        "distances": {"Kotdwar": 110, "Srinagar": 85, "Lansdowne": 90, "Rishikesh": 75},
        "culture": "Traditional Garhwali culture with panoramic Himalayan views.",
        "unique": "Kyunkaleshwar Mahadev Temple and sunset views of Himalayas."
    },

    # Almora District
    "Almora": {
        "lat": 29.5899, "lon": 79.6467,
        "distances": {"Kausani": 50, "Binsar": 30, "Ranikhet": 60, "Nainital": 65},
        "culture": "Cultural heart of Kumaon with famous folk music and dances.",
        "unique": "Bright End Corner for sunrise/sunset and traditional copperware."
    },

    # Nainital District
    "Nainital": {
        "lat": 29.3803, "lon": 79.4636,
        "distances": {"Bhimtal": 22, "Mukteshwar": 50, "Ramgarh": 40, "Almora": 65},
        "culture": "Colonial hill station with mixed British and Kumaoni influences.",
        "unique": "Naini Lake, Naina Devi Temple, and Snow View Point."
    },

    # Pithoragarh District
    "Pithoragarh": {
        "lat": 29.5829, "lon": 80.2182,
        "distances": {"Chaukori": 60, "Munsiyari": 130, "Dharchula": 90, "Almora": 120},
        "culture": "Known as 'Little Kashmir' with strong Tibetan Buddhist influence.",
        "unique": "Pithoragarh Fort and gateway to Kailash Mansarovar route."
    },

    # Bageshwar District
    "Bageshwar": {
        "lat": 29.8376, "lon": 79.7716,
        "distances": {"Kausani": 40, "Baijnath": 30, "Kapkot": 25, "Almora": 50},
        "culture": "Sacred temple town where Gomti and Saryu rivers meet.",
        "unique": "Bagnath Temple and Uttarakhand's most scenic valleys."
    },

    # Champawat District
    "Champawat": {
        "lat": 29.3354, "lon": 80.0786,
        "distances": {"Lohaghat": 15, "Purnagiri": 20, "Tanakpur": 75, "Pithoragarh": 60},
        "culture": "Ancient capital of Chand rulers with historic temples.",
        "unique": "Baleshwar Temple complex and mythological connections."
    },

    # Udham Singh Nagar District
    "Rudrapur": {
        "lat": 28.9734, "lon": 79.4139,
        "distances": {"Kashipur": 30, "Nanakmatta": 60, "Bajpur": 20, "Nainital": 70},
        "culture": "Agricultural hub with mixed Punjabi and Kumaoni influences.",
        "unique": "Golapar Mandir and industrial development center."
    }
}

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371  # Earth's radius
    return round(c * r, 2)

def get_distance(city1, city2):
    if city2 in cities[city1]["distances"]:
        return cities[city1]["distances"][city2]
    elif city1 in cities[city2]["distances"]:
        return cities[city2]["distances"][city1]
    else:
        lat1, lon1 = cities[city1]["lat"], cities[city1]["lon"]
        lat2, lon2 = cities[city2]["lat"], cities[city2]["lon"]
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

    start_time = time.time()
    bf_route, bf_distance, bf_all_routes = tsp_brute_force(selected_cities, start_city)
    bf_time = time.time() - start_time
    
    start_time = time.time()
    dp_route, dp_distance, _ = tsp_dp(selected_cities, start_city)
    dp_time = time.time() - start_time
    
    if not bf_route or not dp_route:
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
        "coordinates": [{"city": city, "lat": cities[city]["lat"], "lon": cities[city]["lon"]} for city in dp_route],
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
        "culture": cities[city].get("culture", "No cultural information available."),
        "unique": cities[city].get("unique", "No unique feature information available.")
    })

if __name__ == "__main__":
    app.run(debug=True)


    
