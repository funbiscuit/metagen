#!/usr/bin/python3
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time

LOCK_FILENAME = "metagen.lock"
CONFIG_FILENAME = "metagen.json"

parser = argparse.ArgumentParser(description="Arg parser")
parser.add_argument('work_dir')
parser.add_argument('-t', dest='timeout', help='How much to wait for another instance to finish (in seconds)')
# 1s is more than enough
parser.set_defaults(timeout=1)
args = parser.parse_args()

if not os.path.exists(args.work_dir):
    print("Working directory %s does not exist!" % args.work_dir)
    sys.exit(-1)

os.chdir(args.work_dir)

if not os.path.exists(CONFIG_FILENAME):
    print("Working directory %s must contain '%s'!" % (args.work_dir, CONFIG_FILENAME))
    sys.exit(-1)

CMAKE_TEMPLATE = """# THIS IS AUTOGENERATED CMAKE FILE, DO NOT MODIFY
cmake_minimum_required(VERSION 3.1)

project({lib} LANGUAGES C)

add_library({lib} STATIC ${{CMAKE_CURRENT_SOURCE_DIR}}/src/meta.c)
target_include_directories({lib} PUBLIC ${{CMAKE_CURRENT_SOURCE_DIR}}/include)
{sources}
"""

HEADER_TEMPLATE = """/**
 * THIS IS AUTOGENERATED HEADER, DO NOT MODIFY
 * @date {date}
 */

#ifndef {header_prefix}_GENERATED_META_H
#define {header_prefix}_GENERATED_META_H

{body}

#endif //{header_prefix}_GENERATED_META_H
"""

SOURCE_TEMPLATE = """/**
 * THIS IS AUTOGENERATED SOURCE, DO NOT MODIFY
 * @date {date}
 */

#include "{header_path}"
"""


