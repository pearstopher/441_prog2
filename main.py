# CS441-003 Winter 2022
# Programming Assignment 2
#   (8 Queens Genetic Algorithm)
# Christopher Juncker

from random import randrange, shuffle, sample, uniform
from math import comb  # n choose k
from matplotlib import pyplot as plt
import numpy as np


# constants & configuration
ITERATIONS = 1000  # how many generations to run the program for
POPULATION_SIZE = 1000  # suggested values: 10, 100, 500, 1000, etc.
ROWS = COLS = QUEENS = 8  # increase if you want to experiment with a bigger chess board
MUTATION_PERCENT = 1  # percent chance that a child's gene will be mutated
UNIQUE_ROWS = True  # enforce unique values per row (unique values per column always enforced)
CROSSOVER = True  # u can turn off crossover just for fun (will be mutation only)


###########################################################################################################
#
# Initial Population: The initialization contains a randomly distributed population. Lower population size
# will lead to lots of time in computation of approximate solution. And higher value will cause internal
# iterations to increase. Therefore choose the population size carefully. Suggestion: try experimenting
# with population sizes of 10, 100, 500, 1000, etc.
#
###########################################################################################################


class Position:
    def __init__(self, position=None):
        self.position = position if position else generate_position()
        self.fitness = generate_fitness(self.position)


def initial_population():
    population = []
    for _ in range(POPULATION_SIZE):
        population.append(Position())
    return population


def generate_position():
    return generate_unique_rows() if UNIQUE_ROWS \
        else generate_random()


def generate_unique_rows():
    position = list(range(ROWS))
    shuffle(position)
    return position


def generate_random():
    position = []
    for _ in range(ROWS):
        position.append(randrange(0, COLS))
    return position


###########################################################################################################
#
# Selection of parents: Just as evolutionary biology requires two parents to undergo meiosis, so does GA.
# Therefore there is need to select two parents which determine a child; this selection should be done in
# proportion to the ???fitness??? of each parent.
#
###########################################################################################################

def generate_fitness(position):
    # the fitness is the difference between the current number of mutually attacking queens and the
    #   theoretical maximum

    # Need to ensure that the minimum fitness value is at least 1 for small population sizes
    #   otherwise a population can have a total of 0 fitness which will cause range errors
    return max_mutually_attacking() - mutually_attacking(position) + 1  # 1 = fitness_offset


def max_mutually_attacking():
    # the theoretical maximum number of mutually attacking queens is (QUEENS choose 2)
    return comb(QUEENS, 2)


def mutually_attacking(position):
    count = 0
    # loop through each column from left to right
    # count queens attacking current queen from the right
    for i in range(QUEENS):
        for j in range(i + 1, QUEENS):
            if attacking(i, j, position[i], position[j]):
                count += 1
    return count


def attacking(col1, col2, row1, row2):
    return attacking_diagonal(col1, col2, row1, row2) \
            or attacking_horizontal(row1, row2)


def attacking_diagonal(col1, col2, row1, row2):
    # (row + column) is equal along secondary diagonal
    # flip row numbers to compare principal diagonal
    return (row1 + col1) == (row2 + col2) or \
           ((ROWS - 1 - row1) + col1) == ((ROWS - 1 - row2) + col2)


def attacking_horizontal(row1, row2):
    return row1 == row2


def select_parents(population):
    total_fitness = total_population_fitness(population)
    parent1_val = randrange(0, total_fitness)
    parent2_val = randrange(0, total_fitness)

    parent1 = parent2 = population[0]  # warning: parents might be referenced before assignment

    counter = 0
    for i in range(len(population)):
        if counter >= parent1_val:
            parent1 = population[i]
            break
        counter += population[i].fitness

    counter = 0
    for i in range(len(population)):
        if counter >= parent2_val:
            parent2 = population[i]
            counter += population[i].fitness
            break
        counter += population[i].fitness

    return parent1, parent2


def total_population_fitness(population):
    total = 0
    for i in population:
        total += i.fitness
    return total


def average_population_fitness(population):
    return total_population_fitness(population) / \
           ((max_mutually_attacking() + 1) * POPULATION_SIZE)  # 1 = fitness_offset


###########################################################################################################
#
# CrossOver: Once parents having high fitness are selected, crossover essentially marks the recombining
# of genetic materials / chromosomes to produce a healthy offspring. Pick a random spot for crossover,
# and breed two new children (with fitness computed).
#
###########################################################################################################

