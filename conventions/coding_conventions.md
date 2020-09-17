# EMPIR project 17IND12 ***Met4FoF*** coding conventions

These coding conventions apply to all code and software written for the project
and will constantly be extended as the project evolves and more code is written.  

## Design

1. All lines in code files should not exceed 88 characters.

1. Names for modules, classes, methods and functions should be speaking and
   explicitly represent the content.

1. The use of global variables should be avoided where possible.

1. There should be no *TODO*-statements in released versions.

1. There should be no out commented code in released versions.

1. *CI/CD* should be implemented, if applicable.

## Documentation

1. All documentation should be provided in English.

1. A first overview of what the code in a repository does should be provided
   inside a `README.md`.

1. All parts of the public interface of modules, classes, methods and functions
   should provide detailed information in their headers about inputs, outputs
   and what is done.

1. A module/class header should at least provide information about authors,
   available functions and module-/class-parameters.

1. Function und method headers should provide information about authors, what
   and how it is done and in- and output parameters.

1. For in- and output parameters that are vectors or matrices, information on
   the dimensions should be provided.

1. Presentation of inputs and outputs should be consistent throughout one
   repository.

1. A function body should include a reasonable amount of commenting to provide
   a broad idea of what is happening at different points within the function.

1. If there are references to external sources in documenting comments, those
   should be consistently spread all over the project.

1. It is highly recommended that version number and release date be included in
   every release.

## Source code management

1. Git should be used during the whole process of software development for the
   project.

1. Commit early and often and publish your code as often as applicable to the
   open-source repository of the project.

1. Commit messages should be either
   [Conventional Commit messages](https://www.conventionalcommits.org/en/v1.0.0/) 
   with a maximum line length of 100 characters or formatted as follows:
   
   * First line is 50 characters or less and contains a brief description of
     the commit. It starts with a capital letter and does not end with a period.
     It finishes the sentence: *"If applied, this commit will" **your commit
     message***
   * If additional explanation is needed:
     * Second line is a blank line.
     * Remaining text should be wrapped at 72 characters and contains a
       detailed description of the commit.

   These conventions are based on different community sources basically stating
   the same:
   
   * [Tim Pope (2008)](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
   * [Chris Beams (2014)](https://chris.beams.io/posts/git-commit/)
   * [Stephen Amaza (2017)](https://medium.com/@steveamaza/how-to-write-a-proper-git-commit-message-e028865e5791)
   * [https://stackoverflow.com/questions/2290016/](https://stackoverflow.com/questions/2290016/git-commit-messages-50-72-formatting)

    For examples look at
    [the commit messages of this repository](https://github.com/Met4FoF/Code/commits).
