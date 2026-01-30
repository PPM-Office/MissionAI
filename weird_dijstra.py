import heapq
import requests
from dataclasses import dataclass
from geopy.geocoders import Nominatim
import re

class Location:
    def __init__(self, address, can_switch=True, can_be_alone=False):
        self.address = address
        self.can_switch = can_switch
        self.can_be_alone = can_be_alone
        self.geolocator = Nominatim(user_agent="osrm_example")

    def _fallback_addresses(self):
        parts = self.address.split(",")
        fallbacks = []

        if len(parts) >= 3:
            fallbacks.append(self.address)                  # full
            fallbacks.append(", ".join(parts[1:]))          # city, state
            fallbacks.append(", ".join(parts[2:]))             # state
        else:
            fallbacks.append(self.address)

        # hard-coded last resorts
        fallbacks.append("Broomall, PA, USA")

        return list(dict.fromkeys(fallbacks))  # remove dups


    def coords(self):
        if self.address in GEOCODE_CACHE:
            return GEOCODE_CACHE[self.address]
        
        loc = self.geolocator.geocode(self.address, timeout=10, exactly_one=True)
        
        if not loc:
            for addr in self._fallback_addresses():
                loc = self.geolocator.geocode(addr, timeout=10, exactly_one=True)
                if loc:
                    coords = (loc.longitude, loc.latitude)
                    GEOCODE_CACHE[self.address] = coords
                    print(f"📍 Approximated '{self.address}' → '{addr}'")
                    return coords
        else:
            coords = (loc.longitude, loc.latitude)
            GEOCODE_CACHE[self.address] = coords
            return coords

        print(f"❌ Could not geocode anything for {self.address}")
        return None
    
class Missionary:
    def __init__(self, email, curArea, destination):
        self.email = email
        self.curArea = curArea
        self.destination = destination

class Vehicle:
    def __init__(self, vid, capacity, curArea, destination):
        self.id = vid
        self.capacity = capacity
        self.curArea = curArea
        self.destination = destination

GEOCODE_CACHE = {}
DIST_CACHE = {}

def vehicle_distance(locA, locB):
    key = (locA.address, locB.address)
    if key in DIST_CACHE:
        return DIST_CACHE[key]

    lon1, lat1 = locA.coords()
    lon2, lat2 = locB.coords()

    url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    data = requests.get(url).json()

    d = data["routes"][0]["distance"] / 1000
    DIST_CACHE[key] = d
    return d

@dataclass(frozen=True)
class State:
    vehicle_pos: tuple
    vehicle_loads: tuple
    missionary_pos: tuple

def valid_grouping(state, vehicles, locations):
    # --- Check locations ---
    for loc in locations:
        count = sum(
            1 for p in state.missionary_pos if p == loc.address
        )
        if count == 1 and not loc.can_be_alone:
            return False

    # --- Check vehicles ---
    for vid, load in enumerate(state.vehicle_loads):
        if len(load) == 1:
            return False

    return True