class GitVersionResult:
    def __init__(self, version, full_version, commit_hash):
        self.ver = version
        self.ver_git = full_version
        self.commit_hash = commit_hash
        self.exact = version == full_version
        self.build = 0

        p = re.compile(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?')
        m = p.match(version)
        self.major = None
        self.minor = None
        self.patch = None
        if m:
            self.major = m.group(1)
            self.minor = m.group(2)
            self.patch = m.group(3)
        if self.major is None:
            self.major = '0'
        if self.minor is None:
            self.minor = '0'
        if self.patch is None:
            self.patch = '0'
        self.major = int(self.major)
        self.minor = int(self.minor)
        self.patch = int(self.patch)
        self.ver = "v%d.%d.%d" % (self.major, self.minor, self.patch)
        self.ver_full = self.ver
        if not self.exact:
            self.ver_full += "-SNAPSHOT"

        # get build number
        p = re.compile(r'^-(\d+)')
        m = p.match(self.ver_git[len(version):])
        if m:
            self.build = int(m.group(1))


def get_version_from_git():
    version = "0.0.0"
    full_version = "0.0.0-0-"
    commit_hash = ""
    try:
        # get actual version
        res = subprocess.check_output(
            "git describe --tags --match \"v*\" --abbrev=0"
        ).decode("utf-8")
        version = res[1:].strip()
        # get abbreviated to detect whether current commit is tagged
        res = subprocess.check_output(
            "git describe --tags --match \"v*\""
        ).decode("utf-8")
        full_version = res[1:].strip()
        # get current commit hash
        commit_hash = subprocess.check_output("git rev-parse HEAD").decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print("Failed to get version from git")
    return GitVersionResult(version, full_version, commit_hash)


def process_win_rc_template(template_filename, output_dir, ver):
    out_filename = output_dir + '/' + template_filename
    with open(template_filename) as win_rc_template, \
            open(out_filename, "w") as out_file:
        data = win_rc_template.read()
        ver_nums = r'\1 %d,%d,%d,%d' % (ver.major, ver.minor, ver.patch, ver.build)
        ver_str = r'\1 "%d.%d.%d.%d"' % (ver.major, ver.minor, ver.patch, ver.build)

        win_rc_template = re.sub(r'^(\s*FILEVERSION\s*) (.*)', ver_nums, data, flags=re.MULTILINE)
        win_rc_template = re.sub(r'^(\s*PRODUCTVERSION\s*) (.*)', ver_nums, win_rc_template, flags=re.MULTILINE)
        win_rc_template = re.sub(r'^(.*"FileVersion",\s*) (.*)', ver_str, win_rc_template, flags=re.MULTILINE)
        win_rc_template = re.sub(r'^(.*"ProductVersion",\s*) (.*)', ver_str, win_rc_template, flags=re.MULTILINE)
        out_file.write(win_rc_template)


def get_source_entry(project_name, source_name):
    return 'target_sources({lib} INTERFACE ${{CMAKE_CURRENT_SOURCE_DIR}}/src/{file})' \
        .format(lib=project_name, file=source_name)


def process_config():
    ver = get_version_from_git()
    print("Using version %s" % ver.ver_full)
    config = json.load(configFile)
    output = config["output"]
    project_name = config["project_name"]

    include_path = output + "/include/" + project_name
    src_path = output + "/src"
    os.makedirs(include_path, exist_ok=True)
    os.makedirs(src_path, exist_ok=True)
    win_rc_filename = None
    build_date = "{:%Y-%m-%d}".format(datetime.date.today())

    if "win_rc_template" in config:
        win_rc_filename = config["win_rc_template"]
        process_win_rc_template(win_rc_filename, src_path, ver)

    with open(output + "/CMakeLists.txt", "w") as cmakeLists:
        sources = ''
        if win_rc_filename is not None:
            sources += get_source_entry(project_name, win_rc_filename)
        cmakeLists.write(CMAKE_TEMPLATE.format(lib=project_name, sources=sources))
        cmakeLists.close()

    with open(include_path + "/meta.h", "w") as header:
        defines = {
            "VERSION_STR": ver.ver,
            "VERSION_FULL_STR": ver.ver_full,
            "VERSION_MAJOR": ver.major,
            "VERSION_MINOR": ver.minor,
            "VERSION_PATCH": ver.patch,
            "VERSION_BUILD": ver.build,
            "VERSION_IS_SNAPSHOT": not ver.exact,
            "BUILD_DATE": build_date,
            "BUILD_COMMIT": ver.commit_hash,
        }

        body = ""

        for key, value in sorted(defines.items()):
            body += "#define %s_%s " % (project_name.upper(), key)
            if type(value) == str:
                body += "\"%s\"" % value
            elif type(value) == int or type(value) == bool:
                body += "%d" % int(value)
            body += "\n"

        header.write(HEADER_TEMPLATE.format(header_prefix=project_name.upper(),
                                            body=body,
                                            date=build_date))
        header.close()

    with open(src_path + "/meta.c", "w") as src:
        build_date = "{:%Y-%m-%d}".format(datetime.date.today())

        src.write(SOURCE_TEMPLATE.format(header_path=project_name + '/meta.h',
                                         date=build_date))
        src.close()


try:
    lockFile = open(LOCK_FILENAME, "x")
    lockFile.close()

    with open(CONFIG_FILENAME) as configFile:
        process_config()
except FileExistsError as e:
    start = time.time()
    # if lock file exist, there are two options: another instance is running or it has crashed
    # if this is the first option - just wait until another instance finishes its job and
    # report that files were created by it (not treated as error)
    # if in `timeout` seconds another instance doesn't finish - there is a good chance it has crashed
    # and left its lock file in place. Report this as error and tell user to manually delete lock file
    # Usually runtime of this script is less than a second
    print("Waiting up to %0.2f seconds for another instance to finish..." % float(args.timeout))
    while os.path.isfile(LOCK_FILENAME) and time.time() < start + float(args.timeout):
        time.sleep(0.1)
    if os.path.isfile(LOCK_FILENAME):
        print("Another instance did not finish in specified amount of time, exiting.\n" +
              "If you are sure that another instance is not running, manually delete " +
              "lock file '" + LOCK_FILENAME + "' from working directory.")
        print("If you are sure that you need more time for generation send it as argument:")
        print("python metagen.py -t=[timeout in seconds] [work_dir]")
        sys.exit(-1)
    else:
        print("Files were created by another instance, exiting.\n" +
              "You can restart script if needed.")
        sys.exit(0)
finally:
    if os.path.exists(LOCK_FILENAME):
        os.remove(LOCK_FILENAME)
