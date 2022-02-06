<p align="center">
 <img src="https://www.ptb.de/empir2018/fileadmin/documents/empir/Met4FoF/images/Metrology-Factory-Future_Logo_200px.png" alt="the logo of the Met4FoF project" title="Met4FoF project logo">
 <br>
  <!-- Zenodo DOI -->
  <a href="https://zenodo.org/badge/latestdoi/138772091">
   <img src="https://zenodo.org/badge/138772091.svg" alt="DOI of the Met4FoF project's source code" title="Met4FoF source code DOI">
  </a>
  <!-- CircleCI -->
  <a href="https://circleci.com/gh/Met4FoF/Code">
   <img src="https://circleci.com/gh/Met4FoF/Code.svg?style=shield&circle-token=3566560a243f21fa06fafbe49e92ac2a6d3fc250" alt="CI status of the Met4FoF project's source code" title="Met4FoF source code CI status">
  </a>
  <!-- Codacy -->
  <a href="https://www.codacy.com/gh/Met4FoF/Code/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Met4FoF/Code&amp;utm_campaign=Badge_Grade">
   <img src="https://app.codacy.com/project/badge/Grade/b72908cff3174e529487518065aded8b" alt="Quality rating of the Met4FoF project's source code" title="Met4FoF source code quality rating">
  </a>
</p>

# Met4FoF Code

