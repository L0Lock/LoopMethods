# SPDX-License-Identifier: GPL-3.0-or-later
"""
This script automates the release process for a Blender extension.

It provides functionalities to:
- Extract version information from `__init__.py` and `blender_manifest.toml`.
- Manage existing versions and create new releases.
- Create development copies of the extension.
- Build the extension into a zip file using Blender's command line interface.
- Optionally install the extension into Blender.

Usage:
    First make sure to customize these variables according to your setup:
    - PATH_TO_BLENDER: Path to the Blender executable.
    - EXTENSION_FOLDER: Name of the folder containing the extension files.

    python release.py [--dev] [--install]

Options:
    --dev, -D       Create a development build with '_dev' suffix.
    --install, -I   Installs the created extension into Blender.

"""

import os
import re
import shutil
import subprocess
import argparse
from colors import printcol, Red, Cyan, Green, LightYellow, Orange
# noqa E501

EXTENSION_FOLDER = 'loop_methods'
PATH_TO_BLENDER = 'C:\\AppInstall\\Blender\\custom\\blender-4.3.2-stable.32f5fdce0a0a\\blender.exe'


def get_base_path():
    """ Returns the base directory path of the release.py script. """
    return os.path.dirname(os.path.abspath(__file__))


def read_version_init(base_path):
    """ Extracts version from __init__.py into a tuple."""
    init_path = os.path.join(base_path, EXTENSION_FOLDER, '__init__.py')
    if not os.path.exists(init_path):
        raise FileNotFoundError(f"File not found: {init_path}")
    with open(init_path, 'r', encoding="utf-8") as file:
        content = file.read()
    match = re.search(
        r'[\'"]version[\'"]\s*:\s*\((\d+),\s*(\d+),\s*(\d+)\)', content
    )
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in __init__.py")


def read_version_toml(base_path):
    """ Extracts version number from blender_manifest.toml into a tuple."""
    toml_path = os.path.join(
        base_path, EXTENSION_FOLDER, 'blender_manifest.toml'
    )
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"File not found: {toml_path}")

    with open(toml_path, 'r', encoding="utf-8") as file:
        content = file.read()
    match = re.search(
        r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content, re.MULTILINE
    )
    if match:
        return tuple(map(int, match.groups()))
    raise ValueError("Version not found in blender_manifest.toml")


def get_existing_versions(base_path):
    """
    Returns a sorted list of all extensions versions (as tuples) found in the
    Releases folder, omitting dev releases.
    """
    releases_dir = os.path.join(base_path, "Releases")
    if not os.path.exists(releases_dir):
        return []

    version_pattern = re.compile(
        rf'extension_{EXTENSION_FOLDER}_v(\d+)-(\d+)-(\d+)\.zip'
    )
    existing_versions = []

    for filename in os.listdir(releases_dir):
        match = version_pattern.match(filename)
        if match:
            version = tuple(map(int, match.groups()))
            existing_versions.append(version)

    return sorted(existing_versions)


def check_zip_exists(base_path, version):
    """
    Checks whether the zip file for the current version exists in the
    Releases folder.
    """
    releases_dir = os.path.join(base_path, "Releases")
    full_version = f"{version[0]}-{version[1]}-{version[2]}"
    zip_filename = f"extension_{EXTENSION_FOLDER}_v{full_version}.zip"
    return os.path.exists(os.path.join(releases_dir, zip_filename))


def update_version_files(base_path, version):
    """ Updates the version in __init__.py and blender_manifest.toml """
    version_str = f'"version": ({version[0]}, {version[1]}, {version[2]})'
    init_path = os.path.join(base_path, EXTENSION_FOLDER, '__init__.py')
    with open(init_path, 'r', encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r'"version"\s*:\s*\(\d+, \d+, \d+\)', version_str, content)
    with open(init_path, 'w', encoding="utf-8") as file:
        file.write(content)

    version_str = f'version = "{version[0]}.{version[1]}.{version[2]}"'
    toml_path = os.path.join(base_path, EXTENSION_FOLDER, 'blender_manifest.toml')
    with open(toml_path, 'r', encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r'^version\s*=\s*"\d+\.\d+\.\d+"', version_str, content, flags=re.MULTILINE)
    with open(toml_path, 'w', encoding="utf-8") as file:
        file.write(content)


