"""
Media recommendation engine
"""
from database.db import get_station_contacts

class StationDatabase:
    def __init__(self):
        self.stations = {
            "TV": {
                "Citizen TV": {"region": "National", "reach": 5000000, "cost_per_spot": 250000, "primary_audience": ["Mass Market"], "best_for": ["Brand Awareness", "Telecom"], "price_tier": "Premium"},
                "KTN": {"region": "National", "reach": 3000000, "cost_per_spot": 200000, "primary_audience": ["Professionals"], "best_for": ["News", "Financial"], "price_tier": "Premium"},
                "NTV": {"region": "National", "reach": 2800000, "cost_per_spot": 220000, "primary_audience": ["General"], "best_for": ["Entertainment", "Retail"], "price_tier": "Premium"},
                "KBC": {"region": "National", "reach": 2000000, "cost_per_spot": 150000, "primary_audience": ["Mass Market"], "best_for": ["Public Service"], "price_tier": "Standard"}
            },
            "Radio": {
                "Citizen Radio": {"region": "National", "reach": 2500000, "cost_per_spot": 90000, "primary_audience": ["General"], "best_for": ["Talk Shows"], "price_tier": "Premium"},
                "Radio Jambo": {"region": "National", "reach": 2000000, "cost_per_spot": 75000, "primary_audience": ["Youth"], "best_for": ["Youth Products"], "price_tier": "Standard"},
                "Classic 105": {"region": "National", "reach": 1500000, "cost_per_spot": 80000, "primary_audience": ["Professionals"], "best_for": ["Corporate"], "price_tier": "Premium"},
                "Baraka FM": {"region": "Coast", "reach": 600000, "cost_per_spot": 40000, "primary_audience": ["Religious"], "best_for": ["Tourism"], "price_tier": "Economy"},
                "Ramogi FM": {"region": "Western", "reach": 850000, "cost_per_spot": 35000, "primary_audience": ["Luo Community"], "best_for": ["Agriculture"], "price_tier": "Economy"},
                "Inooro FM": {"region": "Central", "reach": 1200000, "cost_per_spot": 45000, "primary_audience": ["Kikuyu Community"], "best_for": ["Agriculture"], "price_tier": "Standard"}
            }
        }
    
    def get_stations_by_region(self, region_type):
        filtered = {"TV": [], "Radio": []}
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                if region_type == "National" and info["region"] == "National":
                    filtered[media_type].append({"name": name, **info})
                elif region_type == "Local" and info["region"] != "National":
                    filtered[media_type].append({"name": name, **info})
                elif region_type == "Both":
                    filtered[media_type].append({"name": name, **info})
        return filtered
    
    def get_all_local_areas(self):
        return ["Coast Region (Mombasa)", "Western Region (Kisumu)", "Central Region (Nyeri)"]
    
    def get_all_stations_with_contacts(self):
        result = []
        for media_type, stations in self.stations.items():
            for name, info in stations.items():
                contacts = get_station_contacts(name)
                result.append({"name": name, "media_type": media_type, "region": info["region"], "reach": info["reach"], "price_tier": info["price_tier"], "contacts": contacts})
        return result

class MediaRecommendationEngine:
    def __init__(self):
        self.station_db = StationDatabase()
    
    def recommend_stations(self, campaign_goal, budget, duration_days, target_audience, region_type, selected_area=None):
        available = self.station_db.get_stations_by_region(region_type)
        recommendations = []
        for media_type, stations in available.items():
            for station in stations:
                score = 0
                if campaign_goal in station.get("best_for", []):
                    score += 30
                if target_audience in station.get("primary_audience", []):
                    score += 30
                if station["price_tier"] == "Economy" and budget < 300000:
                    score += 20
                elif station["price_tier"] == "Standard" and 200000 <= budget <= 600000:
                    score += 20
                elif station["price_tier"] == "Premium" and budget > 500000:
                    score += 20
                if score > 20:
                    max_spots = int(budget / station["cost_per_spot"]) if station["cost_per_spot"] > 0 else 0
                    recommendations.append({
                        "station_name": station["name"],
                        "media_type": media_type,
                        "reach": station["reach"],
                        "cost_per_spot": station["cost_per_spot"],
                        "recommended_spots": min(max_spots, 7 if duration_days <= 7 else 14),
                        "price_tier": station["price_tier"],
                        "score": score
                    })
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:5]
