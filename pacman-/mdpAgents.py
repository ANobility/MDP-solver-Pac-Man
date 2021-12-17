# coding=utf-8
# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

# Author WEIBO ZHAO
# Date 03/12/2021
# Knumber: k21026399

from game import Agent
from game import Actions
import api


# this class is a copy from mapAgent.py,I added copy () to it to make it faster to create maps
# It can access itself using coordinates such as (x, y)
class Grid:

    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                # Add a floating point number as the initial value of a space
                row.append(0.0)
            subgrid.append(row)

        self.grid = subgrid

    # Print the grid out.
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print
            # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                value = self.grid[self.height - (i + 1)][j]
                if value == '%':
                    # Printing "++++" is easier to observe
                    value = '++++'
                    print value,
                else:
                    value = float(value)
                    # Print a two-digit floating-point decimal
                    print '%.2f' % value,

            # A new line after each line of the grid
            print
            # A line after the grid
        print

    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    # Copy a blank map
    def copy(self):
        grid = Grid(self.width, self.height)
        for i in range(self.height):
            for j in range(self.width):
                grid.grid[i][j] = self.grid[i][j]
        return grid


class MDPAgent(Agent):

    # The constructor.

    # Set  discount factor = 0.8
    def __init__(self):
        self.dis_count = 0.8
        print "Running init!"

    # This function is run when the agent is created, and it has access
    # to state information, so we use it to build a map for the agent.
    def registerInitialState(self, state):
        print "Running registerInitialState!"

        # Make a complete map and add walls
        self.makeMap(state)
        self.addWallsToMap(state)

        self.ghosts_states = api.ghostStatesWithTimes(state)
        self.reward_map = self.map.copy()

    def final(self, state):

        print "Looks like the game just ended!"

    # Make a map by creating a grid of the right size (copy from mapAgent.py)
    def makeMap(self, state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width = self.getLayoutWidth(corners)
        self.map = Grid(width, height)

    # Set height and width (copy from mapAgent.py)
    # Functions to get the height and the width of the grid.
    #
    # We add one to the value returned by corners to switch from the
    # index (returned by corners) to the size of the grid (that damn
    # "start counting at zero" thing again).
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1

    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1

    # Functions to manipulate the map.(copy from mapAgent.py)
    #
    # Put every element in the list of wall elements into the map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')

    # Create an initialization map and logically set the initialization values for food, ghosts, capsules,
    # and blank Spaces. This method is called after each agent action to reset the map's initial value in the current
    # state
    def initialMap(self, state):

        # Find the location or status of food, capsules, and ghosts
        ghosts=[]
        for i in api.ghostStatesWithTimes(state):
            x = int(i[0][0])
            y = int(i[0][1])
            z = i[1]
            ghosts.append(((x,y),z))
        foods = api.food(state)
        capsules = api.capsules(state)

        # There is only one ghost in the smallGrid. Find the distance between the ghost and each point on the map
        min_distance_of_Ghosts = self.getDistanceToGhost(ghosts[0][0], self.ghosts_facing[0])


        # When the map is mediumClassic, there are two ghosts respectively get two ghosts to each point of the map to
        # the location, take the minimum value at the same location
        if len(ghosts) > 1:
            distance_of_ghost1 = self.getDistanceToGhost(ghosts[1][0], self.ghosts_facing[1])

            for i in range(1,min_distance_of_Ghosts.getWidth()-1):
                for j in range(1,min_distance_of_Ghosts.getHeight()-1):

                    self_value = min_distance_of_Ghosts.getValue(i, j)
                    other_value = distance_of_ghost1.getValue(i, j)
                    if self_value != other_value:
                        min_distance_of_Ghosts.setValue(i, j, min(int(other_value), int(self_value)))

        # the smallGird
        if self.reward_map.getWidth() == 7:

            for i in range(1, self.reward_map.getWidth() - 1):
                for j in range(1, self.reward_map.getHeight() - 1):
                    if self.reward_map.getValue(i, j) != '%':
                        distance_ghost = float(min_distance_of_Ghosts.getValue(i, j))
                        # Use the inverse function (Alpha/ distance from a point to the ghost +1)
                        # +1 because the distance from a point to the ghost maybe zero
                        # Alpha Is a parameter,The further away you go, the smaller the function value is.
                        # Space's alpha is 2,their initial value I set to 1
                        value = 1 - 2 / (distance_ghost + 1)
                        if (i, j) == ghosts[0][0]:
                            # A value of -5 when encountering an inedible ghost
                            value += -5
                        # When there are two foods, choose the food in the lower left corner first
                        # Food's alpha is 3
                        if len(foods) > 1:
                            if (i, j) == foods[0]:
                                value += 1 - 3 / (distance_ghost + 1)
                        else:
                            if (i, j) == foods[0]:
                                value += 1 - 3 / (distance_ghost + 1)
                        self.reward_map.setValue(i, j, value)

        # the mediumClassic
        else:
            for i in range(1, self.reward_map.getWidth() - 1):
                for j in range(1, self.reward_map.getHeight() - 1):
                    if self.reward_map.getValue(i, j) != '%':
                        distance_ghost = float(min_distance_of_Ghosts.getValue(i, j))
                        # Get the distance map of the first ghost
                        distance_ghost0 = float(
                            self.getDistanceToGhost(ghosts[0][0], self.ghosts_facing[0]).getValue(i, j))
                        # Get the distance map of the second ghost
                        distance_ghost1 = float(
                            self.getDistanceToGhost(ghosts[1][0], self.ghosts_facing[1]).getValue(i, j))

                        # Ghosts are dangerous when they have an edible time of 5 or less, because they can become
                        # dangerous at any time and Pac-Man needs to stay away from them

                        # Ghosts are more attractive when their use-time is greater than 5, as eating them earns more
                        # points, so Pac-Man will approach the ghost looking for an opportunity to eat it

                        # There are four different states, both of which are inedible (scaredTimer<=5). Both ghosts
                        # are in inedible state at the same time: Ghost 1 is inedible ghost 2 is inedible,
                        # Ghost 1 is inedible and Ghost 2 is inedible
                        if ghosts[0][1] <= 5 and ghosts[1][1] <= 5:

                            score = 0 - 1.5 / (distance_ghost + 1)
                            if (i, j) == ghosts[0][0] or (i, j) == ghosts[1][0]:
                                score += -5
                            if (i, j) in foods or (i, j) in capsules:
                                score += 2 - 12 / (distance_ghost + 1)

                        elif ghosts[1][1] > 5 and ghosts[0][1] > 5:
                            score = 2 / (distance_ghost + 1)
                            if (i, j) in foods or (i, j) in capsules:
                                score += 2 + 2 / (distance_ghost + 1)
                            if (i, j) == ghosts[0][0] or (i, j) == ghosts[1][0]:
                                score += 5

                        elif ghosts[0][1] <= 5 and ghosts[1][1] > 5:
                            score = 0 - 1.5 / (distance_ghost0 + 1) + 2 / (distance_ghost1 + 1)
                            if (i, j) in foods or (i, j) in capsules:
                                score += 2 - 12 / (distance_ghost0 + 1) + 2 / (distance_ghost1 + 1)
                            if (i, j) == ghosts[0][0]:
                                score += -5
                            if (i, j) == ghosts[1][0]:
                                score += 5
                        elif ghosts[1][1] <= 5 and ghosts[0][1] > 5:
                            score = 0 - 1.5 / (distance_ghost1 + 1) + 2 / (distance_ghost0 + 1)
                            if (i, j) in foods or (i, j) in capsules:
                                score += 2 - 12 / (distance_ghost1 + 1) + 2 / (distance_ghost0 + 1)
                            if (i, j) == ghosts[1][0]:
                                score += -5
                            if (i, j) == ghosts[0][0]:
                                score += 5
                        else:
                            score = 0

                        self.reward_map.setValue(i, j, score)

    # value iteration
    # Part of the MDP decision-making process
    # Stop updating the map when the number of iterations exceeds 50
    def update(self):
        utilities_map = self.map.copy()
        flag = 0
        while True:
            temp_map = utilities_map.copy()
            for i in range(1, self.map.getWidth() - 1):
                for j in range(1, self.map.getHeight() - 1):
                    if self.map.getValue(i, j) != '%':
                        new_value = self.reward_map.getValue(i, j) + self.dis_count * self.getNeighborMaxUtility(i, j, temp_map)
                        utilities_map.setValue(i, j, new_value)

            flag += 1

            if flag >= 50:
                break

        return utilities_map

    # Part of the MDP decision-making process
    # Get the maximum utility point around the point (x, y) on a map
    def getNeighborMaxUtility(self, x, y, a_map):
        value = []
        for point in map(lambda vector: (vector[0] + x, vector[1] + y), [(1, 0), (-1, 0), (0, 1), (0, -1)]):
            fooward = a_map.getValue(point[0], point[1])
            if fooward != '%':
                value.append(fooward)
        maxvaule = max(value)

        return maxvaule

    def getAction(self, state):
        # Gets the current ghost state, subtracting the ghost position in the previous state to get the direction the
        # ghost is facing
        self.current_ghosts_states = api.ghostStatesWithTimes(state)


        self.ghosts_facing = []
        for i in range(len(self.current_ghosts_states)):
            direction_of_ghost = (int(round(self.current_ghosts_states[i][0][0] - self.ghosts_states[i][0][0])),
                                  int(round(self.current_ghosts_states[i][0][1] - self.ghosts_states[i][0][1])))

            self.ghosts_facing.append(direction_of_ghost)

        # update ghosts states
        self.ghosts_states = self.current_ghosts_states

        self.initialMap(state)

        pacman = api.whereAmI(state)
        utilities_map = self.update()

        legal = api.legalActions(state)

        action_vectors = [Actions.directionToVector(a, 1) for a in legal]
        optic_action = max(
            map(lambda x: (float(utilities_map.getValue(x[0] + pacman[0], x[1] + pacman[1])), x),
                action_vectors))
        return api.makeMove(Actions.vectorToDirection(optic_action[1]), legal)

    # Return the true distance from each blank point on the map, because there is a greater error
    # using Manhattan distance

    # position:The ghost's current coordinates
    # direction：The current direction of the ghost

    def getDistanceToGhost(self, position, direction):
        distance_map = self.map.copy()
        distance = 0
        distance_map.setValue(position[0], position[1], distance)
        queue = [[position, direction]]
        temp_queue = []
        queried = {position: 1}
        while queue:
            distance += 1
            while queue:
                [(x, y), current_facing] = queue.pop()

                if current_facing == (0, 0):
                    valid_pos = self.sideNeighbor(x, y, current_facing)
                else:
                    valid_pos = self.sideNeighbor(x, y, current_facing)

                for (i, j) in valid_pos:
                    # If 'position's neighbors have already been queried, increment {position:} by one and select the
                    # smallest value to update
                    if (i, j) in queried:
                        if queried[(i, j)] < 2:
                            temp_queue.append([(i, j), (i - x, j - y)])

                            queried[(i, j)] += 1
                            distance_map.setValue(i, j, min(distance, distance_map.getValue(i, j)))
                    else:
                        temp_queue.append([(i, j), (i - x, j - y)])
                        queried[(i, j)] = 1
                        distance_map.setValue(i, j, distance)

                    queried[(x, y)] += 1

            queue = temp_queue
            temp_queue = []
        return distance_map


    # Returns the direction in which the ghost is facing and the points left and right of the ghost, side-by-side the
    # wall points, or (0,0) the non-wall points
    def sideNeighbor(self, x, y, direction):
        global side_neighbors
        if direction == (0, 0):
            side_neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        elif direction[0] == -1 or direction[0] == 1:
            side_neighbors = [(x, 1 + y), (x, -1 + y), (x + direction[0], y)]
        elif direction[1] == -1 or direction[1] == 1:
            side_neighbors = [(1 + x, y), (-1 + x, y), (x, y + direction[1])]

        valid_neighbor = []
        for neighbor in side_neighbors:
            if self.map.getValue(neighbor[0], neighbor[1]) != '%':
                valid_neighbor.append(neighbor)
        return valid_neighbor