def create_dev_copy(base_path):
    """ Creates a '_dev' copy of the extension with appropriate metadata. """
    dev_folder = EXTENSION_FOLDER + "_dev"
    dev_path = os.path.join(base_path, dev_folder)

    if os.path.exists(dev_path):
        shutil.rmtree(dev_path)
    shutil.copytree(os.path.join(base_path, EXTENSION_FOLDER), dev_path)

    # Modify __init__.py
    init_path = os.path.join(dev_path, '__init__.py')
    with open(init_path, 'r', encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r'("name"\s*:\s*)"([^"]+)"', r'\1"\2_dev"', content)
    content = re.sub(r'("id"\s*:\s*)"([^"]+)"', r'\1"\2_dev"', content)
    with open(init_path, 'w', encoding="utf-8") as file:
        file.write(content)

    # Modify blender_manifest.toml
    toml_path = os.path.join(dev_path, 'blender_manifest.toml')
    with open(toml_path, 'r', encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r'^(name\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE)
    content = re.sub(r'^(id\s*=\s*)"([^"]+)"', r'\1"\2_dev"', content, flags=re.MULTILINE)
    with open(toml_path, 'w', encoding="utf-8") as file:
        file.write(content)

    return dev_folder


def create_zip(base_path, version, source_folder):
    """
    Creates a zip file for the specified Blender extension version.

    Args:
        base_path (str): The base directory path where the Releases folder is located.
        version (tuple): Version number of the extension.
        source_folder (str): The folder name containing the extension source files.

    This function checks for the existence of the Releases directory and creates it if it doesn't exist.
    Then, it constructs a command to invoke Blender's command line interface to build the extension 
    into a zip file, which is stored in the Releases directory. The function logs the creation of 
    the release zip file upon successful execution.
    """

    if not os.path.exists(f'{base_path}\\Releases'):
        os.mkdir(f'{base_path}\\Releases')

    full_version = f"{version[0]}-{version[1]}-{version[2]}"
    output_name = f'extension_{source_folder}_v{full_version}.zip'
    command = f'{PATH_TO_BLENDER} --factory-startup --command extension build '
    command += f'--source-dir "{base_path}\\{source_folder}" '
    command += f'--output-filepath "{base_path}\\Releases\\{output_name}"'
    subprocess.call(command)
    printcol(Green, f"Release zip created: {output_name}")


def install_extension(base_path, version, is_dev):
    """
    Installs a Blender extension from the specified version zip file.

    Args:
        base_path (str): The base directory path of the Releases folder.
        version (tuple): The version of the extension to install.
        is_dev (bool): Whether we install the dev variant of the extension.

    1: tries to uninstall the extension using Blender's CLI.
    2: If the specified version's zip file exists in the Releases directory,
       it proceeds to install it as an extension using Blender's CLI.
    """

    releases_dir = os.path.join(base_path, "Releases")
    full_version = f"{version[0]}-{version[1]}-{version[2]}"
    module = f"loop_methods"

    if is_dev:
        zip_filename = f"extension_{EXTENSION_FOLDER}_dev_v{full_version}.zip"
        command = f"{PATH_TO_BLENDER} --command extension remove {module}_dev"
    else:
        zip_filename = f"extension_{EXTENSION_FOLDER}_v{full_version}.zip"
        command = f"{PATH_TO_BLENDER} --command extension remove {module}"

    printcol(Cyan, f"Removing old extension: {zip_filename}")

    # Run the command without raising an exception on non-zero exit status
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=False
    )

    # Check if there's any output or error
    if result.stdout.strip():
        printcol(LightYellow, result.stdout.strip())

    # Check if stderr contains a message about the addon not being installed
    if result.stderr.strip():
        if "No module named" in result.stderr:
            printcol(Cyan, "Addon not installed, nothing to remove.")
        else:
            printcol(Orange, result.stderr.strip())
    else:
        printcol(Cyan, "Old extension successfully removed!")

    zip_path = os.path.join(releases_dir, zip_filename)
    if not os.path.exists(zip_path):
        printcol(Red, f"Error: Zip file not found: {zip_path}")
        return
    command = f"{PATH_TO_BLENDER} --command extension install-file \
        --repo user_default --enable {zip_path}"
    printcol(Cyan, f"Installing extension: {zip_filename}")
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, check=True
    )
    if result.stdout.strip():
        printcol(LightYellow, result.stdout.strip())
    if result.stderr.strip():
        printcol(Orange, result.stderr.strip())
    else:
        printcol(Green, "Installation completed.")


