# Met4FoF Code
[![CircleCI](https://circleci.com/gh/Met4FoF/Code.svg?style=shield&circle-token=3566560a243f21fa06fafbe49e92ac2a6d3fc250)](https://circleci.com/gh/Met4FoF/Code)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0761272aabbc4010bba5921015ab084f)](https://www.codacy.com/app/PTB-PSt1/Code?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Met4FoF/Code&amp;utm_campaign=Badge_Grade)

This repository combines all the code written for or used in the EMPIR project 17IND12 *Metrology for the Factory of the Future* to enable pulling/cloning all the code and all coding related documents at once.

## Installing Git

The following commands assume you already have Git installed. In case you do not have Git installed go to [https://git-scm.com/book/en/v2/Getting-Started-Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and follow the instructions for your operating system. After successful installation open Git Bash in Windows or the command line and run the given commands.

## Getting the code

To clone the repository locally, you go to any folder on your machine (i.e. `~/your/local/folder/`) and execute

`$ git clone --recurse-submodules https://github.com/Met4FoF/Code Met4FoF_Code`

where `Met4FoF_Code` in the command stands for the folder you want the repository to go into. This folder does not need to exist before you execute the command. It will be created as a subfolder and your local repository will be created inside of that subfolder. If you do not specify a folder, the repository will be cloned to the subfolder `Code`, which is the repository's name.

## Updating the code

Whenever you want to get the latest changes, navigate into your local repository folder (i.e. `~/your/local/folder/Met4FoF_Code`) and execute the two commands

`$ git pull origin master`

to get the latest version of this explanatory file and the [coding conventions](conventions/README.md) and/or

`$ git submodule update --remote --recursive`

to update all included repositories to the latest official project related version.

If you have not locally changed any of the files in the folders you will simply update all your local copies and get the latest version of all files on [github.com/Met4FoF/Code](https://github.com/Met4FoF/Code).

## Working on the code

Working on existing submodules' code is just the same as on a base respository. You switch to the submodule's folder inside your repository

`$ cd ~/your/local/folder/Met4FoF_Code/submodule_folder`

and start editing, committing and pushing in the submodule as if you were in a separate Git respository. Of course pushing to a remote repository at GitHub requires the according access rights for the submodule's repository. More on this topic you can find in the [Pro Git book](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

## Coming soon

All planned developments of the project's code and this repository you can find in the repository's [project board](https://github.com/Met4FoF/Code/projects/3).

## Additional information

Additional information around code writing and software development in the project you can find in the repository's [wiki](https://github.com/Met4FoF/Code/wiki) and in the [coding conventions](conventions/README.md).

## Data management

All publishable research data sets produced for or used in the project you can find in the related [zenodo community](https://zenodo.org/communities/met4fof/).
