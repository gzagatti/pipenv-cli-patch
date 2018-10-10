# Pipenv CLI Patches

This repository implements a few patches to improve my personal experience with [`pipenv`](https://github.com/pypa/pipenv). First of all I would like to thank the developers of `pipenv` for creating such a useful tool that has made my life with `python` much easier.

These patches are only experimental, use it at your own risk. Shall they prove useful to the community at large, they could eventually become part of the official CLI API.

## `pipenv` and `pyenv` integration

I use `pipenv` and [`pyenv`](https://github.com/pyenv/pyenv) on a daily basis and I find that they could be better integrated.

In particular, `pipenv` should pay more attention to where it is creating virtual environments in the presence of `pyenv`. Following the convention adopted by `pyenv-virtualenv`, virtual environments created by `pipenv` should also be created within `$(pyenv root)/versions/<version>/envs`. A symlink should also be created between this location and `$(pyenv root)/versions` for consistency sake. In that way, I can easily start a shell using `pyenv` like I do with other virtual environments. Likewise, if environments are created in the correct place, I can now easily list all my environments with `pyenv versions` or `pyenv virtualenvs`.

This patch dynamically modifies `WORKON_HOME` before handing execution to `pipenv`:

1. If the user passes the flag `--python`, `WORKON_HOME` is set to the python version defined by this option. This only applies if the `python` executable is located within `$(pyenv root)`.

2. If a virtual environment already exists in any of the installed python versions, `WORKON_HOME` is set to the one containing the virtual environment.

3. Otherwise, `WORKON_HOME` is set to the python version currently active.

The user might choose to create two virtual environments for the same project using two different python interpreters. In that case, one virtual environment will end up in `<version_foo>/envs` and the other in `<version_bar>/envs`. However, a symlink between `$(pyenv root)/versions/<version>/envs` and `$(pyenv root)/versions` is only created for the first created virtual environment. 

If that environment is eventually removed using `pipenv --rm`, the symlink is replaced to point to the remaining virtual environment.

## `-C`: Run as if I was there

It is possible to run `pipenv` as if it were started from another location by setting `PIPENV_PIPFILE` to the absolute path of the target `Pipfile`. However, this is cumbersome in an interactive setting. It is much more convenient to do what is done by `git`, where the flag `-C` allows ones to run a command as if `git` was started in `<path>`.

Here I have implemented this flag such that `pipenv -C <path> ...` will set `PIPENV_PIPFILE` to the `Pipfile` in `<path>`, running the command from that location.

## Do not be over eager

`pipenv` has a tendency to create virtual environments whenever some of its commands are invoked and a virtual environment does not exist. In an interactive setting, this becomes problematic because without due attention one ends up polluting the system with Pipfiles and creating unnecessary virtual environments. 

It is much cleaner to restrict the initialization of virtual environments to a single command, a bit like `git init` for initializing git repositories. In that manner, this patch will abort if a command that is not `install` is invoked and virtual environment does not exist. 

(Note that due to implementation details and for simplicity sake, the patch will actually abort if a command does not contain the word `install` and the virtual environment does not exist. So if someone runs `pipenv run pip install foo` that would unnecessarily create a virtual environment if one did not exist. The assumption is that few such commands will be invoked.)

## Implementation details

These patches are implemented by creating a `click` object on top of the `click` object created by `pipenv`. The extra options and environment variable tweaks are done before execution is handed to `pipenv`. 
