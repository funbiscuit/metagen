#include <iostream>

#include "AppMeta/meta.h"

/**
 * A simple program to show how to use metagen script and how to use generated metadata in code.
 */
int main() {
    std::cout << "Version is "<< APPMETA_VERSION_STR <<"\n";
    std::cout << "Full version is "<< APPMETA_VERSION_FULL_STR <<"\n";
    //Expected output:
    //Version is 1.2.3
    //Full version is 1.2.3-SNAPSHOT

    return 0;
}
