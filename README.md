# Met4FoF Code

[![DOI](https://zenodo.org/badge/138772091.svg)](https://zenodo.org/badge/latestdoi/138772091)
[![CircleCI](https://circleci.com/gh/Met4FoF/Code.svg?style=shield&circle-token=3566560a243f21fa06fafbe49e92ac2a6d3fc250)](https://circleci.com/gh/Met4FoF/Code)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b72908cff3174e529487518065aded8b)](https://www.codacy.com/gh/Met4FoF/Code/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Met4FoF/Code&amp;utm_campaign=Badge_Grade)

![met4fof.eu](https://www.ptb.de/empir2018/fileadmin/documents/empir/Met4FoF/images/Metrology-Factory-Future_Logo_200px.png)

This repository combines all the code written for or used in the
[EMPIR project 17IND12 *Metrology for the Factory of the Future*](https://met4fof.eu/) 
to enable pulling/cloning all the code and all coding related documents at once.

For more details in the project visit us on
[met4fof.eu](https://met4fof.eu/). 

You find the project partners' code in the corresponding subfolders of the repository.

## **MIGRATING FROM PREVIOUS VERSIONS**

If you have a clone of this repository where the subprojects were still included as
_Git submodules_, run the following command sequence once in the repository's root
directory:
 
```bash
$ git submodule deinit --all --force
$ git pull
```

This temporarily deletes your copies of the former submodules and replaces them by
the current versions in this repository. From then on simply use the command as
stated in [Updating the code](#Updating-the-code) to stay up-to-date.

## Project's coding conventions and best practices

Additional information around code writing and software development in the project
you can find in the repository's
[wiki](https://github.com/Met4FoF/Code/wiki), in the
[coding conventions](conventions/README.md) and in our related
[Blog post](https://www.ptb.de/empir2018/met4fof/information-communication/blog/detail-view/?tx_news_pi1%5Bnews%5D=38&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Baction%5D=detail&cHash=ce963c7573572d40ef0f496449ef8aff)
on the [project homepage](https://met4fof.eu/). 

## Installing Git

The following commands assume you already have Git installed. In case you do not have
Git installed go to
[https://git-scm.com/book/en/v2/Getting-Started-Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
and follow the instructions for your operating system. After successful installation
open _Git Bash_ in Windows or the command line and run the given commands.

## Getting the code

To clone the repository locally, you go to any folder on your machine (i.e. `~/your/local/folder/`) and execute

```bash
$ git clone --recurse-submodules https://github.com/Met4FoF/Code Met4FoF_Code
```

where `Met4FoF_Code` in the command stands for the folder you want the repository to
go into. This folder does not need to exist before you execute the command. It will
be created as a subfolder and your local repository will be created inside of that
subfolder. If you do not specify a folder, the repository will be cloned to the
subfolder `Code`.

## Updating the code

Whenever you want to get the latest changes, navigate into your local repository folder (i.e. `~/your/local/folder/Met4FoF_Code`) and execute the command

`$ git pull origin master`

to get the latest version of all the official project related code.

If you have not locally changed any of the files in the folders you will simply
update all your local copies and get the latest version of all files on
[github.com/Met4FoF/Code](https://github.com/Met4FoF/Code).

## Working on the code

If you want to contribute to the project code, you can use the usual collaboration
mechanisms (forks, issues, Pull Requests, ... ) on GitHub. If you're unsure where to
start, open a discussion in an [issue](https://github.com/Met4FoF/Code/issues) in
this repository or contact
[us](https://github.com/Met4FoF/Code/graphs/contributors) in any other way.

More on this topic you can find in the
[official GitHub documentation on collaboration](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests).

## Coming soon

All planned developments of the project's code and this repository you can find in
the repository's [project board](https://github.com/Met4FoF/Code/projects/3) and the
subprojects' boards and their GitHub issues.

## Data management

All publishable research data sets produced for or used in the project you can find in the related [zenodo community](https://zenodo.org/communities/met4fof/).
