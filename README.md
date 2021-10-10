## Metadata generator for C/C++

A simple cross-platform metadata generator for C/C++ programs. Works on any platform with Python 3.x.

## What's generated

Generates version defines based on closest reachable tag in git repository Format of git tag should be vX.Y.Z where Y
and Z (with corresponding dots) are optional (treated as 0 if not present). If no git tag is available or even git is
not available, generated version will be 0.0.0. If tag is not placed on current commit, "-SNAPSHOT" will be appended

### C/C++ defines

C/C++ defines are added to meta.h header file. Include it to your project to access generated values.

| define                   | description                                                                                                    |
|--------------------------|----------------------------------------------------------------------------------------------------------------|
| APPMETA_VERSION_STR      | Version string. Based on latest reachable tag from current commit. In format vX.Y.Z (e.g. v2.1.3)              |
| APPMETA_VERSION_FULL_STR | Full version string (same as version, but -SNAPSHOT is added if built from non tagged commit)                  |
| APPMETA_VERSION_MAJOR    | Major version integer (e.g. 2)                                                                                 |
| APPMETA_VERSION_MINOR    | Minor version integer (e.g. 1)                                                                                 |
| APPMETA_VERSION_PATCH    | Patch version intgerer (e.g. 3)                                                                                |
| APPMETA_VERSION_BUILD    | Build integer. It is number of commits which were added since last version tag (0 if current commit is tagged) |
| APPMETA_BUILD_SNAPSHOT   | 0 if current commit has tag, 1 otherwise                                                                       |
| APPMETA_BUILD_DATE       | String of build date in ISO8601 format (YYYY-MM-DD)                                                            |
| APPMETA_BUILD_COMMIT     | String with current commit hash                                                                                |

## How to use

It is the simplest to use this builder with CMake project.

Suppose you have `metagen.py` located at `./libs/metagen/metagen.py`.

Suppose in CMakeLists.txt you create your executable:

~~~
add_executable(YourExecutableName)
~~~

In CMakeLists.txt add following code:

~~~
find_package( PythonInterp 3.0 REQUIRED )

#if you put your meta files not in ./res folder make changes here
execute_process(COMMAND ${PYTHON_EXECUTABLE}
        ${PROJECT_SOURCE_DIR}/libs/metagen/metagen.py #path to python script that builds metadata
        ${PROJECT_SOURCE_DIR}/res                     #work directory where metadata config is stored
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

#meta information will be compiled in res/meta folder (it is specified in res/metagen.json)
#we only need to add it as subdirectory and link to created library
#name of the library is specified in metagen.json
add_subdirectory(res/meta)
target_link_libraries(metagen_example PRIVATE AppMeta)
~~~

It runs python script to generate all required files, and then you just write two lines to include everything in your
project.

You need to place `metagen.json` inside `res` directory in your project root. This file has the following format:

~~~
{
  // in output you should store the name of build folder. all generated files are placed there
  "output" : "meta",
  // project_name is used to prepend header defines so it doesn't collide with any of your defines
  // it is also used to name library that you'll need to link your executable
  "project_name" : "AppMeta",
  // win_rc_template is path to template file for windows resource generation
  // it is just a normal resource file, but all versions will be replaced with generated ones
  // original file is not modified, generated is put into output directory
  "win_rc_template": "win.rc"
}
~~~

Don't forget to remove comments if you use this sample (json doesn't support them).

In your code you can get version information by accessing one of the defines:

~~~
#include "AppMeta/meta.h"
#include <iostream>

// ...

std::cout << "Version is "<< APPMETA_VERSION_STR <<"\n";
std::cout << "Full version is "<< APPMETA_VERSION_FULL_STR <<"\n";
~~~

Examples
--------

A fully functional CMake project is available in `example` directory to show how metadata is generated and accessed in
code.
