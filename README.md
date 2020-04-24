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
appropriate place in the IDE. If not you can either proceed executing the Jupyter
Notebooks or by running some of the script files.

If you have any questions please get in touch with
[the author](https://github.com/bangxiangyong).
  
### Jupyter Notebooks

Run Code 01-03 to prepare the ML models, and run Code 04 to start and run the agents.
While Code 04 is running, run Code 05 in separate terminal to visualize them.

### Scripts

The interesting parts you find in the files

- `main_bnn_agents.py`
- `cuda_agent.py`
- `confusion_matrix_dev.py`

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
