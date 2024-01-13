import requests

# Sostituisci con la tua chiave API
api_key = "5b3ce3597851110001cf62481712b776e66f42019ffa0d5506e9a2d4"


class OpenRouteService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
            "Authorization": f"Bearer {api_key}"
        }

    def get_route_distance(self, start_coordinates, end_coordinates):
        params = {
            "coordinates": [start_coordinates, end_coordinates],
            "format": "geojson",
            "profile": "driving-car"
        }

        try:
            response = requests.post(self.base_url, json=params, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            if "features" in data:
                features = data["features"]
                if features:
                    properties = features[0]["properties"]["summary"]
                    distance = properties.get("distance", 0)
                    return int(distance)

        except requests.exceptions.RequestException as e:
            print(f"Errore durante la richiesta: {e}")

        return None  # Ritorna None in caso di errore o mancanza di dati
