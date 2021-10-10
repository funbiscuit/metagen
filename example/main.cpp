#include <iostream>

#include "AppMeta/meta.h"

/**
 * A simple program to show how to use metagen script and how to use generated metadata in code.
 */
int main() {
    std::cout << "Version is " << APPMETA_VERSION_STR << "\n";
    std::cout << "Full version is " << APPMETA_VERSION_FULL_STR << "\n";
    std::cout << "Build date is " << APPMETA_BUILD_DATE << "\n";
    std::cout << "Major.Minor.Patch.Build = " <<
              APPMETA_VERSION_MAJOR << "." <<
              APPMETA_VERSION_MINOR << "." <<
              APPMETA_VERSION_PATCH << "." <<
              APPMETA_VERSION_BUILD << "\n";
    std::cout << "Is snapshot build: " << APPMETA_BUILD_SNAPSHOT << "\n";
    std::cout << "Build commit: " << APPMETA_BUILD_COMMIT << "\n";
    //Sample output (will be different since tags and build date are changing):
    // Version is 1.2.3
    // Full version is 1.2.3-SNAPSHOT
    // Build date is 2021-10-25
    // Major.Minor.Patch.Build = 1.2.3.4
    // Is snapshot build: 1
    // Build commit: 955d5574a1434e1e270dc661bb4ecdd849f541cd

    return 0;
}
