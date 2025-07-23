"""
Resource management for Space Game Clone.
"""
from settings import STARTING_MINERALS, STARTING_ENERGY, STARTING_MAX_ENERGY

class ResourceManager:
    def __init__(self, minerals=STARTING_MINERALS, energy=STARTING_ENERGY, max_energy=STARTING_MAX_ENERGY):
        self.starting_minerals = minerals
        self.starting_energy = energy
        self.starting_max_energy = max_energy
        self.reset()

    def reset(self):
        self.minerals = self.starting_minerals
        self.energy = self.starting_energy
        self.max_energy = self.starting_max_energy

    def add_minerals(self, amount):
        self.minerals += amount

    def spend_minerals(self, amount):
        if self.minerals >= amount:
            self.minerals -= amount
            return True
        return False

    def add_energy(self, amount):
        self.energy = min(self.energy + amount, self.max_energy)

    def spend_energy(self, amount):
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    def increase_max_energy(self, amount):
        self.max_energy += amount 