def neighbors(state, vehicles, missionaries, locations):
    out = []
    for vid, vpos in enumerate(state.vehicle_pos):
        for mid, mpos in enumerate(state.missionary_pos):

            # missionary at same location as vehicle
            if mpos == vpos and len(state.vehicle_loads[vid]) < vehicles[vid].capacity:

                loads = list(state.vehicle_loads)
                new_load = set(loads[vid])
                new_load.add(mid)

                # 🚫 no solo missionary vehicle
                if len(new_load) == 1:
                    continue

                loads[vid] = frozenset(new_load)

                new_mpos = list(state.missionary_pos)
                new_mpos[mid] = f"IN:{vid}"

                new_state = State(
                    vehicle_pos=state.vehicle_pos,
                    vehicle_loads=tuple(loads),
                    missionary_pos=tuple(new_mpos)
                )

                if valid_grouping(new_state, vehicles, locations):
                    out.append((new_state, 0))
                    
    for vid, vpos in enumerate(state.vehicle_pos):

        # --- Boarding ---

        # 🚫 Vehicle cannot move unless it has >= 2 missionaries
        if len(state.vehicle_loads[vid]) < 2:
            continue

        for loc in locations:
            if loc.address == vpos:
                continue

            new_vpos = list(state.vehicle_pos)
            new_vpos[vid] = loc.address

            new_mpos = list(state.missionary_pos)
            new_loads = list(state.vehicle_loads)

            for mid in new_loads[vid]:
                new_mpos[mid] = f"IN:{vid}"

            new_state = State(
                vehicle_pos=tuple(new_vpos),
                vehicle_loads=tuple(new_loads),
                missionary_pos=tuple(new_mpos)
            )

            if valid_grouping(new_state, vehicles, locations):
                cost = vehicle_distance(
                    next(l for l in locations if l.address == vpos),
                    loc
                )
                out.append((new_state, cost))

        # Transfers
        here = next(l for l in locations if l.address == vpos)
        if here.can_switch:
            for mid in state.vehicle_loads[vid]:
                for v2 in range(len(vehicles)):
                    if v2 == vid:
                        continue
                    if len(state.vehicle_loads[v2]) < vehicles[v2].capacity:
                        loads = list(state.vehicle_loads)
                        new_load_v1 = loads[vid] - {mid}
                        new_load_v2 = loads[v2] | {mid}

                        # 🚫 Cannot create a solo missionary vehicle
                        if len(new_load_v1) == 1 or len(new_load_v2) == 1:
                            continue

                        loads[vid] = frozenset(new_load_v1)
                        loads[v2] = frozenset(new_load_v2)


                        new_state = State(
                            vehicle_pos=state.vehicle_pos,
                            vehicle_loads=tuple(loads),
                            missionary_pos=state.missionary_pos
                        )

                        if valid_grouping(new_state, vehicles, locations):
                            out.append((new_state, 0))
    return out

def is_goal(state, vehicles, missionaries):
    for i, v in enumerate(vehicles):
        if state.vehicle_pos[i] != v.destination:
            return False
    for i, m in enumerate(missionaries):
        if state.missionary_pos[i] != m.destination:
            return False
    return True

def heuristic(state, vehicles, locations):
    h = 0
    for i, v in enumerate(vehicles):
        if state.vehicle_pos[i] != v.destination:
            h += vehicle_distance(
                next(l for l in locations if l.address == state.vehicle_pos[i]),
                next(l for l in locations if l.address == v.destination)
            )
    return h

def solve(vehicles, missionaries, locations):
    start = State(
        vehicle_pos=tuple(v.curArea for v in vehicles),
        vehicle_loads=tuple(frozenset() for _ in vehicles),
        missionary_pos=tuple(m.curArea for m in missionaries)
    )

    pq = [(0 + heuristic(start, vehicles, locations), 0, start)]
    best = {start: 0}
    parent = {}

    while pq:
        _, cost, state = heapq.heappop(pq)

        if is_goal(state, vehicles, missionaries):
            return cost, parent, state

        for nxt, c in neighbors(state, vehicles, missionaries, locations):
            nc = cost + c
            if nxt not in best or nc < best[nxt]:
                best[nxt] = nc
                parent[nxt] = state
                heapq.heappush(
                    pq,
                    (nc + heuristic(nxt, vehicles, locations), nc, nxt)
                )

    return None

def StartThatJawn(mishList, veList, locList):
    print("🚀 Starting the missionary routing")
    # --- Solve ---
    result = solve(mishList, veList, locList)

    if result is None:
        print("❌ No valid solution found")
        return None

    total_distance, parent, goal_state = result

    print(f"✅ Solution found")
    print(f"🚗 Total vehicle distance: {total_distance:.2f} km")

    # --- Reconstruct path ---
    path = []
    cur = goal_state
    while cur in parent:
        path.append(cur)
        cur = parent[cur]
    path.append(cur)
    path.reverse()

    # --- Pretty print ---
    explain_solution(path, veList, mishList)

    return path

def explain_solution(path, vehicles, missionaries):
    print("\n--- PLAN ---\n")

    for step, state in enumerate(path):
        print(f"Step {step}:")

        for i, v in enumerate(vehicles):
            print(f"  Vehicle {v.id} at {state.vehicle_pos[i]}")
            mids = state.vehicle_loads[i]
            if mids:
                names = [missionaries[m].email for m in mids]
                print(f"    carrying: {names}")

        for i, m in enumerate(missionaries):
            pos = state.missionary_pos[i]
            if not pos.startswith("IN:"):
                print(f"  Missionary {m.email} at {pos}")

        print("")

