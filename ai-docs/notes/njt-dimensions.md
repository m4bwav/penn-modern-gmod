# NJ Transit concourse dimensions (area 4)

Cited (Wikipedia, "New York Penn Station", Station layout, read 2026-11-27, https://en.wikipedia.org/wiki/New_York_Penn_Station):
- The Amtrak and NJ Transit concourses are on the first level below the street, so the NJ Transit floor is at the Amtrak floor height (AZ).
- The NJ Transit concourse is at the east end of the block, toward Seventh Avenue.

Derived (judged from the refs in refs/photos/, logged in refs/SOURCES.md):
- NJ_Transit_concourse_New_York_Penn_Station_November_27_2023.jpg (CC0): a long hall with a raised barrel vault down its middle carried on white arched trusses, flared cream columns at the vault edges, cream marble walls with tan stripes and a brown dado, track gates (gold-framed doors, black TRACK signs, screens) along one side, a pink-and-grey diamond granite floor with small black squares.
- NJ_Transit_Ticket_Counter_Penn_Station_NY.jpg (CC0): ticket windows under a black "NJ TRANSIT Tickets" fascia with numbered windows, cream counter, glass.
- Sizes: hall 60 ft wide, 200 ft modelled; side ceilings 12 ft; vault 23 ft wide, crown 20 ft; trusses every 10 ft; columns 3 ft, capital 8 ft, every 40 ft.
- Simplifications: one 20 ft opening from the Amtrak hall's east wall (the real concourses join along several passages); the gates are a painted band, not stairs to the tracks yet (area 5); the vault crown reaches street level (z 0), to be checked against area 6's street.
- Modelled in build_vmf.py njt(): x 4944..7344, y -1800..-1080 u, floor z -240.
