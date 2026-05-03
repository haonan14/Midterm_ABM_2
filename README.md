# Axelrod (1997) — The Dissemination of Culture

## How to Run

```
pip install mesa solara matplotlib altair
solara run app.py
```

## File Structure

- **agents.py** — `CultureAgent`: each agent holds a culture vector (a list of F features, each with a trait value from 0 to q-1).
- **model.py** — `CultureDisseminationModel`: sets up the grid, runs the interaction events, checks convergence, and counts cultural regions/zones via BFS.
- **app.py** — GUI configuration: grid visualization (culture → color), two time-series plots (regions/zones and average neighbor similarity), and parameter sliders.

## Parameters

All parameters varied in the paper are adjustable via sliders:

| Slider | Default |
|--------|---------|
| Grid Width / Height | 10 × 10 |
| Features (F) | 5 |
| Traits per Feature (q) | 10 |
| Neighborhood Size | 4 |

Neighborhood size accepts 4, 8, or 12.