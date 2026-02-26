# Booking Agent

A lightweight personalized travel and booking agent that recommends:

- Flights (based on preferred airlines, budget, seat preference, and trip goal)
- Hotels (based on budget per night, style, and amenity overlap)
- Trip amenities (based on user taste + goal)

## Run demo

```bash
python travel_booking_agent.py
```

## Run tests

```bash
python -m unittest discover -s tests
```

## Customization notes

The current implementation uses in-memory sample inventory. To productionize:

1. Replace `sample_agent()` catalog data with provider APIs (GDS/NDC, OTAs, hotel APIs).
2. Add user profile persistence.
3. Add ranking feedback loops from user interactions.
