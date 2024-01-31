import logging





# ===============================
# ========== Constants ==========
# ===============================

PANIC_PLANET_THRESHOLD = 5  # if we own less than this amount of planets then be aggressive
PANIC_PLANET_FACTOR = 3     # if we own less than total planets/this amount of planets then be aggressive
NEUTRAL_PLANET_CHECK = 3    # ignore this amount of neutral planets when forgoing defense
UNDERDEFENDED_THRESHOLD = 2 # if the amount of "underdefended" planets is <= this number then ignore them
THRESHOLD_FACTOR = 5        # THIS SHOULD BE THE SAME AS THE SAME CONST IN behaviors.py





# ============================
# ========== Checks ==========
# ============================

# do we own less than the desired amount of planets
# set PROPORTION to true to check if we own less than total planets/PANIC_PLANET_FACTOR planets
# set PROPORTION to false to check if we own less than PANIC_PLANET_THRESHOLD planets
def panicCheck(state) :
    PROPORTION = True

    logging.debug('\n panic Check')
    if PROPORTION :
        return len(state.my_planets()) < (len(state.my_planets()) + len(state.not_my_planets())) / PANIC_PLANET_FACTOR
    else :
        return len(state.my_planets()) < PANIC_PLANET_THRESHOLD
    




# are there not enough neutral planets to care about them
def neutralCheck(state) :
    logging.debug('\n neutral Check')
    return len(state.neutral_planets()) >= NEUTRAL_PLANET_CHECK





# are there (enough) planets that are underdefended to consider reinforcing
def underdefendedCheck(state) :
    planets = []
    allPlanets = sorted(state.my_planets(), key=lambda p: p.growth_rate, reverse=True)

    for i in allPlanets :
        if i.num_ships + shipsGoingTo(state, i) < i.growth_rate * THRESHOLD_FACTOR :
            planets.append(i)

    logging.debug('\n undefended check')
    return len(planets) <= UNDERDEFENDED_THRESHOLD





# ======================================
# ========== Helper Functions ==========
# ======================================

# same as the one in behaviors.py
def shipsGoingTo(state, planet) :
    fleets = state.my_fleets()
    ships = 0

    for i in fleets :
        if i.destination_planet == planet :
            ships += i.num_ships

    return(ships)