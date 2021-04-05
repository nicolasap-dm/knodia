# knodia

Tools for knot diagrams.

The package is still under initial development, unsuitable for public use at
present.

## Basic usage

Currently, this is meant to be run in a notebook.

First, import the `Diagram` class:

```python
from knodia import Diagram
```

To define a diagram, use a list of coordinates:

```python
diagram = Diagram(
    line=[
        (0,0), (1,0), (2,-1), (1,-2), (0,-3), (2,-4), (2,-2), (1,-1), (2,0),
        (3,0), (3,-5), (1,-4), (1,-3), (0,-2)
    ]
)
```

alternatively, not defining a `line` will result in a trivial triangle that can
be edited later:

```python
diagram = Diagram()
```

To edit a diagram, it is currently required to set `tk` as the `matplotlib`
backend. The instructions are:

```python
%matplotlib tk
diagram.visual_edit()
```
