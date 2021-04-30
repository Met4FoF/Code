# Met4FoF use case of agent based condition monitoring

This is supported by European Metrology Programme for Innovation and Research (EMPIR)
under the project
[Metrology for the Factory of the Future (Met4FoF)](https://met4fof.eu), project number
17IND12.

## Purpose

This is an implementation of the agent-based approach for the [ZEMA dataset ![DOI
](https://zenodo.org/badge/DOI/10.5281/zenodo.1323611.svg
)](https://doi.org/10.5281/zenodo.1323611)
on condition monitoring of a hydraulic system.

## Getting started

In case you are using PyCharm, you will already find proper run configurations at the
appropriate place in the IDE. It expects that you have prepared and defined a default
interpreter.

If you are not using PyCharm, of course you can run the script files as usual.

If you have any questions please get in touch with
[the author](https://github.com/bangxiangyong).

### Dependencies

To install all dependencies in virtual environment based on Python version 3.9 first
install `pip-tools` and afterwards use our prepared `requirements.txt` to get
everything ready.

### Create a virtual environment on Windows

In your Windows command prompt execute the following to set up a virtual environment
in a folder of your choice.

```shell
> cd /LOCAL/PATH/TO/ENVS
> python -m venv my_agent_use_case_env
> my_agent_use_case_env\Scripts\activate.bat
(my_agent_use_case_env) > pip install --upgrade pip pip-tools numpy
Collecting numpy
...
Successfully installed numpy-...
(my_agent_use_case_env) > pip-sync
Collecting agentMET4FOF
...
Successfully installed agentMET4FOF-... ...
...
```

### Create a virtual environment on Mac and Linux

In your terminal execute the following to set up a virtual environment
in a folder of your choice.

```shell
$ python3.8 -m venv my_agent_use_case_env
$ source my_agent_use_case_env/bin/activate
$ pip install --upgrade pip pip-tools numpy
$ pip-sync
Collecting agentMET4FOF
...
Successfully installed agentMET4FOF-... ...
...
```

### Scripts

The interesting parts you find in the file

- `main_zema_agents.py`

## References

For details about the agents refer to the
[upstream repository _agentMET4FOF_](https://github.com/bangxiangyong/agentMET4FOF)

## Screenshot of web visualization

![Web Screenshot](https://github.com/Met4FoF/agentMET4FOF/blob/0c96171509dd7aec01de44b7ba573279efecbdef/docs/screenshot_met4fof.png)
