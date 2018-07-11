# Met4FoF Code

This repository combines all the code written for or used in the EMPIR project 17IND12 *Metrology for the Factory of the Future* to enable pulling/cloning all the code and all coding related documents at once.

## Getting the code

To clone the repository locally, you go to any folder on your machine (i.e. `~/your/local/folder/`) and execute

`git clone --recurse-submodules https://github.com/Met4FoF/Code Met4FoF_Code`

where `Met4FoF_Code` in the command stands for the folder you want the repository to go into. This folder does not need to exist before you execute the command. It will be created as a subfolder and your local repository will be created inside of that subfolder. If you do not specify a folder, the repository will be cloned to the subfolder `Code`, which is the repository's name.

## Updating the code

Whenever you want to get the latest changes, navigate into your local repository folder (i.e. `~/your/local/folder/Met4FoF_Code`) and execute

`git submodule update --remote`.

If you have not locally changed any of the files in the folders you will simply update all your local copies and get the latest version of all files on [github.com/Met4FoF/Code](https://github.com/Met4FoF/Code).

## Coming soon

All planned developments of the project's code and this repository you can find in the repository's [project board](https://github.com/Met4FoF/Code/projects/3).

## Additional information

Additional information around code writing and software development in the project you can find in the repository's [wiki](https://github.com/Met4FoF/Code/wiki).

## Data management

All publishable research data sets produced for or used in the project you can find in the related [zenodo community](https://zenodo.org/communities/met4fof/).
