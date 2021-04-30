# Met4FoF use case hardware sensors

This is supported by European Metrology Programme for Innovation and Research (EMPIR)
under the project
[Metrology for the Factory of the Future (Met4FoF)](https://met4fof.eu), project number
17IND12.

## Purpose

This is an implementation of an agent-based approach to interconnect hardware
sensors from the manufacturer _Seneca_ and processing the produced data streams
including sensor data buffering as part of the agents' implementation.

## Getting started

Note that you need to have access to the actual hardware sensor setup, to execute
most of the code. To get more information on that, contact the
[author of the code](https://github.com/bangxiangyong).

First you need to create a virtual environment based on Python 3.8, install all
dependencies and finally execute the examples. To install the dependencies we utilize
[_pip-tools_](https://pypi.org/project/pip-tools/) to get the specified requirements
from the `requirements.txt`.
  
```shell
$ python -m venv agentMET4FOF_sensors_env
$ source agentMET4FOF_sensors_env/bin/activate
(agentMET4FOF_sensors_env) $ pip install --upgrade pip setuptools pip-tools
(agentMET4FOF_sensors_env) $ pip-sync
```

In case you are using PyCharm, you will already find proper run configurations at the
appropriate place in the IDE. If not you can proceed executing the script files
 manually.

If you have any questions please get in touch with
[the author](https://github.com/bangxiangyong).

### Scripts

The interesting parts you find in the subfolder [_agentMET4FOF_sensors_](agentMET4FOF_sensors).

## References

For details about the agents refer to the
[upstream repository _agentMET4FOF_](https://github.com/bangxiangyong/agentMET4FOF)
