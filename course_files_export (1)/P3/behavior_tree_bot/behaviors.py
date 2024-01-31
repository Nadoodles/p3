import logging, sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import namedtuple





# ====================================
# ========== Constants/Data ==========
# ====================================

ValuedPlanet = namedtuple('PlanetRank', ['planet', 'value'])
DISTANCE_FACTOR = 5
THRESHOLD_FACTOR = 4
ATTACK_BUFFER = 5


# Actions

def uniformSafeSpread(state):
    try:
        readyPlanets = musterPlanets(state)
        targetPlanets = getAllPlanets(state)

        for x in readyPlanets:
            shipsAvailable = x.num_ships - (x.growth_rate * (THRESHOLD_FACTOR + 1))
            div = sum(range(1, len(targetPlanets) + 1))
            
            for y, targetPlanet in enumerate(targetPlanets):
                if shipsAvailable > len(targetPlanets) - y:
                    shipsToSend = shipsAvailable * ((len(targetPlanets) - y) / div)
                    if (targetPlanet.owner == 0 and shipsToSend > targetPlanet.num_ships) or targetPlanet.owner == 2:
                        issue_order(state, x.ID, targetPlanet.ID, shipsToSend)
        return True
    except Exception as e:
        logging.exception("Error in uniformSafeSpread: %s", str(e))
        return False

def aggressiveSpread(state):
    try:
        myPlanets = state.my_planets()
        targetPlanets = sorted(state.not_my_planets(), key=lambda p: (p.num_ships, -p.growth_rate, state.distance(myPlanets[0].ID, p.ID)))

        index1 = 0  # owned planets
        index2 = 0  # target planets
        while index1 < len(myPlanets) and index2 < len(targetPlanets):
            strength = targetPlanets[index2].num_ships - shipsGoingTo(state, targetPlanets[index2])

            if targetPlanets[index2].owner == 2:
                strength += targetPlanets[index2].growth_rate * state.distance(myPlanets[index1].ID, targetPlanets[index2].ID)

            while index2 < len(targetPlanets) and myPlanets[index1].num_ships > strength + ATTACK_BUFFER and strength > 0:
                strength = targetPlanets[index2].num_ships - shipsGoingTo(state, targetPlanets[index2])
                if targetPlanets[index2].owner == 2:
                    strength += targetPlanets[index2].growth_rate * state.distance(myPlanets[index1].ID, targetPlanets[index2].ID)

                issue_order(state, myPlanets[index1].ID, targetPlanets[index2].ID, strength + ATTACK_BUFFER)
                index2 += 1

            index1 += 1

        return True
    except Exception as e:
        logging.exception("Error in aggressiveSpread: %s", str(e))
        return False

def reinforce(state):
    readyPlanets = musterPlanets(state)
    readyNumbers = musterNumbers(state)
    targetPlanets = findUnderdefended(state)
    index1 = 0
    index2 = 0
    ordersSent = 0

    while index1 < len(readyPlanets) and index2 < len(targetPlanets) and readyNumbers > 0:
        i1Planet = readyPlanets[index1]
        i2Planet = targetPlanets[index2]
        i1PNumber = i1Planet.num_ships - i1Planet.growth_rate * (THRESHOLD_FACTOR + 1)
        i2PNumber = (i2Planet.growth_rate * THRESHOLD_FACTOR) - i2Planet.num_ships

        if shipsGoingTo(state, i2Planet.ID) + i2Planet.num_ships >= i2Planet.growth_rate * THRESHOLD_FACTOR:
            index2 += 1
        else:
            if i1Planet.num_ships <= i1Planet.growth_rate * (THRESHOLD_FACTOR + 1):
                index1 += 1
            else:
                ships_to_send = min(i1PNumber, i2PNumber)
                issue_order(state, i1Planet.ID, i2Planet.ID, ships_to_send)
                readyNumbers -= ships_to_send
                index2 += 1
                ordersSent += 1

    return ordersSent > 0

# Helper Functions

def findUnderdefended(state):
    allPlanets = sorted(state.my_planets(), key=lambda p: p.growth_rate, reverse=True)
    return [planet for planet in allPlanets if planet.num_ships < planet.growth_rate * THRESHOLD_FACTOR]

def getAllPlanets(state):
    planets = []
    valuedPlanets = []

    for i in state.neutral_planets():
        valuedPlanets.append(ValuedPlanet(i, i.growth_rate / i.num_ships))
    for j in state.enemy_planets():
        valuedPlanets.append(ValuedPlanet(j, j.growth_rate / (j.num_ships + (j.growth_rate * DISTANCE_FACTOR))))

    valuedPlanets = sorted(valuedPlanets, key=lambda p: p.value, reverse=True)
    planets = [valued_planet.planet for valued_planet in valuedPlanets]

    return planets

def musterNumbers(state):
    planets = musterPlanets(state)
    return sum(i.num_ships - (i.growth_rate * (THRESHOLD_FACTOR + 1)) for i in planets)

def musterPlanets(state):
    return [planet for planet in state.my_planets() if planet.num_ships >= planet.growth_rate * (THRESHOLD_FACTOR + 1)]

def shipsGoingTo(state, planet):
    fleets = state.my_fleets()
    return sum(fleet.num_ships for fleet in fleets if fleet.destination_planet == planet)