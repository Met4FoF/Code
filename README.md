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

### Scripts

The interesting parts you find in the file

- `main_zema_agents.py`

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
