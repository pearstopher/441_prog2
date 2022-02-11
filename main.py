# CS441-003 Winter 2022
# Programming Assignment 2
#   (8 Queens Genetic Algorithm)
# Christopher Juncker

# import numpy as np
from random import randrange
from math import comb  # n choose k
from copy import deepcopy

# constants & configuration
ITERATIONS = 100
POPULATION_SIZE = 100  # suggested values: 10, 100, 500, 1000, etc.
ROWS = COLS = QUEENS = 8  # increase if you want to experiment with a bigger chess board
MUTATION_PERCENT = 5  # percent chance that a child's gene will be mutated


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
    position = []
    for _ in range(ROWS):
        position.append(randrange(0, COLS))
    return position


###########################################################################################################
#
# Selection of parents: Just as evolutionary biology requires two parents to undergo meiosis, so does GA.
# Therefore there is need to select two parents which determine a child; this selection should be done in
# proportion to the “fitness” of each parent.
#
###########################################################################################################

def generate_fitness(parent):
    # the fitness is the difference between the current number of mutually attacking queens and the
    #   theoretical maximum (QUEENS choose 2)
    max_mutually_attacking = comb(QUEENS, 2)

    # Need to ensure that the minimum fitness value is at least 1 for small population sizes
    #   otherwise a population can have a total of 0 fitness which will cause range errors
    fitness_offset = 1
    return max_mutually_attacking - mutually_attacking(parent) + fitness_offset


def mutually_attacking(parent):
    count = 0
    # loop through each column from left to right
    # count queens attacking current queen from the right
    for i in range(QUEENS):
        for j in range(i + 1, QUEENS):
            if attacking(i, j, parent[i], parent[j]):
                count += 1
    return count


def attacking(col1, col2, row1, row2):
    return attacking_diagonal(col1, col2, row1, row2) \
            or attacking_horizontal(row1, row2)


def attacking_diagonal(col1, col2, row1, row2):
    # (row + column) is equal along secondary diagonal
    # flip row numbers to compare principal diagonal
    return (row1 + col1) == (row2 + col2) or \
           (ROWS - row1 + col1) == (row2 + col2)


def attacking_horizontal(row1, row2):
    return row1 == row2


def select_parents(population):
    total_fitness = total_population_fitness(population)
    parent1_val = randrange(0, total_fitness)
    parent2_val = randrange(0, total_fitness)

    parent1 = parent2 = population[0]  # why not

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
    # for i in range(len(population)):
    #     total += population[i].fitness
    for i in population:
        total += i.fitness
        print(i.fitness)
    return total


###########################################################################################################
#
# CrossOver: Once parents having high fitness are selected, crossover essentially marks the recombining
# of genetic materials / chromosomes to produce a healthy offspring. Pick a random spot for crossover,
# and breed two new children (with fitness computed).
#
###########################################################################################################

def crossover(parent1, parent2):
    random_location = randrange(0, COLS)
    child1 = child2 = []
    for i in range(0, random_location):
        child1.append(parent1.position[i])
        child2.append(parent2.position[i])
    for i in range(random_location, COLS):
        child1.append(parent2.position[i])
        child2.append(parent1.position[i])

    child1 = mutate(child1)
    child2 = mutate(child2)
    return Position(child1), Position(child2)


###########################################################################################################
#
# Mutation: Mutation may or may not occur. In case mutation occurs, it forces a random value of child to
# change. Randomly decide whether to mutate based on a MutationPct, and if so, mutate one gene.
#
###########################################################################################################

def mutate(child):
    if randrange(0, 100) <= MUTATION_PERCENT:
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

    children = initial_population()

    for _ in range(ITERATIONS):
        # parents = deepcopy(children)
        parents = children  # don't really see the problem
        children = []

        for _ in range(POPULATION_SIZE):
            parent1, parent2 = select_parents(parents)
            child1, child2 = crossover(parent1, parent2)

            children.append(child1)
            children.append(child2)


if __name__ == '__main__':
    main()
