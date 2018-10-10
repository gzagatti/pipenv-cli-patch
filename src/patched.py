import os
from pipenv import cli
from pipenv.patched import crayons
from pipenv.vendor import click, delegator
from pipenv.vendor.pythonfinder.environment import PYENV_INSTALLED, PYENV_ROOT

def venv_symlink(workon, venv_name):

    def handle_venv_symlink():

        if PYENV_INSTALLED and workon and venv_name:

            src = os.path.join(workon, venv_name)
            dst = os.path.join(PYENV_ROOT, "versions", venv_name)

            # delete broken links, which might be caused by actions such as --rm
            if os.path.islink(dst) and not os.path.exists(dst):
                os.unlink(dst)
                # perhaps we can link with another pre-existing virtual environment
                versions = delegator.run("pyenv versions").out.splitlines(
                    keepends=False)
                for v in versions:
                    v = v.split()
                    v = v[0] if v[0] != "*" else v[1]
                    if "/envs/" in v:
                        if v.endswith(venv_name):
                            src = os.path.join(PYENV_ROOT, "versions", v)
                            break

            # create a symlink between source and destination
            if os.path.exists(src) and not os.path.exists(dst):
                os.symlink(src, dst)


    return handle_venv_symlink

@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option(
    "working_dir",
    "-C",
    help="Run as if pipenv started in <path> instead of the current working directory.",
    type=click.Path(exists=True, resolve_path=True)
)
@click.option("--python", type=click.Path(exists=True, resolve_path=True))
@click.pass_context
def patched_cli(ctx, working_dir, python):

    if working_dir:
        if not os.path.isdir(working_dir):
            working_dir = os.path.dirname(working_dir)
        os.environ["PIPENV_PIPFILE"] = os.path.join(working_dir, "Pipfile")

    # we need to import environments and modify PIPENV_PIPFILE
    # to ensure that Project is imported with the right value
    from pipenv import environments
    environments.PIPENV_PIPFILE = os.environ.get("PIPENV_PIPFILE")
    from pipenv.project import Project

    if PYENV_INSTALLED:

        workon = None
        venv_name = None

        if python and python.startswith(PYENV_ROOT) and "bin/python" in python:
            workon = os.path.dirname(os.path.dirname(python))
            workon = os.path.join(workon, "envs")


        try:
            venv_name = Project().virtualenv_name
        except AttributeError:
            # AttributeError is raised when pipenv does not find a valid
            # Pipfile and attempts spliting None
            pass

        if not workon and venv_name:
            versions = delegator.run("pyenv versions").out.splitlines(
                keepends=False)
            for v in versions:
                v = v.split()
                v = v[0] if v[0] != "*" else v[1]
                if "/envs/" in v:
                    if v.endswith(venv_name):
                        workon = os.path.join(PYENV_ROOT, "versions",
                                os.path.dirname(v.strip()))
                        break

        if not workon:
            c = delegator.run("pyenv which python")
            c.block()
            workon = os.path.dirname(os.path.dirname(c.out.strip()))
            workon = os.path.join(workon, "envs")

        os.environ["WORKON_HOME"] = workon
        ctx.call_on_close(venv_symlink(workon, venv_name))

    if python:
        ctx.args = ["--python", python] + ctx.args

    try:
        venv_exists = Project().virtualenv_exists
    except:
        venv_exists = False

    if not ("install" in ctx.args or venv_exists):
        click.echo(
            crayons.red("No virtualenv has been created for this project yet!"),
            err = True,
        )
        ctx.abort()

    ctx.invoke(cli, ctx.args)

if __name__ == "__main__":
    patched_cli()

