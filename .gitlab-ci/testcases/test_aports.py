#!/usr/bin/env python3
# Copyright 2018 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import pytest
import sys
import os

import add_pmbootstrap_to_import_path
import pmb.parse
import pmb.parse._apkbuild


@pytest.fixture
def args(request):
    # Initialize args
    sys.argv = ["pmbootstrap",
                "--aports", os.path.dirname(__file__) + "/../..",
                "--log", "$WORK/log_testsuite_pmaports.txt"
                "chroot"]
    args = pmb.parse.arguments()

    # Initialize logging
    pmb.helpers.logging.init(args)
    request.addfinalizer(args.logfd.close)
    return args


def test_deviceinfo(args):
    """
    Parse all deviceinfo files successfully and run checks on the parsed data.
    """
    # Iterate over all devices
    last_exception = None
    count = 0
    for folder in glob.glob(args.aports + "/device/device-*"):
        device = folder[len(args.aports):].split("-", 1)[1]

        try:
            # Check for successful deviceinfo parsing
            info = pmb.parse.deviceinfo(args, device)

            # deviceinfo_name must start with manufacturer
            name = info["name"]
            manufacturer = info["manufacturer"]
            if not name.startswith(manufacturer) and \
                    not name.startswith("Google"):
                raise RuntimeError("Please add the manufacturer in front of"
                                   " the deviceinfo_name, e.g.: '" +
                                   manufacturer + " " + name + "'")

        # Don't abort on first error
        except Exception as e:
            last_exception = e
            count += 1
            print(device + ": " + str(e))

    # Raise the last exception
    if last_exception:
        print("deviceinfo error count: " + str(count))
        raise last_exception


def test_aports_device(args):
    """
    Various tests performed on the /device/device-* aports.
    """
    for path in glob.glob(args.aports + "/device/device-*/APKBUILD"):
        apkbuild = pmb.parse.apkbuild(args, path)

        # Depends: Require "postmarketos-base"
        if "postmarketos-base" not in apkbuild["depends"]:
            raise RuntimeError("Missing 'postmarketos-base' in depends of " +
                               path)

        # Depends: Must not have firmware packages
        for depend in apkbuild["depends"]:
            if (depend.startswith("firmware-") or
                    depend.startswith("linux-firmware")):
                raise RuntimeError("Firmware package '" + depend + "' found in"
                                   " depends of " + path + ". These go into"
                                   " subpackages now, see"
                                   " <https://postmarketos.org/devicepkg>.")


def test_aports_device_kernel(args):
    """
    Verify the kernels specified in the device packages:
    * Kernel must not be in depends when kernels are in subpackages
    * Check if only one kernel is defined in depends
    * Validate kernel subpackage names
    """
    # Generate list of valid subpackages
    valid_subpackages = ["downstream", "rpi", "rpi2"]
    for path in glob.glob(args.aports + "/main/linux-postmarketos-*"):
        suffix = os.path.basename(path)[len("linux-postmarketos-"):]
        valid_subpackages.append(suffix)

    # Iterate over device aports
    for path in glob.glob(args.aports + "/device/device-*/APKBUILD"):
        # Parse apkbuild and kernels from subpackages
        apkbuild = pmb.parse.apkbuild(args, path)
        device = apkbuild["pkgname"][len("device-"):]
        kernels_subpackages = pmb.parse._apkbuild.kernels(args, device)

        # Parse kernels from depends
        kernels_depends = []
        for depend in apkbuild["depends"]:
            if not depend.startswith("linux-"):
                continue
            kernels_depends.append(depend)

            # Kernel in subpackages *and* depends
            if kernels_subpackages:
                raise RuntimeError("Kernel package '" + depend + "' needs to"
                                   " be removed when using kernel" +
                                   " subpackages: " + path)

        # No kernel
        if not kernels_depends and not kernels_subpackages:
            raise RuntimeError("Device doesn't have a kernel in depends or"
                               " subpackages: " + path)

        # Multiple kernels in depends
        if len(kernels_depends) > 1:
            raise RuntimeError("Please use kernel subpackages instead of"
                               " multiple kernels in depends (see"
                               " <https://postmarketos.org/devicepkg>): " +
                               path)

        # Verify subpackages
        if kernels_subpackages:
            for subpackage in kernels_subpackages:
                if subpackage not in valid_subpackages:
                    raise RuntimeError("Invalid kernel subpackage name '" +
                                       subpackage + "', valid: " +
                                       str(valid_subpackages))