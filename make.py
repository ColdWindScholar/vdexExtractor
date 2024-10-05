#!/usr/bin/env python3
#
# vdexExtractor
# -----------------------------------------
#
# Anestis Bechtsoudis <anestis@census-labs.com>
# Copyright 2017 by CENSUS S.A. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import subprocess
import sys
import shutil
from shutil import which
from os.path import dirname, basename
sysTools= ["make"]
MODULE_NAME="vdexExtractor"
def call(exe, out=0):
    if isinstance(exe, list):
        cmd = [c_i for c_i in exe if c_i]
    else:
        cmd =  exe
        if os.name == 'posix':
            cmd = cmd.split()
    if os.name != 'posix':
        conf = subprocess.CREATE_NO_WINDOW
    else:
        conf = 0
    try:
        ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, creationflags=conf)


        for i in iter(ret.stdout.readline, b""):
            if out == 0:
                try:
                    out_put = i.decode("utf-8").strip()
                except (Exception, BaseException):
                    out_put = i.decode("gbk").strip()
                print(out_put)
    except subprocess.CalledProcessError as e:
        for i in iter(e.stdout.readline, b""):
            if out == 0:
                try:
                    out_put = i.decode("utf-8").strip()
                except (Exception, BaseException):
                    out_put = i.decode("gbk").strip()
                print(out_put)

        return 2
    except FileNotFoundError:
        return 2
    ret.wait()
    return ret.returncode

def commandExists(cmd):
    return bool(shutil.which(cmd))

def usage():
    print(f"{sys.argv[0]} [gcc|clang|cross-android|clean] (default is gcc) DEBUG (default is false)")
    exit(1)
def build_cross_android():
    if not os.environ.get("NDK"):
        if which("ndk-build"):
            NDK=(dirname(which("ndk-build")))
        else:
            print("[-] Could not detect Android NDK dir")
            exit(1)
    ndk_extra_args=""
    if DEBUG_BUILD == 'true':
        ndk_extra_args+="V=1 NDK_DEBUG=1 APP_OPTIM=debug"
    call([f"{NDK}/ndk-build", "clean"])
    if call([f"{NDK}/ndk-build", ndk_extra_args]) != 0:
        print("[-] android build failed")
        exit(1)
    baseDir="libs"
    if DEBUG_BUILD == 'true':
        baseDir="obj/local"
    for cpuBaseDir in os.walk("libs"):
        cpu=basename(cpuBaseDir)
        shutil.copy(f"{baseDir}/{cpu}/{MODULE_NAME}", f"bin/{MODULE_NAME}-android-{cpu}")

def build(compiler:str=''):
    if compiler == '':
        if not os.environ.get("CC"):
            compiler="gcc"
        else:
            compiler=os.environ.get("CC")
    if call(["make", "clean", "-C", "src"]) != 0:
        print("[-] make clean failed")
        exit(1)
    os.environ.setdefault("CC", compiler)
    os.environ.setdefault("DEBUG", DEBUG_BUILD)
    if call(["make", "-C", "src"]) != 0:
        print("[-] build failed")
        exit(1)

def clean():
    if call(["make", "clean", "-C", "src"]) != 0:
        print("[-] make clean failed")
        exit(1)
    if not os.environ.get("NDK"):
        if which("ndk-build"):
            NDK=(dirname(which("ndk-build")))
            call([f"{NDK}/ndk-build", "clean"])

if __name__ == "__main__":
    # Check that common system tools exist
    for i in sysTools:
        if not commandExists(i):
            print(f'[-] {i} command not found')
            exit(1)
    if len(sys.argv) > 3:
        print("[-] Invalid args")
        exit(1)
    if len(sys.argv) == 1:
        target = ''
        DEBUG_BUILD= 'false'
    elif len(sys.argv) == 2:
        target = sys.argv[1]
        DEBUG_BUILD= 'false'
    elif len(sys.argv) >= 3:
        target = sys.argv[1]
        DEBUG_BUILD = sys.argv[2]
    else:
        usage()
        exit(1)
    if target == '':
        build("")
    elif target in ["gcc","clang"]:
        build(target)
    elif target == 'cross-android':
        build_cross_android()
    elif target == 'clean':
        clean()
    else:
        usage()
    exit(0)

