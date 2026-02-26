import unittest

from travel_booking_agent import (
    FlightOption,
    HotelOption,
    TravelBookingAgent,
    TripRequest,
    UserProfile,
    build_personalized_plan,
    sample_agent,
)


class TravelBookingAgentTests(unittest.TestCase):
    def test_relaxation_plan_prioritizes_spa_pool(self):
        profile = UserProfile(
            name="Jamie",
            preferred_airlines=["SkyWays"],
            seat_preference="economy",
            budget_level="medium",
            amenity_preferences=["spa", "pool"],
            hotel_style_preferences=["resort"],
        )
        trip = TripRequest("NYC", "BCN", "relaxation", nights=4, max_budget=900)

        plan = build_personalized_plan(profile, trip)

        self.assertGreaterEqual(len(plan["flights"]), 1)
        self.assertGreaterEqual(len(plan["hotels"]), 1)
        self.assertIn("spa", [a.lower() for a in plan["amenities"]])

    def test_business_goal_returns_business_amenities(self):
        agent = sample_agent()
        profile = UserProfile(name="Taylor", amenity_preferences=["breakfast"])
        trip = TripRequest("NYC", "BCN", "business", nights=3, max_budget=1500)

        amenities = [a.lower() for a in agent.suggest_amenities(profile, trip)]

        self.assertIn("high-speed wifi", amenities)
        self.assertIn("workspace", amenities)

    def test_recommend_flights_only_returns_requested_itinerary(self):
        agent = TravelBookingAgent(
            flights=[
                FlightOption("FastHop", "NYC", "BCN", "economy", 650, 8.5, ["city"]),
                FlightOption("CheapElsewhere", "NYC", "LAX", "economy", 120, 6.0, ["budget"]),
                FlightOption("QuickElsewhere", "BOS", "BCN", "economy", 500, 7.1, ["city"]),
            ],
            hotels=[HotelOption("Dummy Hotel", "Center", 100, "business", ["wifi"])],
        )
        profile = UserProfile(name="Casey", seat_preference="economy")
        trip = TripRequest("NYC", "BCN", "business", nights=2, max_budget=1000)

        flights = agent.recommend_flights(profile, trip, limit=5)

        self.assertEqual(len(flights), 1)
        self.assertEqual(flights[0].origin, "NYC")
        self.assertEqual(flights[0].destination, "BCN")


if __name__ == "__main__":
    unittest.main()
