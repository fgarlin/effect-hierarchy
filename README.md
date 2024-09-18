# FlightGear Effect Hierarchy Visualization Tool

FlightGear effects can get very complex, very fast. Inheritance, schemes and deprecated effects make it hard to visualize the global picture and the complicated relationships that arise between effects. This can lead to bugs and unexpected behaviour when modifying the effect hierarchy.

This small Python script attempts to aid the developer by building a visual graph that represents the relationships between all of the effects in `$FG_ROOT/Effects`. Just point the script to your FlightGear data directory and it will output a PNG file with the graph.

## Cloning

``` sh
git clone https://github.com/fgarlin/effect-hierarchy.git
```

Alternatively you can download the script through the GitHub interface (Code -> Download ZIP).

## Dependencies

This script is known to work with Python 3.12 and requires the `pydot` package to draw the graph. You can satisfy the required dependency using a virtual environment:

``` sh
python -m venv venv
source env/bin/activate # or activate.fish if using Fish shell
                        # or Activate.ps1 if using the Microsoft Powershell
pip install -r requirements.txt
```

## Usage

``` sh
python effect_hierarchy.py <path to $FG_ROOT>
```

This will output an image to `output.png`. An example graph for the default effect scheme is shown below.

- Diamond shaped nodes indicate that it is a root node (the effect does not have a parent effect).
- Rectangular shaped nodes indicate that the effect does not have a parent effect.
- <span style="color:blue">Blue</span> nodes indicate that the effect **is** implemented for the given scheme.
- <span style="color:blue">Grey</span> nodes indicate that the effect is **not** implemented for the given scheme.

![Default Scheme Example Output](https://raw.githubusercontent.com/fgarlin/effect-hierarchy/master/example_output.png)

## License

This code is released under the GPL-2.0 license. See LICENSE for more details.
