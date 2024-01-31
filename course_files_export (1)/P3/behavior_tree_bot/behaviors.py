import logging, sys
sys.path.insert(0, '../')
from planet_wars import issue_order
from collections import namedtuple





# ====================================
# ========== Constants/Data ==========
# ====================================

ValuedPlanet = namedtuple('PlanetRank', ['planet', 'value'])
DISTANCE_FACTOR = 5
THRESHOLD_FACTOR = 5
ATTACK_BUFFER = 5





# =============================
# ========== Actions ==========
# =============================

# all planets over a certain threshold send ships to all planets, sending more ships to more valuable planets
def uniformSafeSpread(state):
    try:
        readyPlanets = [planet for planet in state.my_planets() if planet.num_ships > planet.growth_rate * (THRESHOLD_FACTOR + 1)]
        targetPlanets = getAllPlanets(state)

        for source in readyPlanets:
            for target in targetPlanets:
                shipsAvailable = source.num_ships - source.growth_rate * (THRESHOLD_FACTOR + 1)
                if shipsAvailable > 1:
                    issue_order(state, source.ID, target.ID, shipsAvailable / 2)
        return True
    except Exception as e:
        logging.exception("Error in uniformSafeSpread: %s", str(e))
        return False

def aggressiveSpread(state):
    try:
        myPlanets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
        targetPlanets = sorted(state.not_my_planets(), key=lambda p: p.num_ships)

        for source in myPlanets:
            for target in targetPlanets:
                strength = target.num_ships
                if target.owner == 2:
                    strength += target.growth_rate * state.distance(source.ID, target.ID)

                if source.num_ships > strength + ATTACK_BUFFER:
                    issue_order(state, source.ID, target.ID, strength + ATTACK_BUFFER)

        return True
    except Exception as e:
        logging.exception("Error in aggressiveSpread: %s", str(e))
        return False

def reinforce(state):
    try:
        readyPlanets = [planet for planet in state.my_planets() if planet.num_ships > planet.growth_rate * (THRESHOLD_FACTOR + 1)]
        targetPlanets = findUnderdefended(state)

        for source in readyPlanets:
            for target in targetPlanets:
                shipsNeeded = target.growth_rate * THRESHOLD_FACTOR - target.num_ships
                if shipsNeeded > 0:
                    shipsSent = min(source.num_ships - source.growth_rate * (THRESHOLD_FACTOR + 1), shipsNeeded)
                    issue_order(state, source.ID, target.ID, shipsSent)

        return True
    except Exception as e:
        logging.exception("Error in reinforce: %s", str(e))
        return False





# ======================================
# ========== Helper Functions ==========
# ======================================

# returns a list of all player planets that are underdefended, defined as growth_rate * threshold_factor
def findUnderdefended(state) :
    planets = []
    allPlanets = sorted(state.my_planets(), key=lambda p: p.growth_rate, reverse=True)

    for i in allPlanets :
        if i.num_ships < i.growth_rate * THRESHOLD_FACTOR :
            planets.append(i)

    return(planets)





# returns a list of all non-player planets, sorted by rank, which is growth_rate / num_ships
def getAllPlanets(state) :
    planets = []
    valuedPlanets = []
    allNeutral = state.neutral_planets()
    allEnemy = state.enemy_planets()

    for i in allNeutral : 
        valuedPlanets.append(ValuedPlanet(i, i.growth_rate / i.num_ships))
    for j in allEnemy : 
        valuedPlanets.append(ValuedPlanet(j, j.growth_rate / (j.num_ships + (j.growth_rate * DISTANCE_FACTOR))))

    valuedPlanets = sorted(valuedPlanets, key=lambda p: p.value, reverse=True)
    for k in valuedPlanets :
        planets.append(k.planet)

    return(planets)





# returns the amount of ships available, based on growth rate * threshold factor + 1
def musterNumbers(state) :
    planets = musterPlanets(state)
    ships = 0

    for i in planets :
        ships += i.num_ships - (i.growth_rate * (THRESHOLD_FACTOR + 1))

    return(ships)





# returns the planets with excess ships
def musterPlanets(state) :
    planets = []
    allPlanets = state.my_planets()

    for i in allPlanets :
        if i.num_ships >= i.growth_rate * (THRESHOLD_FACTOR + 1) :
            planets.append(i)

    return(planets)





# returns the number of ships going to a given planet
def shipsGoingTo(state, planet) :
    fleets = state.my_fleets()
    ships = 0

    for i in fleets :
        if i.destination_planet == planet :
            ships += i.num_ships

    return(ships)