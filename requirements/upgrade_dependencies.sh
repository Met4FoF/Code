#!/bin/bash
#
# This script is meant to simplify the upgrade of the various provided requirements
# files to the latest available package versions. We assume, that the script is
# either called from the project root directly or from its subfolder 'requirements'.
# All provided requirements-files are updated according to the
# specified dependencies from setup.py and the dev-requirements-files for all the
# different versions.
# The production dependencies belong into the according list 'install_requires' in
# setup.py and the development dependencies into the various dev-requirements.in-files.
# For execution the script needs virtual environments, one for each of the upstream
# supported Python versions, with pip-tools installed. Those environments need to be
# placed at ../envs/PyDynamic-PYTHONVERSION relative to the project root. The proper
# naming for the versions you find in the line starting with 'for PYVENV in ' in this
# script.
# The script starts with navigating to the project root, if it was called from
# the subfolder ./requirements/.
if [ -f requirements.txt ] && [ -d ../PyDynamic/ ] && [ -d ../requirements/ ]; then
    cd ..
fi

# Handle all Python versions via setup.py by cycling through the different Python
# environments and update the corresponding two requirements files by issuing the
# appropriate pip-tools command pip-compile from within the specific environments.
export PYTHONPATH=$PYTHONPATH:$(pwd)
for PYVENV in "py36" "py37" "py38"
do
    # Activate according Python environment.
    source ../envs/PyDynamic-$PYVENV/bin/activate && \
    # Create requirements.txt from requirements.in.
    pip-compile --upgrade --output-file requirements/requirements-$PYVENV.txt && \
    # Create dev-requirements...txt from dev-requirements...in.
    pip-compile --upgrade requirements/dev-requirements-$PYVENV.in \
        --output-file requirements/dev-requirements-$PYVENV.txt && \
    deactivate
done
