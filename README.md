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

### Create a virtual environment on Windows

In your Windows command prompt execute the following to set up a virtual environment
in a folder of your choice.

```shell
> python -m venv agentMET4FOF_ml_env
> agentMET4FOF_ml_env\Scripts\activate.bat
(agentMET4FOF_ml_env) > pip install --upgrade pip numpy
```

And then install the required dependencies after navigating to the root of your clone. 

```shell
(agentMET4FOF_ml_env) > pip install -r requirements.txt
```

### Create a virtual environment on Mac and Linux

In your terminal execute the following to set up a virtual environment in a folder of
your choice.

```shell
$ python3 -m venv agentMET4FOF_ml_env
$ source agentMET4FOF_ml_env/bin/activate
(agentMET4FOF_ml_env) $ pip install --upgrade pip numpy
```

And then install the required dependencies after navigating to the root of your clone. 

```shell
(agentMET4FOF_ml_env) $ pip install -r requirements.txt
```

In case you are using PyCharm, you will already find proper run configurations at the
appropriate place in the IDE. If not you can proceed executing the script files
 manually.

If you have any questions please get in touch with
[the author](https://github.com/bangxiangyong).

### Scripts

The interesting parts you find in the subfolder [_agentMET4FOF_ml_](agentMET4FOF_ml).

### Orphaned processes

In the event of agents not terminating cleanly, you can end all Python processes
running on your system (caution: the following commands affect **all** running Python
 processes, not just those that emerged from the agents).

#### Killing all Python processes in Windows

In your Windows command prompt execute the following to terminate all python processes.

```shell
> taskkill /f /im python.exe /t
>
```

#### Killing all Python processes on Mac and Linux

In your terminal execute the following to terminate all python processes.

```shell
$ pkill python
$
```

## References

For details about the agents refer to the
[upstream repository _agentMET4FOF_](https://github.com/bangxiangyong/agentMET4FOF)

## Screenshot of web visualization

![Web Screenshot](https://raw.githubusercontent.com/bangxiangyong/agentMET4FOF/develop/docs/screenshot_met4fof.png)
