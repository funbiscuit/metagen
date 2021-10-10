cmake_minimum_required(VERSION 3.1)
project(metagen_example)

set(CMAKE_CXX_STANDARD 11)

# compile resources
find_package( PythonInterp 3.0 REQUIRED )
execute_process(COMMAND ${PYTHON_EXECUTABLE}
        ${PROJECT_SOURCE_DIR}/../metagen.py #path to python script that builds meta info
        ${PROJECT_SOURCE_DIR}/res           #work directory where generated files are stored
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(metagen_example main.cpp)

#meta information will be compiled in res/meta folder (it is specified in res/metagen.json)
#we only need to add it as subdirectory and link to created library
#name of the library is specified in metagen.json
add_subdirectory(res/meta)
target_link_libraries(metagen_example PRIVATE AppMeta)