def crossover(parent1, parent2):
    if not CROSSOVER:
        return Position(mutate(parent1.position)), Position(mutate(parent2.position))

    child1, child2 = crossover_unique(parent1, parent2) if UNIQUE_ROWS \
        else crossover_random(parent1, parent2)

    child1 = mutate(child1)
    child2 = mutate(child2)
    return Position(child1), Position(child2)


def crossover_unique(parent1, parent2):
    random_location = randrange(1, COLS - 1)
    child1 = []
    child2 = []

    # fill child1's head with sequential values from parent2
    for i in range(0, COLS):
        for j in range(0, random_location):
            if parent2.position[i] == parent1.position[j]:
                child1.append(parent2.position[i])
    # fill child1's tail with original values
    for i in range(random_location, COLS):
        child1.append(parent1.position[i])

    # fill child2's head with original values
    for i in range(0, random_location):
        child2.append(parent2.position[i])
    # fill child2's tail with sequential values from parent1
    for i in range(0, COLS):
        for j in range(random_location, COLS):
            if parent1.position[i] == parent2.position[j]:
                child2.append(parent1.position[i])

    return child1, child2


def crossover_random(parent1, parent2):
    random_location = randrange(0, COLS)
    child1 = child2 = []
    for i in range(0, random_location):
        child1.append(parent1.position[i])
        child2.append(parent2.position[i])
    for i in range(random_location, COLS):
        child1.append(parent2.position[i])
        child2.append(parent1.position[i])

    return child1, child2


###########################################################################################################
#
# Mutation: Mutation may or may not occur. In case mutation occurs, it forces a random value of child to
# change. Randomly decide whether to mutate based on a MutationPct, and if so, mutate one gene.
#
###########################################################################################################

def mutate(child):
    # if randrange(0, 101) < MUTATION_PERCENT:
    if uniform(0, 1) < MUTATION_PERCENT / 100:
        return mutate_unique(child) if UNIQUE_ROWS \
            else mutate_random(child)
    return child


def mutate_unique(child):
    # instead of switching a random value,
    #   swap two consecutive values, randomly
    i = sample(range(0, COLS), 2)
    temp = child[i[0]]
    child[i[0]] = child[i[1]]
    child[i[1]] = temp
    return child


def mutate_random(child):
    rand_gene = randrange(0, COLS)
    rand_mutation = randrange(0, ROWS)
    child[rand_gene] = rand_mutation
    return child


###########################################################################################################
#
# Set up and run the algorithm
#
###########################################################################################################

def main():
    better_children_counter = 0
    x = np.empty(1)
    y = np.empty(1)
    children = initial_population()

    # calculate and display average fitness of initial population
    fitness = average_population_fitness(children)
    print("Avg. Fitness (Gen 0):\t", fitness)
    x = np.append(x, 0)
    y = np.append(y, fitness)

    for i in range(ITERATIONS):
        parents = children
        children = []

        # fill children array with next generation of Positions
        for j in range(int(POPULATION_SIZE / 2)):

            # print out some specific populations to look at
            # if i == 0 or i == 100 or i == 900 or i == 999:
            #     print("\tPosition", j, ":", parents[j].position, "Fitness:", parents[j].fitness)

            parent1, parent2 = select_parents(parents)
            child1, child2 = crossover(parent1, parent2)

            # let's see how often the children are more fit than their parents
            parent_fitness = generate_fitness(parent1.position) + generate_fitness(parent2.position)
            child_fitness = generate_fitness(child1.position) + generate_fitness(child2.position)
            if child_fitness > parent_fitness:
                better_children_counter += 1
            if child_fitness == parent_fitness and randrange(0, 2) == 1:
                better_children_counter += 1
            # spoiler: turns out it's never quite 50% even with the good crossover function :'(

            children.append(child1)
            children.append(child2)

        # calculate and display average fitness of population
        fitness = average_population_fitness(children)
        print("Avg. Fitness (Gen " + str(i + 1) + "):\t" + str(fitness))
        x = np.append(x, i + 1)
        y = np.append(y, fitness)

    print((better_children_counter / ((POPULATION_SIZE/2)*ITERATIONS))*100,
          "percent of child pairs improved on their parents.")

    plt.plot(x, y)
    plt.xlim([0, ITERATIONS])
    plt.ylim([0, 1])
    plt.show()


if __name__ == '__main__':
    main()
