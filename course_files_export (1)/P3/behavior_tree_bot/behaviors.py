import sys
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
def uniformSafeSpread(state) :
    readyPlanets = musterPlanets(state)
    targetPlanets = getAllPlanets(state)

    for x in readyPlanets :
        for y in targetPlanets :
            shipsAvailable = x.num_ships - (x.growth_rate * (THRESHOLD_FACTOR + 1))
            if shipsAvailable > 1 :
                issue_order(state, x, y, shipsAvailable / 2)
    
    return(True)





# send ships to the least defended planets, regardless of ships on owned planets
def aggressiveSpread(state) :
    myPlanets = state.my_planets()
    neutralPlanets = state.neutral_planets()
    enemyPlanets = state.enemy_planets()
    targetPlanets = []

    # populate the list of not-owned planets
    for i in neutralPlanets :
        targetPlanets.append[i]
    for i in enemyPlanets : 
        targetPlanets.append[i]
    targetPlanets = sorted(targetPlanets, key=lambda p: p.num_ships, reverse=False)

    index1 = 0  # owned planets
    index2 = 0  # target planets
    while index1 < len(myPlanets) and index2 < len(targetPlanets) :
        i1Planet = myPlanets[index1]
        i2Planet = targetPlanets[index2]
        strength = i2Planet.num_ships

        if i2Planet.owner == 2 :
            strength += i2Planet.growth_rate * state.distance(i1Planet, i2Planet)

        while index2 < len(targetPlanets) and i1Planet.num_ships > strength + ATTACK_BUFFER :
            issue_order(state, i1Planet, i2Planet, strength + ATTACK_BUFFER)
            index2 += 1

        index += 1

    return(True)






# ensure all owned planets are above a certain threshold
def reinforce(state) :
    readyPlanets = musterPlanets(state)
    readyNumbers = musterNumbers(state)
    targetPlanets = findUnderdefended(state)
    index1 = 0  # readyPlanets
    index2 = 0  # targetPlanets
    i1Planet = None
    i2Planet = None

    while index1 < len(readyPlanets) and index2 < len(targetPlanets) and readyNumbers > 0 :
        i1Planet = readyPlanets[index1]
        i2Planet = targetPlanets[index2]
        i1PNumber = i1Planet.num_ships - i1Planet.growth_rate * (THRESHOLD_FACTOR + 1)  # ships this planet has extra above the threshold
        i2PNumber = (i2Planet.growth_rate * THRESHOLD_FACTOR) - i2Planet.num_ships      # ships this planet needs to be considered well defended

        if shipsGoingTo(state, i2Planet.ID) + i2Planet.num_ships >= i2Planet.growth_rate * THRESHOLD_FACTOR :
            index2 += 1                     # planet has enough ships either already on or going to planet
        else :
            if i1Planet.num_ships <= i1Planet.growth_rate * (THRESHOLD_FACTOR + 1) :
                index1 += 1                 # planet doesnt have enough ships to send anything
            else :
                if i1PNumber < i2PNumber :  # planet doesnt have enough to reinforce planet fully
                    issue_order(state, i1Planet, i2Planet, i1PNumber)
                    readyNumbers -= i1PNumber
                else :                      # planet sends minimum ships to defend planet
                    issue_order(state, i1Planet, i2Planet, i2PNumber)
                    readyNumbers -= i2PNumber
                    index2 += 1

    return(True)





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
    allNeutral = state.neutral_planets
    allEnemy = state.enemy_planets

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