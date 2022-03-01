# M2 Graphical User Interface (GUI) in Python

## Platform

- CentOS 7
- python: 3.8.12

## Needed Package

- pyside2 (install by `conda`)
- mesa-libGL.x86_64 (install by `yum`)
- [black](https://github.com/psf/black) (19.10b0, optional)
- [documenteer](https://github.com/lsst-sqre/documenteer) (optional)

## Code Format

This code is automatically formatted by `black` using a git pre-commit hook.
To enable this:

1. Install the `black` Python package.
2. Run `git config core.hooksPath .githooks` once in this repository.

## Build the Document

To build project documentation, run `package-docs build` to build the documentation.
To clean the built documents, use `package-docs clean`.
See [Building single-package documentation locally](https://developer.lsst.io/stack/building-single-package-docs.html) for further details.

## Run GUI in Docker Container (MacOS)

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
