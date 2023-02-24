[![docs](https://img.shields.io/badge/docs-ts--m2gui.lsst.io-brightgreen)](https://ts-m2gui.lsst.io/)

# M2 Graphical User Interface (GUI) in Python

## Platform

- CentOS 7
- python: 3.10.5

## Needed Package

- numpy (install by `conda`)
- pyyaml (install by `conda`)
- pyside2 (install by `conda`)
- qt5-qtbase-devel (install by `yum`)
- xorg-x11-server-Xvfb (optional, install by `yum`)
- qasync (install by `conda -c conda-forge`)
- [black](https://github.com/psf/black) (23.1.0, optional)
- [flake8](https://github.com/PyCQA/flake8) (4.0.1, optional)
- [isort](https://github.com/PyCQA/isort) (5.10.1, optional)
- [documenteer](https://github.com/lsst-sqre/documenteer) (optional)
- pytest (optional, install by `conda`)
- pytest-flake8 (optional, install by `conda -c conda-forge`)
- pytest-qt (optional, install by `conda -c conda-forge`)
- pytest-xvfb (optional, install by `conda -c conda-forge`)

## Code Format

This code is automatically formatted by `black` using a git pre-commit hook (see `.pre-commit-config.yaml`).
To enable this, see [pre-commit](https://pre-commit.com).

## Build the Document

To build project documentation, run `package-docs build` to build the documentation.
To clean the built documents, use `package-docs clean`.
See [Building single-package documentation locally](https://developer.lsst.io/stack/building-single-package-docs.html) for further details.

## Run GUI in Docker Container

### CentOS 7

Forward GUI by:

```bash
xhost local:root
docker run -it --rm -e DISPLAY -v ${path_to_this_package}:${path_of_package_in_container} -v /tmp/.X11-unix:/tmp/.X11-unix ${docker_image}:${image_tag}
```

### MacOS

1. Setup the x11 by following: [x11_docker_mac](https://gist.github.com/cschiewek/246a244ba23da8b9f0e7b11a68bf3285).

2. Forward GUI by:

```bash
xhost +
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
docker run -it --rm -e DISPLAY=${IP}:0 -v ${path_to_this_package}:${path_of_package_in_container} -v /tmp/.X11-unix:/tmp/.X11-unix ${docker_image}:${image_tag}
```

## Run GUI without the LSST Docker Image on MacOS

You need to setup the QT environment with:

```bash
export QT_MAC_WANTS_LAYER=1
export QT_MAC_USE_NSWINDOW=1
```

You may need to setup the **PYTHONPATH** to point to `python/` directory as well.

## Executable

The executable (`run_m2gui`) is under the `bin/` directory.
Use the argument of `-h` to know the available options.
The logged message will be under the `log/` directory.

The environment variable **TS_CONFIG_MTTCS_DIR** specifies [ts_config_mttcs](https://github.com/lsst-ts/ts_config_mttcs) directory for GUI started in the simulation mode.

## Unit Tests

You can run the unit tests by:

```bash
export PYTEST_QT_API="PySide2"
pytest tests/
```

If you have the **Xvfb** and **pytest-xvfb** installed, you will not see the prompted windows when running the unit tests.

Note: If the variable of `PYTEST_QT_API` is not set, you might get the core dump error in the test.

## Class Diagrams

The class diagrams are in [here](doc/uml).
You can use the [PlantUML](https://plantuml.com) to read them.
QT is an event-based framework and the signal plays an important role among classes.
The `emit()` and `connect()` in the class diagrams mean the class **emits** a specific siganl or **connects** it to a specific callback function.
The environment variable **PATH_PLANTUML** is required to indicate the position of **plantuml.jar**.
Otherwise, the default position will be used.
