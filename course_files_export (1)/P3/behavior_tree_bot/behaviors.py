import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def attack_best_neutral_planet(state):
    # list of owned planets, descending from number of ships
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True))
    # list of neutral planets, descending from growth rate
    neutral_planets = iter(sorted(state.neutral_planets(), key=lambda p: p.growth_rate, reverse=True))
    # ships the most productive neutral planet has
    target = neutral_planets[0]
    target_strength = target.num_ships
    # ships that have been sent to attack this planet
    sent_strength = 0

    available_ships = 0
    for i in my_planets:
        available_ships += my_planets[i].num_ships - 1
    if available_ships < target_strength:
        return(False)

    index = 0
    ships_to_send = 0
    while sent_strength < target_strength:
        if not index in range(len(my_planets)):
            index = 0
        
        if(my_planets[index].num_ships / 2 > target_strength - sent_strength + 1):  # if half the current ship's planets is more than enough
            ships_to_send = target_strength - sent_strength + 1                     # send the minimum required to take the planet
        elif my_planets[index].num_ships == 1:                                      # do not have the ships required to take planet
            return(False)                                                           # ideally should never run
        else:                                                                       # else
            ships_to_send = my_planets[index].num_ships / 2                         # send half the planet's strength
        issue_order(state, my_planets[index].id, target.id, ships_to_send)
        sent_strength += ships_to_send

        index += 1
    return True