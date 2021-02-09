# Changelog

<!--next-version-placeholder-->

## v0.13.0 (2021-02-09)
### :sparkles:
* :sparkles: Update PyDynamic and ZeMA_emc and their dependencies  ([`b2531b6`](https://github.com/Met4FoF/Code/commit/b2531b66768be21f778bf99fe672e0a977861185))
* :sparkles: Update agentMET4FOF and thus introduce SineGeneratorAgent and improved docs  ([`ede0878`](https://github.com/Met4FoF/Code/commit/ede08789193e705b48f542eaae89c4d7e54b0bda))

**[See all commits in this version](https://github.com/Met4FoF/Code/compare/v0.12.0...v0.13.0)**

## v0.12.0 (2020-12-16)
### :egg:

* :egg: Introduce Met4FoF-redundancy and update some of the other projects ([`214533d`](https://github.com/Met4FoF/Code/commit/214533dca90afd4c0c5e4e7dec76294a83704ed6))

### :sparkles: 

* :sparkles: Update agentMET4FOF to version 0.4.1 and thus fix an issue with shutdowns ([`c29467f`](https://github.com/Met4FoF/Code/commit/c29467ff93e1ba967cc6173abee27ed4d3bf4896))
* :sparkles: Update agentMET4FOF_anomaly_detection and thus drop agentMET4FOF pinning to version 0.2.0 ([`7ef0713`](https://github.com/Met4FoF/Code/commit/7ef0713ab6555c1552eb62f6dcf2a8e62f83530a))


**[See all commits in this version](https://github.com/Met4FoF/Code/compare/v0.11.0...v0.12.0)**

## v0.11.0 (2020-12-09)
### :sparkles:
* :sparkles: Update agentMET4FOF and thus introduce uncertainty generators  ([`d427444`](https://github.com/Met4FoF/Code/commit/d42744425d83c8bb20933968f9bf6bb764725574))

**[See all commits in this version](https://github.com/Met4FoF/Code/compare/v0.10.2...v0.11.0)**

## v0.10.2 (2020-11-25)
### :lock:
* :lock: Update requirements  ([`d37191b`](https://github.com/Met4FoF/Code/commit/d37191bdbcaa5cd3e58435b0bc776300068c78c6))

### :speech_balloon:
* :speech_balloon: Introduce project homepage's link into _README.md_  ([`49bf174`](https://github.com/Met4FoF/Code/commit/49bf174990476e34f6a1e4446a5bb361fa54d614))

**[See all commits in this version](https://github.com/Met4FoF/Code/compare/v0.10.1...v0.10.2)**

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
