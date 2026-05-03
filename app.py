"""
The Dissemination of Culture - App
"""

import matplotlib.colors as mcolors
from model import CultureDisseminationModel
from mesa.visualization import (
    SolaraViz,
    make_space_component,
    make_plot_component,
    Slider,
)

# 10 visually distinct colors from matplotlib, designed for readability
COLORS = list(mcolors.TABLEAU_COLORS.values())


def culture_to_color(culture):
    """
    Map a culture vector to a color using hash
    Same culture always gets the same color
    With 10 colors, two different cultures might collide to the same color occasionally, but for typical runs (3-10 stable regions) this is fine
    
    Here I consulted AI, for how to do representation through Mesa as I can not truly replicate what the original paper does. So I consulted for how to
    use color to represent culture, and the idea of hashing the culture vector to a color came up. I think this is a reasonable way to visually distinguish different cultures, 
    even if there might be some collisions due to the limited color palette. 
    And I chose the Tableau colors from matplotlib because they are designed to be visually distinct and readable, 
    which should help in distinguishing different cultures on the grid.
    """
    return COLORS[hash(tuple(culture)) % len(COLORS)]


def agent_portrayal(agent):
    return {
        "color": culture_to_color(agent.culture),
        "size": 200,
        "marker": "s",
    }


# Sliders for four parameter groups varied in the paper:
# territory size, cultural complexity (F and q), and range of interaction
model_params = {
    "width": Slider("Grid Width", value=10, min=5, max=50, step=5),
    "height": Slider("Grid Height", value=10, min=5, max=50, step=5),
    "num_features": Slider("Features (F)", value=5, min=2, max=15, step=1),
    "num_traits": Slider("Traits per Feature (q)", value=10, min=2, max=15, step=1),
    # Only 4, 8, 12 are valid
    "neighborhood_size": Slider(
        "Neighborhood Size", value=4, min=4, max=12, step=4
    ),
    "seed": 42,
}

space_component = make_space_component(
    agent_portrayal,
    backend="matplotlib",
)

# Blue = regions (identical culture), Red = zones (compatible culture)
# At convergence these two lines meet because every zone becomes one region
regions_plot = make_plot_component(
    {"Num_Regions": "tab:blue", "Num_Zones": "tab:red"},
    backend="matplotlib",
)

# Tracks how similar neighbors are on average across the grid
# Starts low (random cultures), rises as convergence happens
similarity_plot = make_plot_component(
    {"Avg_Similarity": "tab:green"},
    backend="matplotlib",
)

page = SolaraViz(
    model = CultureDisseminationModel(),
    components=[space_component, regions_plot, similarity_plot],
    model_params=model_params,
    name="Axelrod Culture Dissemination Model",
)