# Explore with notebooks

The notebooks in this section provide examples for exploring the GKM Toolkit and
working with bundles. The source notebooks live in the project's `notebooks/`
directory.

## Available walkthroughs

The walkthroughs below are rendered examples, so you can read them directly in
your browser without installing anything. Mini bundles are subsets for
exploration. Published bundles contain the complete dataset released by a
producer.

- [Explore GKM Toolkit features with CIViC mini bundles](civic-notebook.md) —
  learn the Toolkit by loading two mini CIViC bundles, inspecting their
  collections, and following bundle-local references.
- [Explore the public bundle repository](repository-notebook.md) — discover
  public resources, retrieve a producer's complete published bundle and its
  schema, load them into GKM models, and handle repository errors.

## Run the notebooks with MyBinder

[Binder](https://mybinder.org/) provides a ready-to-use computing environment for running the notebooks directly in your browser, with no local installation required.

You can launch the notebooks on Binder [here](https://mybinder.org/v2/gh/ga4gh/gkm-starter-kit/main?urlpath=%2Fdoc%2Ftree%2Fnotebooks).

Once launched, select **GKM Toolkit Kernel** as the notebook kernel.

## Run the notebooks locally

If you want to run the notebooks yourself, follow the [Installation steps](../installation.md)
to clone the repository, create the virtual environment (`.venv`), and activate it.

!!! note "Notebook dependency"

    If you did not install the `notebooks` optional dependency during setup,
    run this command from the root of the cloned project (`gkm-starter-kit/`),
    with the virtual environment activated:

    ```shell
    python3 -m pip install "ga4gh.gkm[notebooks]" --pre
    ```

      `--pre` is provided since this project uses pre-release versions of the
      [GKM reference implementations](../../reference-implementations.md)

### Open a notebook

We recommend either of the following options for opening a notebook.

#### JupyterLab

1. In the terminal, activate the project's `.venv` virtual environment:

         source .venv/bin/activate

2. In the activated virtual environment, start [JupyterLab](https://docs.jupyter.org/en/latest/):

         python3 -m jupyterlab

3. JupyterLab usually opens automatically in a new browser window. If it does not, open
   the URL shown in the terminal.
4. Open a notebook from the `notebooks/` directory.

#### VS Code

1. Install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
   and [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).
2. Open the project root in VS Code and open a notebook from the
   `notebooks/` directory.
3. Select **Select Kernel** in the upper-right corner and choose the Python
   interpreter from the repository's `.venv` virtual environment.
