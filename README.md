# Met4FoF use case machine learning

This is supported by European Metrology Programme for Innovation and Research (EMPIR)
under the project
[Metrology for the Factory of the Future (Met4FoF)](https://met4fof.eu), project number
17IND12.

## Purpose

This is an implementation of and agent-based approach to machine learning utilizing
 the external Python library [`scikit-multiflow`](https://scikit-multiflow.github.io/).

## Getting started

First you need to create a virtual environment, install all dependencies and finally
 execute the examples. To install the dependencies you first have to install _numpy_
  and then the specified requirements from the `requirements.txt`.
  
```shell
$ python -m venv agentMET4FOF_ML_env
$ source agentMET4FOF_ML_env/bin/activate
(agentMET4FOF_ML_env) $ pip install --upgrade pip setuptools numpy
(agentMET4FOF_ML_env) $ pip install -r requirements.txt
```

In case you are using PyCharm, you will already find proper run configurations at the
appropriate place in the IDE. If not you can proceed executing the script files
 manually.

If you have any questions please get in touch with
[the author](https://github.com/bangxiangyong).

### Scripts

The interesting parts you find in the subfolder [_agentMET4FOF_ML_](agentMET4FOF_ML).

### Note

In the event of agents not terminating cleanly, run

```shell
taskkill /f /im python.exe /t
```

in Windows Command Prompt to terminate all  background python processes.

## References

For details about the agents refer to the
[upstream repository _agentMET4FOF_](https://github.com/bangxiangyong/agentMET4FOF)

## Screenshot of web visualization
![Web Screenshot](https://github.com/bangxiangyong/agentMet4FoF/blob/master/screenshot_met4fof.png)
