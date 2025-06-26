import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib.patches as mpatches
import matplotlib
import time
import seaborn as sns
from numba import Boolean


class SIRS:
    def __init__(self, size, p1, p2, p3, immune, lattice=None):
        self.rng = np.random.default_rng()
        self.size = size
        self.probabilities = np.array([p1, p2, p3])
        self.immune = immune

        # S:0, I:1, R:2
        if lattice is None:
            self.lattice = self.rng.integers(0, 2, size=(self.size, self.size), endpoint=True)
        else:
            if lattice.shape == (self.size, self.size):
                self.lattice = lattice
            else:
                raise Exception("Lattice given does not match the size")

    def step(self):
        # choose which point to update
        i = self.rng.integers(0, self.size, endpoint=False)
        j = self.rng.integers(0, self.size, endpoint=False)

        value = self.rng.uniform(0.0, 1.0)

        # auxilliary matrix
        aux = np.zeros((self.size + 2, self.size + 2), dtype=int)
        # middle of auxilliary is same as lattice
        aux[1:self.size + 1, 1: self.size + 1] = self.lattice
        # periodic boundary conditions
        aux[1:self.size + 1, 0] = self.lattice[:, -1]
        aux[1:self.size + 1, -1] = self.lattice[:, 0]
        aux[0, 1:self.size + 1] = self.lattice[-1, :]
        aux[-1, 1:self.size + 1] = self.lattice[0, :]
        aux[0, 0] = self.lattice[-1, -1]
        aux[0, -1] = self.lattice[-1, 0]
        aux[-1, 0] = self.lattice[0, -1]
        aux[-1, -1] = self.lattice[0, 0]

        if int(self.lattice[i, j]) == 0:
            infected = np.array([aux[i + 2, j + 1], aux[i, j + 1], aux[i + 1, j + 2], aux[i + 1, j]])
            if np.any(infected == 1):
                if value < self.probabilities[0]:
                    self.lattice[i, j] += 1
                    aux[i + 1, j + 1] += 1

        elif int(self.lattice[i, j]) != 3:
            if value < self.probabilities[int(self.lattice[i, j])]:
                self.lattice[i, j] += 1
                aux[i + 1, j + 1] += 1

                if self.immune == False:
                    if int(self.lattice[i, j]) == 3:
                        self.lattice[i, j] = 0
                        aux[i + 1, j + 1] = 0

    def sweep(self):
        for i in range(self.size * self.size):
            self.step()

    def simulate(self, fps):
        cmap = matplotlib.cm.get_cmap('viridis')
        fig = plt.figure(figsize=(12, 10))
        im = plt.imshow(self.lattice, interpolation="none", aspect="auto", vmin=0, vmax=2)
        plt.title("SIRS Model")
        s_patch = mpatches.Patch(color=cmap(0), label="Susceptible")
        i_patch = mpatches.Patch(color=cmap(1 / 2), label="Infected")
        r_patch = mpatches.Patch(color=cmap(0.999), label="Recovered")
        plt.legend(bbox_to_anchor=(1.2, 1), handles=[s_patch, i_patch, r_patch])
        plt.tight_layout()
        plt.gca().set_aspect("equal", adjustable="box")

        def animate(i):
            self.sweep()
            im.set_array(self.lattice)
            return [im]

        anim = animation.FuncAnimation(fig, animate, interval=1000 / fps, blit=True)
        plt.show()