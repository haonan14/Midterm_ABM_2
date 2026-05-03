"""
The Dissemination of Culture
"""

from mesa import Agent

class CultureAgent(Agent):
    """
    A site with a cultural profile: a vector of F features, each taking an integer value in [0, q).
    """

    def __init__(self, model, num_features, num_traits):
        super().__init__(model)
        # Each feature gets a random trait from [0, q)
        self.culture = []
        for i in range(num_features):
            self.culture.append(self.random.randrange(num_traits))

    def cultural_similarity(self, other):
        """
        Fraction of features with identical traits
        Returns float in [0, 1]
        """
        matches = 0
        for i in range(len(self.culture)):
            if self.culture[i] == other.culture[i]:
                matches = matches + 1
        return matches / len(self.culture)

    def get_differing_features(self, other):
        """
        Return indices of features where traits differ
        """
        differing = []
        for i in range(len(self.culture)):
            if self.culture[i] != other.culture[i]:
                differing.append(i)
        return differing

    def is_compatible(self, other):
        """
        True if they share at least one feature, meaning they can interact
        Used for zone counting and convergence checks
        """
        for i in range(len(self.culture)):
            if self.culture[i] == other.culture[i]:
                return True
        return False

    def is_identical(self, other):
        """
        True if all features match 
        Used for region counting
        """
        return self.culture == other.culture