# OTpy

OTpy is a fast Python package for models and algorithms in 
[Optimality Theory](http://en.wikipedia.org/wiki/Optimality_theory) (OT),
alone with a simple easy-to-use user interface.

It reads files in a format illustrated in `sample_input.txt` and
is able to generates legible report in `HTML`.

It implements Constraint Demotion (CD) and Fusional Reduction (FRed) for strict ranking model,
and Generalized Iterative Scaling (GIS), Sequential Conditional GIS (SCGIS) and Nonlinear Conjugate Gradient (NCG)
for Maximum Entropy model (Maxent).

The code is written in `Python 3.3.3`.
The graphic interface is based on `Tkinter` within it.
The generation of Hasse diagraph is supported by `Graphviz`
and Python package `pydot`.

## Quick start

- Download the repostory and run `main.py` using `Python 3.3`.

- Or download and run a stand-alone self-extracting executable from [here](https://github.com/jmzhao/ot_py/releases).

- To generate Hasse diagram, you will need to install [Graphviz](http://www.graphviz.org/). 
For people run with Python, [pydot](https://github.com/nlhepler/pydot) is also needed to operate `.dot` file.

## Links

- [Project home](https://github.com/jmzhao/ot_py)
- [Stand-alone executables](https://github.com/jmzhao/ot_py/releases)
- Poster: [OTpy: A Tool for Constraint-based Linguistics](https://drive.google.com/file/d/0B_DcK-C71ugIdy1NeEEwakpKLUU/view?usp=sharing)
