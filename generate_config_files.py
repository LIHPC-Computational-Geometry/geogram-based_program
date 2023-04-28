#!/usr/bin/python

import sys
import os
from pathlib import Path

project_name = ''
if len(sys.argv)>1:
    project_name = sys.argv[1]
else:
    project_name = input('Name of your project (for references in config files): ')

project_name_uppercase = project_name.upper()

# --------------------------------------------------------------------------------------------------------------------------------
# Step 1 : generate .cmake files
# based on https://github.com/BrunoLevy/GraphiteThree/blob/main/cmake/graphite.cmake
#      and https://github.com/BrunoLevy/GraphiteThree/blob/main/cmake/graphite_config.cmake

if not (Path('cmake').exists() & Path('cmake').is_dir()):
    os.mkdir('cmake')

with open(Path('cmake') / (project_name + '.cmake'), 'w') as file:
    file.write(
r"""
set(""" + project_name_uppercase + r"""_SOURCE_DIR ${CMAKE_SOURCE_DIR})
include(${""" + project_name_uppercase + r"""_SOURCE_DIR}/cmake/""" + project_name + r"""_config.cmake)
link_directories(${""" + project_name_uppercase + r"""_SOURCE_DIR}/${RELATIVE_LIB_DIR})
""")
    
with open(Path("cmake") / (project_name + "_config.cmake"), "w") as file:
    file.write(
r"""
macro(""" + project_name + r"""_find_Python)
find_package(PythonLibs 3 QUIET)
if(NOT PYTHONLIBS_FOUND)
    message(
        STATUS
        "CMake did not find Python library, 
            using default fallbacks (edit WHERE_IS... in CMakeGUI if need be)."	
    )
    set(PYTHON_INCLUDE_DIRS ${WHERE_ARE_PYTHON_INCLUDES})
    set(PYTHON_LIBRARIES ${WHERE_IS_PYTHON_LIB})
endif()
if(
    NOT "${PYTHON_INCLUDE_DIRS}" STREQUAL "" AND
    NOT "${PYTHON_LIBRARIES}" STREQUAL ""
)
    set(""" + project_name_uppercase + r"""_FOUND_PYTHON TRUE)
endif()
endmacro()

if(IS_DIRECTORY ${CMAKE_SOURCE_DIR}/ext/geogram/)
set(
    GEOGRAM_SOURCE_DIR "${CMAKE_SOURCE_DIR}/ext/geogram/"
    CACHE PATH "full path to the Geogram installation"
)
set(USE_BUILTIN_GEOGRAM TRUE)
else()
message(
    SEND_ERROR
    "CMake did not find Geogram in ${CMAKE_SOURCE_DIR}/ext/geogram/"	
    )
endif()
""")

# --------------------------------------------------------------------------------------------------------------------------------
# Step 2 : generate CMakeOptions.txt.xxx in geogram's folder
# based on files in ext/geogram/cmake/options/

with open('ext/geogram/CMakeOptions.txt.' + project_name, 'w') as file:
    file.write(
r"""
if(WIN32)
   set(VORPALINE_PLATFORM Win-vs-dynamic-generic)
elseif(APPLE)
   set(VORPALINE_PLATFORM Darwin-clang-dynamic)
elseif(UNIX)
   set(VORPALINE_PLATFORM Linux64-gcc-dynamic)
endif()

# Only geogram, geogram_gfx and GLFW will be built
# (skips generation of geogram demos and programs)
set(GEOGRAM_LIB_ONLY ON)
""")

# --------------------------------------------------------------------------------------------------------------------------------
# Step 3 : generate CMakeLists.txt
# based on https://github.com/BrunoLevy/GraphiteThree/blob/main/CMakeLists.txt

with open('CMakeLists.txt', 'w') as file:
    file.write(
r"""
cmake_minimum_required(VERSION 3.0)

project(""" + project_name + r""")

set(
  GEOGRAM_SOURCE_DIR "${CMAKE_SOURCE_DIR}/ext/geogram/"
  CACHE PATH "full path to the Geogram installation"
)

include(${CMAKE_SOURCE_DIR}/cmake/""" + project_name + r""".cmake)

file(GLOB SRCFILES src/*.cpp )
include_directories(include)

add_subdirectory(ext/geogram)

add_executable(simple_mesh_app ${SRCFILES} app/simple_mesh_app)
target_link_libraries(simple_mesh_app geogram geogram_gfx ${GLFW_LIBRARIES})
""")

# --------------------------------------------------------------------------------------------------------------------------------
# Step 4 : generate configure.sh
# based on https://github.com/BrunoLevy/GraphiteThree/blob/main/configure.sh

