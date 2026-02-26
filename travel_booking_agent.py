"""Personalized travel and booking assistant.

This module provides a small, self-contained agent that recommends flights,
hotels, and amenities based on user personalization and trip goals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(frozen=True)
class UserProfile:
    name: str
    preferred_airlines: List[str] = field(default_factory=list)
    seat_preference: str = "economy"
    budget_level: str = "medium"  # low, medium, high
    amenity_preferences: List[str] = field(default_factory=list)
    hotel_style_preferences: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TripRequest:
    origin: str
    destination: str
    goal: str  # e.g. relaxation, business, adventure
    nights: int
    max_budget: int


@dataclass(frozen=True)
class FlightOption:
    airline: str
    origin: str
    destination: str
    cabin: str
    price: int
    duration_hours: float
    tags: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class HotelOption:
    name: str
    location: str
    nightly_price: int
    style: str
    amenities: List[str] = field(default_factory=list)


class TravelBookingAgent:
    """Recommends flights and hotels from in-memory catalogs.

    Replace in-memory data with API integrations to connect this to production
    booking systems.
    """

    def __init__(self, flights: Iterable[FlightOption], hotels: Iterable[HotelOption]) -> None:
        self._flights = list(flights)
        self._hotels = list(hotels)

    def recommend_flights(self, profile: UserProfile, trip: TripRequest, limit: int = 3) -> List[FlightOption]:
        candidates = [
            f
            for f in self._flights
            if f.price <= trip.max_budget
            and f.origin.lower() == trip.origin.lower()
            and f.destination.lower() == trip.destination.lower()
        ]
        ranked = sorted(candidates, key=lambda f: self._flight_score(profile, trip, f), reverse=True)
        return ranked[:limit]

    def recommend_hotels(self, profile: UserProfile, trip: TripRequest, limit: int = 3) -> List[HotelOption]:
        total_budget_per_night = max(trip.max_budget // max(trip.nights, 1), 1)
        candidates = [h for h in self._hotels if h.nightly_price <= total_budget_per_night]
        ranked = sorted(candidates, key=lambda h: self._hotel_score(profile, trip, h), reverse=True)
        return ranked[:limit]

    def suggest_amenities(self, profile: UserProfile, trip: TripRequest) -> List[str]:
        base_by_goal = {
            "relaxation": ["spa", "pool", "late checkout"],
            "business": ["high-speed wifi", "workspace", "airport shuttle"],
            "adventure": ["gear storage", "guided tours", "trail transfer"],
        }
        amenities = base_by_goal.get(trip.goal.lower(), ["wifi", "breakfast"])
        personalized = list(dict.fromkeys(profile.amenity_preferences + amenities))
        return personalized

    def _flight_score(self, profile: UserProfile, trip: TripRequest, option: FlightOption) -> float:
        score = 100.0
        score -= option.price / 25
        score -= option.duration_hours * 2

        if option.airline in profile.preferred_airlines:
            score += 12
        if option.cabin.lower() == profile.seat_preference.lower():
            score += 10
        if trip.goal.lower() in (tag.lower() for tag in option.tags):
            score += 6
        if profile.budget_level == "low" and option.price < trip.max_budget * 0.75:
            score += 6
        if profile.budget_level == "high" and option.cabin.lower() in {"business", "first"}:
            score += 5

        return score

    def _hotel_score(self, profile: UserProfile, trip: TripRequest, option: HotelOption) -> float:
        score = 100.0
        score -= option.nightly_price / 10

        if option.style.lower() in [style.lower() for style in profile.hotel_style_preferences]:
            score += 10

        amenity_overlap = set(map(str.lower, option.amenities)).intersection(
            set(map(str.lower, profile.amenity_preferences))
        )
        score += len(amenity_overlap) * 5

        goal_bonus_map = {
            "relaxation": {"spa", "pool", "wellness"},
            "business": {"wifi", "workspace", "conference"},
            "adventure": {"tour desk", "gear storage", "transfer"},
        }
        goal_amenities = goal_bonus_map.get(trip.goal.lower(), set())
        goal_overlap = set(map(str.lower, option.amenities)).intersection(goal_amenities)
        score += len(goal_overlap) * 3

        return score


def sample_agent() -> TravelBookingAgent:
    flights = [
        FlightOption("SkyWays", "NYC", "BCN", "economy", 680, 8.2, ["relaxation", "city"]),
        FlightOption("Global Air", "NYC", "BCN", "business", 1240, 8.0, ["business", "city"]),
        FlightOption("BlueJet", "NYC", "BCN", "economy", 540, 10.1, ["budget", "adventure"]),
        FlightOption("AeroLux", "NYC", "BCN", "premium economy", 890, 8.6, ["comfort", "relaxation"]),
    ]

    hotels = [
        HotelOption("Calma Retreat", "Barcelona Beach", 190, "resort", ["spa", "pool", "wifi"]),
        HotelOption("Urban WorkHub", "City Center", 165, "business", ["wifi", "workspace", "conference"]),
        HotelOption("Trail & Tile Inn", "Old Quarter", 120, "boutique", ["tour desk", "gear storage", "breakfast"]),
        HotelOption("Vista Grand", "Eixample", 220, "luxury", ["pool", "wellness", "airport shuttle"]),
    ]

    return TravelBookingAgent(flights=flights, hotels=hotels)


def build_personalized_plan(profile: UserProfile, trip: TripRequest) -> dict:
    agent = sample_agent()
    return {
        "flights": agent.recommend_flights(profile, trip),
        "hotels": agent.recommend_hotels(profile, trip),
        "amenities": agent.suggest_amenities(profile, trip),
    }


if __name__ == "__main__":
    user = UserProfile(
        name="Alex",
        preferred_airlines=["SkyWays", "AeroLux"],
        seat_preference="economy",
        budget_level="medium",
        amenity_preferences=["wifi", "spa", "pool"],
        hotel_style_preferences=["resort", "boutique"],
    )
    trip_request = TripRequest(
        origin="NYC",
        destination="BCN",
        goal="relaxation",
        nights=5,
        max_budget=1000,
    )

    plan = build_personalized_plan(user, trip_request)
    print("Top flight recommendations:")
    for flight in plan["flights"]:
        print(
            f"- {flight.airline} | {flight.origin}->{flight.destination} | "
            f"{flight.cabin} | ${flight.price} | {flight.duration_hours}h"
        )

    print("\nTop hotel recommendations:")
    for hotel in plan["hotels"]:
        print(f"- {hotel.name} | {hotel.style} | ${hotel.nightly_price}/night")

    print("\nSuggested amenities:")
    for amenity in plan["amenities"]:
        print(f"- {amenity}")
