from raw_data_storage import raw_data

class Location:
    def __init__(self, name, description, rating, image_path):
        self.name = name
        self.description = description
        self.rating =  rating
        self.image_path = image_path
class City:
    def __init__(self, name, description, locations):
        self.name = name
        self.description = description
        self.locations = locations

#Database :-
cities = [City(city[0], city[1], [Location(loc[0], loc[1], loc[2], loc[3]) for loc in city[2]])
                    for city in raw_data]