# leviathan/learning/genetic.py
import random
import numpy as np
from typing import Dict, List, Callable, Any
from loguru import logger

class GeneticOptimizer:
    def __init__(self, param_ranges: Dict[str, tuple], fitness_func: Callable, population_size: int = 50, generations: int = 20):
        self.param_ranges = param_ranges; self.fitness_func = fitness_func; self.population_size = population_size; self.generations = generations; self.population = []
    def _create_individual(self) -> Dict[str, float]:
        return {k: random.uniform(v[0], v[1]) for k,v in self.param_ranges.items()}
    def _crossover(self, p1, p2):
        return {k: p1[k] if random.random() < 0.5 else p2[k] for k in p1.keys()}
    def _mutate(self, individual, mutation_rate=0.1):
        for k in individual.keys():
            if random.random() < mutation_rate:
                individual[k] += random.uniform(-0.1,0.1) * (self.param_ranges[k][1] - self.param_ranges[k][0])
                individual[k] = max(self.param_ranges[k][0], min(self.param_ranges[k][1], individual[k]))
        return individual
    def run(self, initial_population: List[Dict[str, float]] = None) -> Dict[str, float]:
        if initial_population: self.population = initial_population
        else: self.population = [self._create_individual() for _ in range(self.population_size)]
        best_individual = None; best_fitness = -float('inf')
        for gen in range(self.generations):
            fitness_scores = []
            for ind in self.population:
                fitness = self.fitness_func(ind); fitness_scores.append(fitness)
                if fitness > best_fitness: best_fitness = fitness; best_individual = ind.copy()
            new_population = []
            for _ in range(self.population_size):
                tournament = random.sample(list(zip(self.population, fitness_scores)), 3)
                winner = max(tournament, key=lambda x: x[1])[0]
                new_population.append(winner)
            next_population = []
            for i in range(0, self.population_size, 2):
                p1 = new_population[i]; p2 = new_population[i+1] if i+1 < self.population_size else new_population[0]
                child1 = self._crossover(p1,p2); child2 = self._crossover(p2,p1)
                child1 = self._mutate(child1); child2 = self._mutate(child2)
                next_population.extend([child1, child2])
            self.population = next_population[:self.population_size]
            logger.debug(f"Gen {gen+1}/{self.generations}, Best fitness: {best_fitness:.4f}")
        return best_individual
