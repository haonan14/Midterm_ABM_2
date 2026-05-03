"""
The Dissemination of Culture - Model
"""

from mesa import Model, DataCollector
from mesa.space import SingleGrid
from collections import deque
from agents import CultureAgent


class CultureDisseminationModel(Model):

    def __init__(
        self,
        width=10,
        height=10,
        num_features=5,
        num_traits=10,
        neighborhood_size=4,
        events_per_step=None,
        seed=None,
    ):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.num_features = num_features
        self.num_traits = num_traits

        # Default: width*height events per step, so each site gets activated roughly once per step
        # I made this change here because the original "one random site per step" is very slow to converge on larger grids when implemening through Mesa
        if events_per_step is not None:
            self.events_per_step = events_per_step
        else:
            self.events_per_step = width * height

        # Mesa uses (moore, radius) to define neighborhoods
        # 4  = Von Neumann r=1:  N, E, S, W
        # 8  = Moore r=1:        adds 4 diagonals
        # 12 = Von Neumann r=2:  adds 4 cells two steps in cardinal directions
        if neighborhood_size == 4:
            self._moore = False
            self._radius = 1
        elif neighborhood_size == 8:
            self._moore = True
            self._radius = 1
        elif neighborhood_size == 12:
            self._moore = False
            self._radius = 2
        else:
            raise ValueError(
                f"Re-choose the neighborhood_size, it must be 4, 8, or 12, got {neighborhood_size}"
            )
        self.neighborhood_size = neighborhood_size

        # torus = False: edges are real boundaries, for the sites on edges and corners
        self.grid = SingleGrid(width, height, torus=False)

        for x in range(width):
            for y in range(height):
                agent = CultureAgent(self, num_features, num_traits)
                self.grid.place_agent(agent, (x, y))

        self.converged = False
        self.running = True

        # Store region/zone counts to avoid rerunning BFS every step when nothing has changed
        self._cached_regions = 0
        self._cached_zones = 0
        self._counts_dirty = True

        self.datacollector = DataCollector(
            model_reporters={
                "Num_Regions": lambda m: m.count_regions(),
                "Num_Zones": lambda m: m.count_zones(),
                "Avg_Similarity": lambda m: m.avg_neighbor_similarity(),
                "Converged": lambda m: m.converged,
            }
        )
        self.datacollector.collect(self)

    # helper functions below

    def _get_neighbors(self, pos):
        """
        Get neighbor agents at position 
        Returns list of agents, excluding None for empty cells
        """
        return self.grid.get_neighbors(
            pos, moore=self._moore, include_center=False, radius=self._radius
        )

    def _get_neighborhood(self, pos):
        """
        Get neighbor coordinates at position
        Returns list of (x, y) tuples, excluding out-of-bounds and the center
        """
        return self.grid.get_neighborhood(
            pos, moore=self._moore, include_center=False, radius=self._radius
        )

    # Interaction
    def _single_event(self):
        """
        One interaction event: pick a random feature
        """
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        agent = self.grid[x][y]

        neighbors = self._get_neighbors((x, y))
        if not neighbors:
            return False
        neighbor = self.random.choice(neighbors)

        # Random feature check
        f = self.random.randrange(self.num_features)
        if agent.culture[f] != neighbor.culture[f]:
            return False

        differing = agent.get_differing_features(neighbor)
        if len(differing) == 0:
            return False

        g = self.random.choice(differing)
        agent.culture[g] = neighbor.culture[g]
        return True

    def step(self):
        """
        Run events_per_step interaction events, then check convergence
        """
        if self.converged:
            return

        any_change = False
        for event in range(self.events_per_step):
            if self._single_event():
                any_change = True

        if any_change:
            self._counts_dirty = True
        else:
            self.converged = self._check_convergence()
            if self.converged:
                self.running = False

        self.datacollector.collect(self)

    def _check_convergence(self):
        """
        Stable when every neighbor pair is either identical (interaction does nothing) 
        or completely incompatible (interaction can't happen)
        """
        for x in range(self.width):
            for y in range(self.height):
                agent = self.grid[x][y]
                for neighbor in self._get_neighbors((x, y)):
                    if agent.is_compatible(neighbor) and not agent.is_identical(neighbor):
                        return False
        return True

    def avg_neighbor_similarity(self):
        """
        Average cultural similarity across all neighbor pairs
        Each pair is counted twice (A→B and B→A) but that doesn't affect the average
        """
        total_similarity = 0.0
        total_pairs = 0

        for x in range(self.width):
            for y in range(self.height):
                agent = self.grid[x][y]
                for neighbor in self._get_neighbors((x, y)):
                    total_similarity = total_similarity + agent.cultural_similarity(neighbor)
                    total_pairs = total_pairs + 1

        if total_pairs == 0:
            return 0.0
        return total_similarity / total_pairs


    # Region and zone counting
    def _recompute_counts(self):
        """
        Recompute both counts together using BFS
        """
        self._cached_regions = self._count_components("identical")
        self._cached_zones = self._count_components("compatible")
        self._counts_dirty = False

    def count_regions(self):
        """
        Contiguous sites with identical culture.
        """
        if self._counts_dirty:
            self._recompute_counts()
        return self._cached_regions

    def count_zones(self):
        """
        Contiguous sites with at least one shared feature
        """
        if self._counts_dirty:
            self._recompute_counts()
        return self._cached_zones

    def _count_components(self, match_type="identical"):
        """
        BFS-based connected component counting
        "identical" = regions (all features match)
        "compatible" = zones (any feature matches)
        """
        visited = set()
        num_components = 0

        for x in range(self.width):
            for y in range(self.height):
                if (x, y) in visited:
                    continue

                num_components = num_components + 1
                queue = deque()
                queue.append((x, y))
                visited.add((x, y))

                while len(queue) > 0:
                    cx, cy = queue.popleft()
                    current_agent = self.grid[cx][cy]

                    for nx, ny in self._get_neighborhood((cx, cy)):
                        if (nx, ny) in visited:
                            continue
                        neighbor_agent = self.grid[nx][ny]
                        if neighbor_agent is None:
                            continue

                        connected = False
                        if match_type == "identical":
                            connected = current_agent.is_identical(neighbor_agent)
                        elif match_type == "compatible":
                            connected = current_agent.is_compatible(neighbor_agent)

                        if connected:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

        return num_components