# Changelog

<!--next-version-placeholder-->

## v0.10.1 (2020-11-06)
### :ambulance:
* :ambulance: _Update agentMET4FOF_anomaly_detection_ to latest version for avoiding test timeouts ([`8bc68f7`](https://github.com/Met4FoF/Code/commit/8bc68f7ccd09e7b570a3afd74a4ef59d583e953f))

### :robot:
* :robot: Improve release automation and changelog generation  ([`63fe7c5`](https://github.com/Met4FoF/Code/commit/63fe7c567ff7405584874222388f37a81706d0ef))

**[See all commits in this version](https://github.com/Met4FoF/Code/compare/v0.10.0...v0.10.1)**

## v0.10.0 (2020-11-06)

### Updated repositories

In this release we updated

- _agentMET4FOF_ to version 0.3.0,
- _PyDynamic_ to version 1.6.1,
- tutorials/_anomaly_detection_ to its current version relying on _agentMET4FOF_ version 0.2.0.

#### PyDynamic improvements

_PyDynamic_ has received two new features, some bug fixes and documentation improvements. The new features are:

* Add a method `shift_uncertainty()` to shift a vector with associated uncertainty ([`2584ea1`](https://github.com/Met4FoF/Code/commit/2584ea1fffb828cec726434bf669738ed5c5d034))
* Handle case of no filter uncertainty in `FIRuncFilter()` ([`63ca553`](https://github.com/Met4FoF/Code/commit/63ca553170453870b9113e7fbbb6d9262fd7414e))

See the [PyDynamic releases](https://github.com/PTB-PSt1/PyDynamic/releases) for details.

#### agentMET4FOF improvements

_agentMET4FOF_ has evolved regarding the metrological agents quite a bit. Please check the [agentMET4FOF release](https://github.com/bangxiangyong/agentMET4FOF/releases/) page for details.