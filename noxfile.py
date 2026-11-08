import nox
from shlex import split

nox.options.reuse_existing_virtualenvs = True


def _sync(session):
    session.run_install(
        *split("uv sync --locked --group execute"),
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )


@nox.session(venv_backend="uv")
def docs(session):
    _sync(session)
    if "live" in session.posargs:
        session.run(
            *split("sphinx-autobuild -b dirhtml . _build/dirhtml --ignore _build/* --ignore **/.ipynb_checkpoints")
        )
    else:
        session.run(
            *"sphinx-build -nW --keep-going -b dirhtml . _build/dirhtml".split()
        )
        session.log("open ./_build/dirhtml/index.html")


@nox.session(venv_backend="uv")
def lab(session):
    _sync(session)
    session.run(*split("jupyter lab ."))