with open('configure.sh', 'w') as file:
    file.write(
r"""#!/bin/sh

# This file for Linux users, 
# launches CMake and creates configuration for
# Release and Debug modes.

# Check for the presence of geogram

if [ ! -f ext/geogram/CMakeOptions.txt.""" + project_name + r""" ]; then
   echo "geogram is missing, you need to install it as well with:"
   echo "git clone https://github.com/BrunoLevy/geogram.git"
   echo "(or clone automatic_polycube repo with the --recursive option)"
   exit
fi

if [ -f ext/geogram/CMakeOptions.txt ]; then
   echo "Using user-supplied CMakeOptions.txt in geogram"
else
   echo "Using Graphite default CMakeOptions.txt in geogram"
   cp ext/geogram/CMakeOptions.txt.graphite ext/geogram/CMakeOptions.txt
fi

echo
echo ============= Checking for CMake ============
echo

if (cmake --version); then
    echo "Found CMake"
    echo
else
    echo "Error: CMake not found, please install it (see http://www.cmake.org/)"
    exit 1
fi

# Parse command line arguments

cmake_options=-DCMAKE_BUILD_TYPE=Debug
build_name_suffix=
while [ -n "$1" ]; do
    case "$1" in
        --with-*=*)
            cmake_option=`echo "$1" | sed 's/--with-\([^=]*\)=\(.*\)$/-DVORPALINE_WITH_\U\1\E:STRING="\2"/'`
            cmake_options="$cmake_options $cmake_option"
            shift
            ;;

        --with-*)
            cmake_option=`echo "$1" | sed 's/--with-\(.*\)$/-DVORPALINE_WITH_\U\1:BOOL=TRUE/'`
            cmake_options="$cmake_options $cmake_option"
            shift
            ;;
        --help-platforms)
            echo "Supported platforms:"
            for i in `find ext/geogram/cmake/platforms/* -type d`
            do
                if [ $i != "xxxgeogram/cmake/platforms" ]
                then
                    echo "*" `basename $i`
                fi
            done
            exit
            ;;
        --build_name_suffix=*)
            build_name_suffix=`echo "$1" | sed 's/--build_name_suffix=\(.*\)$/\1/'`
            shift
            ;; 

        --help)
            cat <<END
NAME
    configure.sh
SYNOPSIS
    Prepares the build environment for """ + project_name + r""".
    
    - For Unix builds, the script creates 2 build trees for Debug and Release
    build in a 'build' sub directory under the project root.
USAGE
    configure.sh [options] [build-platform]
OPTIONS
    --help
        Prints this page.
    --build_name_suffix=suffix-dir
        Add a suffix to define the build directory
PLATFORM
    Build platforms supported by """ + project_name + r""": use configure.sh --help-platforms
END
            exit
            ;;

        -*)
            echo "Error: unrecognized option: $1"
            return 1
            ;;
        *)
            break;
            ;;
    esac
done

# Check the current OS

os="$1"
if [ -z "$os" ]; then
    os=`uname -a`
    case "$os" in
        Linux*x86_64*)
            os=Linux64-gcc-dynamic
            ;;
        Linux*amd64*)
            os=Linux64-gcc-dynamic
            ;;
        Linux*i586*|Linux*i686*)
            os=Linux32-gcc-dynamic
            ;;
        Darwin*)
            os=Darwin-clang-dynamic
            ;;
        *)
            echo "Error: OS not supported: $os"
            exit 1
            ;;
    esac
fi

# Generate the Makefiles

for config in Release Debug; do
   platform=$os-$config
   echo
   echo ============= Creating makefiles for $platform ============
   echo

   build_dir=build/$platform$build_name_suffix
   mkdir -p $build_dir
   (cd $build_dir;
    cmake \
        -DCMAKE_BUILD_TYPE:STRING=$config \
        -DVORPALINE_PLATFORM:STRING=$os \
    $cmake_options ../../)
done

echo
echo ============== """ + project_name + r""" build configured ==================
echo

cat << EOF
To build """ + project_name + r""":
  - go to build/$os-Release$build_name_suffix or build/$os-Debug$build_name_suffix
  - run 'make' or 'cmake --build .'
Note: local configuration can be specified in CMakeOptions.txt
(see CMakeOptions.txt.sample for an example)
You'll need to re-run configure.sh if you create or modify CMakeOptions.txt
EOF


""")

# --------------------------------------------------------------------------------------------------------------------------------
# Step 5 : generate the source file for the executable

if not (Path('app').exists() & Path('app').is_dir()):
    os.mkdir('app')

with open(Path('app') / 'simple_mesh_app.cpp', 'w') as file:
    file.write(
r"""
#include <iostream>
#include <geogram_gfx/gui/simple_mesh_application.h>

int main(int argc, char** argv) {

    GEO::SimpleMeshApplication app("simple_mesh_app");
	app.start(argc,argv);
    return 0;
}
""")
