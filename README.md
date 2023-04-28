# geogram-based_program
A ready-to-use empty program based on the [geogram](https://github.com/BrunoLevy/geogram) library.

Requires CMake. Only explected to work on Ubuntu.

## Generate the configuration files

Replace `<name_of_your_project>` by the name of your project (for references in config files).
It must contain only alphanumerical or underscore characters, no spaces, and start with a letter.

```bash
git clone --recurse-submodules https://github.com/LIHPC-Computational-Geometry/geogram-based_program.git
cd geogram-based_program
chmod +x generate_config_files.py
./generate_config_files.py <name_of_your_project>
```

## Build

```bash
cd ext/geogram
git submodule init
git submodule update
cd ../..
chmod +x configure.sh
./configure.sh
cd build/Linux64-gcc-dynamic-Release/
make -j8
```

## Execute

```bash
./simple_mesh_app
```