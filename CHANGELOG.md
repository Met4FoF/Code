# Changelog

<!--next-version-placeholder-->

## v0.10.0 (2020-11-06)
### Feature
* Add a method to shift a vector with associated uncertainty ([`01c1fb2`](https://github.com/Met4FoF/Code/commit/01c1fb21c29a9ec300f4e1008389631fe74daeec))
* Handle case of no filter uncertainty ([`63ca553`](https://github.com/Met4FoF/Code/commit/63ca553170453870b9113e7fbbb6d9262fd7414e))

### Fix
* Flip theta in uncertainty formulas of FIRuncFilter ([`dd04eea`](https://github.com/Met4FoF/Code/commit/dd04eeace70ce4fe7a81fb432cc117f80af74d4f))
* Prepend xlow with constant value ([`f481845`](https://github.com/Met4FoF/Code/commit/f481845e6392a024933b4e79b3a64b6c63915ee5))
* Insert assertion that sigma_noise must be 1D ([`113bc10`](https://github.com/Met4FoF/Code/commit/113bc10b6bc48bf1e5052a38ac9fd4fc5450feb7))
* Insert assertion that sigma_noise must be 1D ([`d984975`](https://github.com/Met4FoF/Code/commit/d9849756a71f0c1ec9d0df63aaf418fd95340cc0))
* Fix a bug in `interp1d_unc` resulting from relying on default values ([`8fb7c3a`](https://github.com/Met4FoF/Code/commit/8fb7c3ababd3346e3bae104947270379b432bd61))

### Documentation
* Include new interpolation tutorials into docs ([`bcd3e89`](https://github.com/Met4FoF/Code/commit/bcd3e89db9eb9996e73715895ac996120b73fbbf))
* Insert important parameter `--force` into migration hint in _Code's_ _README_ ([`316838f`](https://github.com/Met4FoF/Code/commit/316838f75be3105565e075ea7c65cda8edcb4deb))
* Drop Python 3.5 support because it reached EOL on 2020-09-13 ([`d09bda3`](https://github.com/Met4FoF/Code/commit/d09bda38ca6f2298096118356c5be594c98a817f))
* Improve _CONTRIBUTING.md_ with further commit message conventions ([`4c047c5`](https://github.com/Met4FoF/Code/commit/4c047c51628f4c125774c2a225c9730226623eb2))
* Update path to package diagram in _README.md_ ([`05c6007`](https://github.com/Met4FoF/Code/commit/05c6007fee987f0bd30d016513f13258abcc9cd6))