def main():
    """
    Main function that orchestrates the Blender extension release process.

    This function parses command-line arguments to determine the mode of operation, 
    checks the existence of required files and directories, and manages versioning 
    and packaging for the Blender extension. It supports creating both standard and 
    development builds, updating version files, and optionally installing the 
    extension into Blender.

    Command-line Arguments:
        --dev, -D: Create a development build with '_dev' suffix.
        --install, -I: Installs the created extension into Blender.

    Workflow:
    - Validates the presence of the Blender executable and the extension directory.
    - Reads and compares version information from versioning files.
    - Checks if a release already exists for the current version and prompts the user 
      to overwrite, increment the version, or cancel.
    - Handles cleanup of old development builds and creates new ones if needed.
    - Builds the extension into a zip file.
    - Optionally installs the extension into Blender.

    Raises:
        FileNotFoundError: If the Blender executable or the extension directory is not found.
        ValueError: If the version format is invalid.
    """
    parser = argparse.ArgumentParser(description="Blender Extension Release Script")
    parser.add_argument("--dev", "-D", action="store_true", help="Create a development build with '_dev' suffix.")
    parser.add_argument("--install", "-I", action="store_true", help="Installs the created extension into Blender")
    args = parser.parse_args()

    base_path = get_base_path()

    if not os.path.isfile(PATH_TO_BLENDER):
        printcol(Red, f"Error: Blender Executable not found in:\n    `{PATH_TO_BLENDER}`")
        return
    elif not os.path.isdir(os.path.join(base_path, EXTENSION_FOLDER)):
        printcol(Red, f"Error: Extension not found in:\n    `{base_path}\\{EXTENSION_FOLDER}`")
        return
    else:
        printcol(Cyan, "Found Blender Executable and Extension. Proceeding!")

    version_init = read_version_init(base_path)
    # version_toml = read_version_toml(base_path)

    # Check if zip exists for the current version
    if check_zip_exists(base_path, version_init) and not args.dev:
        existing_versions = get_existing_versions(base_path)

        # Filter versions starting from the current version
        starting_index = existing_versions.index(version_init)
        versions_from_current = existing_versions[starting_index:]

        # Display versions from the current one onward
        existing_versions_str = [
            f"{v[0]}.{v[1]}.{v[2]}{' (current)' if v == version_init else ''}"
            for v in versions_from_current
        ]

        printcol(Orange, f"A release with version \
            {version_init[0]}.{version_init[1]}.{version_init[2]} \
            already exists."
        )
        printcol(LightYellow, f"Existing versions from current: \
            {', '.join(existing_versions_str)}"
        )

        while True:
            response = input("Do you want to \
                (O)verwrite, \
                (I)ncrement version, or \
                (C)ancel? (O/I/C): ").strip().lower()

            if response == 'o':
                break  # Proceed with overwriting
            elif response == 'i':
                new_version = input("Enter new version (X.Y.Z): ").strip()
                try:
                    version_tuple = tuple(map(int, new_version.split('.')))
                    if len(version_tuple) != 3:
                        raise ValueError
                    update_version_files(base_path, version_tuple)
                    version_init = version_tuple
                    break
                except ValueError:
                    printcol(Orange, "Invalid version format. Try again.")
            elif response == 'c':
                printcol(LightYellow, "Operation canceled.")
                return
            else:
                printcol(Orange, "Invalid input. Please enter O, I, or C.")

    elif args.dev:
        # Define paths
        dev_folder = os.path.join(base_path, EXTENSION_FOLDER + "_dev")
        releases_dir = os.path.join(base_path, "Releases")

        # Remove the dev folder if it exists
        if os.path.exists(dev_folder):
            printcol(Orange, f"Removing old dev folder: {dev_folder}")
            shutil.rmtree(dev_folder)

        # Find and delete any existing _dev zip file
        version_pattern = re.compile(rf'extension_{EXTENSION_FOLDER}_dev_v\d+-\d+-\d+\.zip')
        dev_zip_files = [f for f in os.listdir(releases_dir) if version_pattern.match(f)]
        
        for dev_zip in dev_zip_files:
            dev_zip_path = os.path.join(releases_dir, dev_zip)
            printcol(Orange, f"Removing old dev zip: {dev_zip_path}")
            os.remove(dev_zip_path)

        printcol(Cyan, "Running in development mode. Overwriting dev zip if exists.")

    source_folder = create_dev_copy(base_path) if args.dev else EXTENSION_FOLDER
    create_zip(base_path, version_init, source_folder)

    if args.install:
        install_extension(base_path, version_init, args.dev)

if __name__ == '__main__':
    main()