This repository combines all the code written for or used in the
[EMPIR project 17IND12 *Metrology for the Factory of the
Future*](https://www.ptb.de/empir2018/met4fof/)
to simplify getting started and enable pulling/cloning all the code and all coding
related documents at once.

For a general overview on the project visit us on
[ptb.de/empir2018/met4fof](https://www.ptb.de/empir2018/met4fof/).

Detailed information about the project goals you find in
the [downloadable publishable summary](https://www.ptb.de/empir2018/fileadmin/documents/empir/Met4FoF/Documents/17IND12_Met4FoF_M27_PublishableSummary.pdf)
.

In [the software section of the project homepage
](https://www.ptb.de/empir2018/met4fof/software/) you will get an overview of all
software development activities throughout the duration of the project.

## Table of content

- [Getting started](#getting-started)
  - [Getting into Git and GitHub](#getting-into-git-and-github)
  - [The content of this repository](#the-content-of-this-repository)
  - [Tutorials](#tutorials)
- [Project's coding conventions and best practices
  ](#projects-coding-conventions-and-best-practices)
- [Contributing](#contributing)
- [Further development](#further-development)
- [Data management](#data-management)
- [Citation](#citation)
- [Acknowledgement](#acknowledgement)
- [Disclaimer](#disclaimer)
- [License](#license)

## Getting started

### Getting into Git and GitHub

If you are new to Git or GitHub you find
extensive [guidance on how to start with the repository in our wiki](https://github.com/Met4FoF/Code/wiki)
.

### The content of this repository

Collected in this repository you can find the results of most of the software
development activities in the project. The main projects you can find in the subfolders
of this repository:

#### [agentMET4FOF](agentMET4FOF)

agentMET4FOF is an interactive and flexible open-source implementation of a multi-agent
system.

#### [Met4FoF-SmartUpUnit](Met4FoF-SmartUpUnit)

This software contains code for the firmware of the microcontroller board, which we call
the "SmartUp Unit".

#### [Met4FoF SmartUp Unit datareceiver](datareceiver)

This repository contains the Python driver to receive the measurement data from the
[Met4FoF SmartUp Unit](#Met4FoF-SmartUpUnit).

#### [Met4FoF-redundancy](https://www.ptb.de/empir2018/met4fof/software/further-developments/#c5948)

This software package contains software tools based on [agentMET4FOF](#agentMET4FOF)
that can be used to analyze measurement data which contain redundancy. It is fully
integrated into [agentMET4FOF](#agentMET4FOF) in form of the [Redundancy Agent
](https://agentmet4fof.readthedocs.io/en/latest/tutorials.html#working-with-signals-carrying-redundant-information)

#### [Bayesian Noise and Jitter removal algorithm](https://www.ptb.de/empir2018/met4fof/software/further-developments/#c6058)

This software implements an algorithm to reduce timing and noise effects in the data
recorded by sensors in industrial sensor networks. It is fully integrated
into [agentMET4FOF](#agentMET4FOF) in form of the [Noise-Jitter Removal Agent
](https://agentmet4fof.readthedocs.io/en/latest/agentMET4FOF_tutorials/noise_jitter/remove_noise_and_jitter.html)

#### [ZeMA Testbed Bayesian Machine Learning](ZeMA_testbed_Bayesian_machine_learning)

This is an implementation of Bayesian machine learning for the ZeMA dataset on condition
monitoring of a hydraulic system.

#### [time-series-buffer - a metrological time-series buffer](time-series-buffer)

This package provides support for time-series buffering based on the build-in Python
`collections.deque`.

#### [A metrologically enabled time-series metadata scheme](time-series-metadata)

time-series-metadata is a Python implementation of a metadata scheme for time-series
with measurement uncertainties.

#### [PyDynamic](PyDynamic)

The goal of this package is to provide a starting point for users in metrology and
related areas who deal with time-dependent i.e., dynamic, measurements.

### [Tutorials](tutorials)

The majority of our code base is accompanied by a series of tutorials in form of Jupyter
Notebooks, Python scripts or even parts of our [video tutorial series
](https://www.ptb.de/empir2018/de/met4fof/information-communication/video-portal/). The
videos require a self-registration which takes only a minute and serves to keep track of
who is interested in our material. 

## Project's coding conventions and best practices

Additional information around code writing and software development in the project you
can find in the repository's
[wiki](https://github.com/Met4FoF/Code/wiki), in the
[coding conventions](conventions/README.md) and in our related
[Blog post](https://www.ptb.de/empir2018/met4fof/information-communication/blog/detail-view/?tx_news_pi1%5Bnews%5D=38&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Baction%5D=detail&cHash=ce963c7573572d40ef0f496449ef8aff)
on the [project homepage](https://met4fof.eu/).

## Contributing

If you want to contribute back to the project take a look at our open developments in
the [pull requests
](https://github.com/Met4FoF/Code/pulls) and search [the issues
](https://github.com/Met4FoF/Code/issues). If you find something similar to your ideas
or troubles, let us know by leaving a comment or remark. If you have something new to
tell us, feel free to open a feature request or bug report in the issues.

If your interest is focused on one of the subprojects, please visit their respective
repository's pages as well.

More on this topic you can find in the
[official GitHub documentation on collaboration](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests)
.

## Further development

The project itself ended with September 2021. Some subprojects in this repository are
still well maintained due to their ongoing use in other projects or personal interest.
Upstream changes are usually still mirrored into this repository here on an irregular
basis.

## Data management

All publishable research data sets produced for or used in the project you can find in
the related [zenodo community](https://zenodo.org/communities/met4fof/) side by side
with each released version of this source code repository.

## Citation

If you publish results obtained with the help of any parts of this code base, please
cite the linked [![Met4FoF source code DOI](https://zenodo.org/badge/138772091.svg)
](https://zenodo.org/badge/latestdoi/138772091).

## Acknowledgement

This work was part of the Joint Research
Project [Metrology for the Factory of the Future (Met4FoF), project number 17IND12](https://www.ptb.de/empir2018/met4fof/)
of the European Metrology Programme for Innovation and Research (EMPIR). The
[EMPIR](http://msu.euramet.org) is jointly funded by the EMPIR participating countries
within EURAMET and the European Union.

## Disclaimer

This software is developed as a joint effort of several project partners under the lead
of PTB. The software is made available "as is" free of cost. The authors and their
institutions assume no responsibility whatsoever for its use by other parties, and makes
no guarantees, expressed or implied, about its quality, reliability, safety, suitability
or any other characteristic. In no event will the authors be liable for any direct,
indirect or consequential damage arising in connection with the use of this software.

## License

The Met4FoF code base is distributed under the
[LGPLv3 license](https://github.com/Met4FoF/Code/blob/main/license.md).