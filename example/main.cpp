#include <iostream>

#include "AppMeta/meta.h"

/**
 * A simple program to show how to use metagen script and how to use generated metadata in code.
 */
int main() {
    std::cout << "Version is "<< APPMETA_VERSION_STR <<"\n";
    std::cout << "Full version is "<< APPMETA_VERSION_FULL_STR <<"\n";
    std::cout << "Build date is "<< APPMETA_BUILD_DATE <<"\n";
    //Sample output (will be different since tags and build date are changing):
    //Version is 1.2.3
    //Full version is 1.2.3-SNAPSHOT
    //Build date is 2021-10-25

    return 0;
}
