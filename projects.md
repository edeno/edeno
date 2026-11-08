# Projects

Code for most of my projects can be found on my [GitHub page](https://github.com/edeno). Here are some select projects I've worked on:

## Featured

::::{div} featured

```{image} _static/spyglass.png
:alt: Spyglass logo
```

**[Spyglass](https://github.com/LorenFrankLab/spyglass)**

A framework for storing, analyzing, visualizing, and sharing neurophysiology data reproducibly. It stores data in the [NWB](https://www.nwb.org/) standard, tracks every analysis step with [DataJoint](https://datajoint.com/), and wraps tools such as [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/) and [DeepLabCut](https://www.mackenziemathislab.org/deeplabcut) in shared pipelines. I am a co-first author on the paper describing it.

:::{div} project-links
[Code](https://github.com/LorenFrankLab/spyglass) · [Paper](https://doi.org/10.7554/eLife.108089.3)
:::

::::

::::{div} featured

```{raw} html
<video controls autoplay loop muted playsinline preload="metadata" aria-label="Animation of classifying replay trajectories">
  <source src="/_static/replay-trajectory-classification.mp4" type="video/mp4">
</video>
```

**[Replay Trajectory Classification](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification)**

Decodes position moment by moment from hippocampal spiking, sorted or clusterless, and classifies each replay as stationary, continuous, or fragmented. It handles linearized 1D and 2D environments and can run on the GPU.

:::{div} project-links
[Code](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification) · [Paper](https://doi.org/10.7554/eLife.64505)
:::

::::

## More projects

::::{div} project

**[Non-Local Detector](https://github.com/LorenFrankLab/non_local_detector)**

Detects non-local activity such as replay, and decodes position, from sorted or clusterless spikes using hidden Markov models written in JAX. It supports several likelihood models and multiple environments, and runs on the GPU.

:::{div} project-links
[Code](https://github.com/LorenFrankLab/non_local_detector)
:::

::::

::::{div} project

**[Spectral Connectivity](https://github.com/Eden-Kramer-Lab/spectral_connectivity)**

Multitaper spectral estimates and frequency-domain connectivity measures, including coherence, spectral Granger causality, and phase-lag indices, for many signals at once on the CPU or GPU.

:::{div} project-links
[Code](https://github.com/Eden-Kramer-Lab/spectral_connectivity) · [Paper](https://doi.org/10.21105/joss.04840)
:::

::::

::::{div} project

**[RasterVis](https://github.com/NeurophysVis/RasterVis)**

A browser tool for viewing spike rasters across many neurons: align them to trial events, group them by experimental factors, and overlay smoothed firing-rate estimates.

:::{div} project-links
[Code](https://github.com/NeurophysVis/RasterVis) · [Demo](https://neurophysvis.github.io/RasterVis/public/)
:::

::::

::::{div} project

**[SpectraVis](https://github.com/NeurophysVis/SpectraVis)**

A browser tool for exploring functional brain networks over time and frequency, comparing pairwise and whole-network views across connectivity measures.

:::{div} project-links
[Code](https://github.com/NeurophysVis/SpectraVis) · [Demo](https://neurophysvis.github.io/SpectraVis/public/)
:::

::::

::::{div} project

**[Track Linearization](https://github.com/LorenFrankLab/track_linearization)**

Converts 2D position on a maze or track into 1D position along the track, using a graph of the track's layout, with an optional hidden Markov model to handle noisy tracking.

:::{div} project-links
[Code](https://github.com/LorenFrankLab/track_linearization)
:::

::::

::::{div} project

**[Ripple Detection](https://github.com/Eden-Kramer-Lab/ripple_detection)**

Detects hippocampal sharp-wave ripples (150–250 Hz) in local field potentials, with several published detectors side by side so results can be compared and reproduced (see [Liu et al. 2022](https://www.nature.com/articles/s41467-022-33536-x)).

:::{div} project-links
[Code](https://github.com/Eden-Kramer-Lab/ripple_detection)
:::

::::
