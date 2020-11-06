# Changelog

<!--next-version-placeholder-->

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