# Projects

Code for most of my projects can be found on my [GitHub page](https://github.com/edeno). Here are some select projects I've worked on:

## Featured

:::::{grid} 1
:gutter: 3

  ::::{grid-item-card} Spyglass
  :img-top: _static/spyglass.png
  :img-alt: Spyglass logo
  :text-align: left
  :class-card: featured-project

  [Spyglass](https://github.com/LorenFrankLab/spyglass) is a data analysis framework that facilitates the storage, analysis, visualization, and sharing of neuroscience data to support reproducible research. It is designed to be interoperable with the [NWB format](https://www.nwb.org/) (a data standard for neurophysiology) and integrates open-source tools such as [SpikeInterface](https://spikeinterface.readthedocs.io/en/latest/) and [DeepLabCut](https://www.mackenziemathislab.org/deeplabcut) into a coherent framework. I am a co-first author on the [eLife reviewed preprint](https://doi.org/10.7554/eLife.108089.1).

  +++
  {bdg-primary}`Python` {bdg-info}`NWB` {bdg-light}`Data Framework`

  {bdg-link-primary}`GitHub <https://github.com/LorenFrankLab/spyglass>` [![GitHub stars](https://img.shields.io/github/stars/LorenFrankLab/spyglass?style=social&label=Stars)](https://github.com/LorenFrankLab/spyglass)
  ::::

  ::::{grid-item-card} Replay Trajectory Classification
  :img-top: _static/fra_11_04_0001.gif
  :img-alt: Animation of classifying replay trajectories
  :text-align: left
  :class-card: featured-project

  [replay_trajectory_classification](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification) is a Python package for decoding spatial position represented by neural activity and categorizing the type of trajectory. It can decode both clustered and unclustered spiking activity and uses GPU acceleration for fast inference. The underlying state-space methods are described in our [eLife paper](https://doi.org/10.7554/eLife.64505).

  +++
  {bdg-primary}`Python` {bdg-info}`GPU` {bdg-light}`Neuroscience`

  {bdg-link-primary}`GitHub <https://github.com/Eden-Kramer-Lab/replay_trajectory_classification>` [![GitHub stars](https://img.shields.io/github/stars/Eden-Kramer-Lab/replay_trajectory_classification?style=social&label=Stars)](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification)
  ::::

:::::

## More projects

:::::{grid} 1 2 2 3
:gutter: 3

  ::::{grid-item-card} Spectral Connectivity
  :img-top: _static/spectral_connectivity.png
  :img-alt: Spectral Connectivity visualization example
  :text-align: left

  [spectral_connectivity](https://github.com/Eden-Kramer-Lab/spectral_connectivity) computes multitaper spectral estimates and frequency-domain brain connectivity measures (coherence, spectral Granger causality, phase-lag index) on the CPU and GPU. Published in [JOSS](https://doi.org/10.21105/joss.04840).

  +++
  {bdg-primary}`Python` {bdg-info}`Signal Processing` {bdg-light}`Neuroscience`

  {bdg-link-primary}`GitHub <https://github.com/Eden-Kramer-Lab/spectral_connectivity>` [![GitHub stars](https://img.shields.io/github/stars/Eden-Kramer-Lab/spectral_connectivity?style=social&label=Stars)](https://github.com/Eden-Kramer-Lab/spectral_connectivity)
  ::::

  ::::{grid-item-card} RasterVis
  :text-align: left

  ```{raw} html
  <video autoplay loop muted playsinline preload="metadata" aria-label="Demonstration of RasterVis interactive visualization" style="width:100%;display:block;border-top-left-radius:inherit;border-top-right-radius:inherit;">
    <source src="../_static/RasterVis.mp4" type="video/mp4">
  </video>
  ```

  Interactive JavaScript tool for quickly viewing, grouping, and summarizing spike rasters across many neurons, with trial-aligned PSTH overlays and arbitrary smoothing.

  +++
  {bdg-warning}`JavaScript` {bdg-info}`Visualization` {bdg-light}`Neuroscience`

  {bdg-link-primary}`GitHub <https://github.com/NeurophysVis/RasterVis>` {bdg-link-secondary}`Demo <https://neurophysvis.github.io/RasterVis/public/>` [![GitHub stars](https://img.shields.io/github/stars/NeurophysVis/RasterVis?style=social&label=Stars)](https://github.com/NeurophysVis/RasterVis)
  ::::

  ::::{grid-item-card} SpectraVis
  :text-align: left

  ```{raw} html
  <video autoplay loop muted playsinline preload="metadata" aria-label="Demonstration of SpectraVis interactive network visualization" style="width:100%;display:block;border-top-left-radius:inherit;border-top-right-radius:inherit;">
    <source src="../_static/SpectraVis-Demo.mp4" type="video/mp4">
  </video>
  ```

  Interactive JavaScript tool for analyzing task-related functional brain networks across time and frequency, with side-by-side local and global views.

  +++
  {bdg-warning}`JavaScript` {bdg-info}`Visualization` {bdg-light}`Network Analysis`

  {bdg-link-primary}`GitHub <https://github.com/NeurophysVis/SpectraVis>` {bdg-link-secondary}`Demo <https://neurophysvis.github.io/SpectraVis/public/>` [![GitHub stars](https://img.shields.io/github/stars/NeurophysVis/SpectraVis?style=social&label=Stars)](https://github.com/NeurophysVis/SpectraVis)
  ::::

  ::::{grid-item-card} Track Linearization
  :img-top: _static/track_linearization.png
  :img-alt: Example of track linearization from 2D to 1D
  :text-align: left

  [track_linearization](https://github.com/LorenFrankLab/track_linearization) projects 2D animal-tracking position to 1D for any spatial environment, with visualization tools for inspecting the projection. The hippocampal field often relies on this transformation to simplify downstream analyses.

  +++
  {bdg-primary}`Python` {bdg-info}`Spatial Analysis` {bdg-light}`Neuroscience`

  {bdg-link-primary}`GitHub <https://github.com/LorenFrankLab/track_linearization>` [![GitHub stars](https://img.shields.io/github/stars/LorenFrankLab/track_linearization?style=social&label=Stars)](https://github.com/LorenFrankLab/track_linearization)
  ::::

  ::::{grid-item-card} Ripple Detection
  :img-top: _static/ripple_detection.png
  :img-alt: Illustration of hippocampal ripple detection
  :text-align: left

  [ripple_detection](https://github.com/Eden-Kramer-Lab/ripple_detection) is a Python package collecting the Frank lab methods for detecting hippocampal sharp-wave ripples (150-250 Hz oscillations associated with replay), so the procedure is transparent and reproducible across labs (see [Liu et al. 2022](https://www.nature.com/articles/s41467-022-33536-x) for a comparison).

  +++
  {bdg-primary}`Python` {bdg-info}`Signal Processing` {bdg-light}`Neuroscience`

  {bdg-link-primary}`GitHub <https://github.com/Eden-Kramer-Lab/ripple_detection>` [![GitHub stars](https://img.shields.io/github/stars/Eden-Kramer-Lab/ripple_detection?style=social&label=Stars)](https://github.com/Eden-Kramer-Lab/ripple_detection)
  ::::

:::::
