import heapq
import requests
from dataclasses import dataclass
from geopy.geocoders import Nominatim

class Location:
    def __init__(self, address, state, can_switch=True, can_be_alone=False):
        self.address = address
        self.state = state
        self.can_switch = can_switch
        self.can_be_alone = can_be_alone
        self.geolocator = Nominatim(user_agent="osrm_example")

    def coords(self):
        loc = self.geolocator.geocode(self.address)
        if not loc:
            raise ValueError(f"Could not geocode {self.address}")
        return loc.longitude, loc.latitude
    
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

def no_one_alone(state, locations):
    for loc in locations:
        if loc.can_be_alone:
            continue
        count = sum(1 for p in state.missionary_pos if p == loc.address)
        if count == 1:
            return False
    return True

def neighbors(state, vehicles, missionaries, locations):
    out = []

    for vid, vpos in enumerate(state.vehicle_pos):
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

            if no_one_alone(new_state, locations):
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
                        loads[vid] = frozenset(loads[vid] - {mid})
                        loads[v2] = frozenset(loads[v2] | {mid})

                        new_state = State(
                            vehicle_pos=state.vehicle_pos,
                            vehicle_loads=tuple(loads),
                            missionary_pos=state.missionary_pos
                        )

                        if no_one_alone(new_state, locations):
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
    # --- Build locations ---
    locations = []
    loc_by_addr = {}

    for addr, state in locList:
        # Customize these rules as needed
        can_switch = True
        can_be_alone = (addr == "721 paxton hollow rd Broomall PA")

        loc = Location(
            address=addr,
            state=state,
            can_switch=can_switch,
            can_be_alone=can_be_alone
        )
        locations.append(loc)
        loc_by_addr[addr] = loc

    # --- Build missionaries ---
    missionaries = []
    for email, curArea, destination in mishList:
        missionaries.append(
            Missionary(email, curArea, destination)
        )

    # --- Build vehicles ---
    vehicles = []
    for vid, capacity, curArea, destination, _assigned in veList:
        vehicles.append(
            Vehicle(vid, capacity, curArea, destination)
        )

    # --- Solve ---
    result = solve(vehicles, missionaries, locations)

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
    explain_solution(path, vehicles, missionaries)

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

