# Projects

Code for most of my projects can be found on my [Github page](https://github.com/edeno). Here are some select projects I've worked on:

`````{grid} 2

````{grid-item}
:columns: 6

```{image} ../_static/fra_11_04_0001.gif
:alt: replay movie
:target: https://github.com/Eden-Kramer-Lab/replay_trajectory_classification
:align: center
```

````

````{grid-item}
:columns: 6
#### Replay Trajectory Classification
[replay_trajectory_classification](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification) is a Python package for decoding spatial position represented by neural activity and categorizing the type of trajectory. It can decode both clustered and unclustered spiking activity and can take advantage of the GPU for faster computation.

````

````{grid-item}
:columns: 6

```{image} ../_static/spyglass.png
:alt: spyglass logo
:target: https://github.com/LorenFrankLab/spyglass
:width: 70%
:align: center
```

````

````{grid-item}
:columns: 6
#### Spyglass
[Spyglass](https://github.com/LorenFrankLab/spyglass) is a data analysis framework that facilitates the storage, analysis, visualization, and sharing of neuroscience data to support reproducible research. It is designed to be interoperable with the [NWB format](https://www.nwb.org/) (a data standard for neurophysiology) and integrates open-source tools such as [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/) and [DeepLabCut](http://www.mackenziemathislab.org/deeplabcut) into a coherent framework.

````

````{grid-item}
:columns: 6

```{image} ../_static/spectral_connectivity.png
:alt: spectral connectivity image
:target: https://github.com/Eden-Kramer-Lab/spectral_connectivity
:align: center
```

````

````{grid-item}
:columns: 6
#### Spectral Connectivity
[spectral_connectivity](https://github.com/Eden-Kramer-Lab/spectral_connectivity) is a Python software package that computes multitaper spectral estimates and frequency-domain brain connectivity measures such as coherence, spectral granger causality, and the phase lag index using the multitaper Fourier transform.

````

````{grid-item}
:columns: 6

```{image} ../_static/RasterVis.gif
:alt: demo of interactive visualization
:target: https://github.com/NeurophysVis/RasterVis
:align: center
```

````

````{grid-item}
:columns: 6
#### RasterVis
[RasterVis](https://github.com/NeurophysVis/RasterVis) is interactive javascript-based neuroscience visualization tool for quickly viewing, grouping and summarizing spike rasters for many neurons. This tool allows you to generate and change between rasters for many neurons, quickly view rasters aligned to experimental trial events, add Gaussian-smoothed peristimulus time kernel density estimates with arbitrary smoothing and group spikes based on experimental factors. [Demo](https://neurophysvis.github.io/RasterVis/public/)

````

````{grid-item}
:columns: 6

```{image} ../_static/SpectraVis-Demo.gif
:alt: demo of interactive visualization
:target: https://github.com/NeurophysVis/SpectraVis
:align: center
```

````

````{grid-item}
:columns: 6
#### SpectraVis
[SpectraVis](https://github.com/NeurophysVis/SpectraVis) is a interactive javascript-based neuroscience visualization tool for analyzing task-related functional networks over time and frequency. It allows users to examine how network dynamics change over time and frequency, compare local (statistical dependencies between a single pair of nodes) and global (statistical dependencies between all nodes) dynamics, compare different types of functional connectivity measures (correlation, coherence) and switch between multiple network views for better understanding of the network structure. [Demo](https://neurophysvis.github.io/SpectraVis/public/)

````

````{grid-item}
:columns: 6

```{image} ../_static/track_linearization.png
:alt: linearization image
:target: https://github.com/LorenFrankLab/track_linearization
:align: center
```

````

````{grid-item}
:columns: 6
#### Track Linearization
[Track linearization](https://github.com/LorenFrankLab/track_linearization). The hippocampal field often projects the tracked position of the animal from 2D to 1D to simplify computations. These projections are often only computed for one specific spatial environment. This Python package provides tools to flexibly project 2D position to 1D position for any type of spatial environment. There are also visualization tools to inspect these projections.

````

````{grid-item}
:columns: 6

```{image} ../_static/ripple_detection.png
:alt: linearization image
:target: https://github.com/Eden-Kramer-Lab/ripple_detection
:align: center
```

````

````{grid-item}
:columns: 6
#### Ripple Detection
[Ripple detection](https://github.com/Eden-Kramer-Lab/ripple_detection). Sharp wave ripples are 150-250 Hz oscillations in the hippocampus (combined with a slower sharp wave). They are associated with replay, a burst of hippocampal spiking activity where cells recapitulate previously experienced trajectories in the spatial environment. A common task is to detect these sharp wave ripples, but detection varies from lab to lab (see [Liu et al. 2022](https://www.nature.com/articles/s41467-022-33536-x)). I have collected the Frank lab methods for ripple detection in a Python software package so that our methods are transparent and reproducible.

````

`````
