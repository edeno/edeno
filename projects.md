# Projects

Code for most of my projects can be found on my [Github page](https://github.com/edeno). Here are some select projects I've worked on:

## Replay Trajectory Classification

`replay_trajectory_classification` is a python package for decoding spatial position represented by neural activity and categorizing the type of trajectory.

<p align="center">
  <img src="https://github.com/Eden-Kramer-Lab/replay_trajectory_classification/blob/master/fra_11_04_0001.gif" height="400"></img>
</p>

It has several advantages over decoders typically used to characterize hippocampal data:

1. It allows for moment-by-moment estimation of position using small temporal time bins which allow for rapid movement of neural position and makes fewer assumptions about what downstream cells can integrate.
2. The decoded trajectories can change direction and are not restricted to constant velocity trajectories.
3. The decoder can use spikes from spike-sorted cells or use clusterless spikes and their associated waveform features to decode .
4. The decoder can categorize the type of neural trajectory and give an estimate of the confidence of the model in the type of trajectory.
5. Proper handling of complex 1D linearized environments
6. Ability to extract and decode 2D environments
7. Easily installable, documented code with tutorials on how to use the code (see below)
8. Fast computation using GPUs. (Note: must install `cupy` to use)

[Repo](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification)

## Spectral Connectivity

`spectral_connectivity` is a Python software package that computes multitaper spectral estimates and frequency-domain brain connectivity measures such as coherence, spectral granger causality, and the phase lag index using the multitaper Fourier transform. Although there are other Python packages that do this (see [nitime](https://github.com/nipy/nitime) and [MNE-Python](https://github.com/mne-tools/mne-python)), `spectral_connectivity` has several differences:

+ it is designed to handle multiple time series at once
+ it caches frequently computed quantities such as the cross-spectral matrix and minimum-phase-decomposition, so that connectivity measures that use the same processing steps can be more quickly computed.
+ it decouples the time-frequency transform and the connectivity measures so that if you already have a preferred way of computing Fourier coefficients (i.e. from a wavelet transform), you can use that instead.
+ it implements the non-parametric version of the spectral granger causality in Python.
+ it implements the canonical coherence, which can
efficiently summarize brain-area level coherences from multielectrode recordings.
+ easier user interface for the multitaper fourier transform
+ all function are GPU-enabled if `cupy` is installed and the environmental variable `SPECTRAL_CONNECTIVITY_ENABLE_GPU` is set to 'true'.

[Repo](https://github.com/Eden-Kramer-Lab/spectral_connectivity).

## SpectraVis

SpectraVis is a javascript-based interactive web-based neuroscience tool for analyzing task-related functional networks over time and frequency. It allows users to:

+ examine how network dynamics change over time and frequency
+ compare local (statistical dependencies between a single pair of nodes) and global (statistical dependencies between all nodes) dynamics.
+ compare different types of functional connectivity measures (correlation, coherence).
+ compare between different subjects.
+ examine only within- or between-brain area connections
+ switch between multiple network views for better understanding of the network structure

[Demo](https://neurophysvis.github.io/SpectraVis/). [Repo](https://github.com/NeurophysVis/SpectraVis).
![demo](https://github.com/NeurophysVis/SpectraVis/blob/master/SpectraVis-Demo.gif)

## RasterVis

RasterVis is interactive javascript-based neuroscience visualization tool for quickly viewing, grouping and summarizing spike rasters for many neurons.

This tool allows you to:

+ Generate and change between rasters for many neurons
+ Quickly view rasters aligned to experimental trial events.
+ Add Gaussian-smoothed peristimulus time kernel density estimates with arbitrary smoothing.
+ Group spikes based on experimental factors.

[Demo](https://neurophysvis.github.io/RasterVis/public/). [Repo](https://github.com/NeurophysVis/RasterVis).
![demo](https://github.com/NeurophysVis/RasterVis/blob/master/img/RasterVis-ChangeNeurons.gif)

## Spyglass

`spyglass` is a data analysis framework that facilitates the storage, analysis, visualization, and sharing of neuroscience data to support reproducible research. It is designed to be interoperable with the NWB format and integrates open-source tools into a coherent framework.s

[Repo](https://github.com/LorenFrankLab/spyglass)

## Track Linearization

Tools to flexible linearize 2D position to 1D position. Works for any type of spatial environment.

[Repo](https://github.com/LorenFrankLab/track_linearization)
