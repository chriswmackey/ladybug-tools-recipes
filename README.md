# ladybug-tools-recipes

Publicly available recipes for common workflows, produced by Ladybug Tools.

## Load as Queenbee recipe

1. Change directory to one of the recipes folders (e.g. `cd recipes/daylight-factor`).
2. Install the package using `pip install .`.
3. Use `queenbee_dsl` to load the package as a Queenbee Recipe.

```python
from queenbee_dsl.package import load

recipe = load(python_package)
print(recipe.yaml())
```
