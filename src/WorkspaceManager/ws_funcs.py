# ws_funcs.py
# @Author: Muhammad Umair
# @Date:   2023-01-08 16:28:03
# @Last Modified by:   Dan Bergen, Eva Caro, Sophie Clemens, Marti Zentmaier
# @Last Modified time: 2024-06-26

from enum import Enum
from typing import List, Dict
import os
import glob
import shutil
import itertools
from pathlib import Path
import subprocess

import json
import yaml
import toml
import csv



class CMD_STATUS(Enum):
    RUNNING = 0
    FINISHED = 1
    STOPPED = 2
    ERROR = 3
    NOTFOUND = 4


def is_directory(dir_path: str) -> bool:
    """
    Determine if the given path is a directory.

    Args:
        dir_path (str): directory path to check

    Returns:
        bool: true if the directory path is valid, false if not
    """
    try:
        return Path(dir_path).is_dir()
    except Exception as e:
        # logger.error(dir_path, exc_info=e)
        return False


def is_file(file_path: str) -> bool:
    """
    Determine if the given path is a file.

    Args:
        file_path (str): file path to check

    Returns:
        bool: true if the file path is valid, false if not
    """
    try:
        return Path(file_path).is_file()
    except Exception as e:
        # logger.error(file_path, exc_info=e)
        return False


def num_items_in_dir(
    path: str, extensions: List[str], recursive: bool = False, only_dirs: bool = False
) -> int:
    """
    Determine the number of files in the directory.

    Args:
        path (str): Path to the directory.
        extensions (List[str]): Specific file extensions to look for.
            Ex: ["pdf"]. '*' is a wildcard and considers all extensions.
            Does not consider sub-directories. Default is ["*"].
        recursive (bool): True to check subdirectories, False otherwise.
            Default is False.
        only_dirs (bool): Only applies to directories.

    Returns:
        int: number of files in the directory
    """
    try:
        return len(paths_in_dir(path, extensions, recursive, only_dirs))
    except Exception as e:
        # logger.error(e)
        return False


def is_path(source: str) -> bool:
    """
    Checks whether a given string is a valid path.

    Args:
        source (str): the path to check if it is valid or not

    Returns:
        bool: true if the path is a file or directory
    """
    return is_file(source) or is_directory(source)



def get_subfiles(path):
    subfiles = []

    # Walk through the directory recursively
    for root, dirs, files in os.walk(path):
        for file in files:
            # Get the full path to the file
            file_path = os.path.join(root, file)
            subfiles.append(file_path)

    return subfiles


def subdirs_in_dir(dir_path: str, recursive: bool = False) -> List[str]:
    """
    Get paths of subdirectories in the directory.

    Args:
        dir_path (str): Directory path to search for subdirectories.
        recursive (bool): True to check subdirectories, False otherwise.
            Default is False.

    Returns:
        List[str]: List of paths to subdirectories in the directory
    """
    try:
        return paths_in_dir(path=dir_path, filter=None, recursive=recursive)
    except Exception as e:
        # logger.error(e)
        return []


def num_subdirs(dir_path: str, recursive: bool = False) -> int:
    """
    Get the number of subdirectories in the directory.

    Args:
        dir_path (str): Directory path to count subdirectories in.
        recursive (bool): True to check subdirectories, False otherwise.
            Default is False.

    Returns:
        int: Number of subdirectories in the directory
    """
    try:
        return len(subdirs_in_dir(dir_path, recursive))
    except Exception as e:
        # logger.error(e)
        return False


def get_name(path: str) -> str:
    """
    Given the path, returns the name of the file or directory without extension.

    Args:
        path (str): Path to a file or directory.

    Returns:
        str: Name of the file or directory without extension.
    """
    try:
        dir_path, file_name = os.path.split(path)
        if file_name:
            return os.path.splitext(os.path.basename(path))[0]
        else:
            return os.path.basename(dir_path)
    except Exception as e:
        # logger.error(e)
        return False


def get_extension(path: str) -> str:
    """
    Given the path to the file, return the extension of the file.

    Args:
        path (str): Path to a file.

    Returns:
        str: Extension of the file.
    """
    try:
        return os.path.splitext(os.path.basename(path))[1][1:]
    except Exception as e:
        # logger.error(e)
        return False


def get_parent_path(path: str) -> str:
    """
    Given the path to the file, returns the path to the file's parent directory.

    Args:
        path (str): Path to a file.

    Returns:
        str: Path to the file's parent directory.
    """
    try:
        return str(Path(path).parent.absolute())
    except Exception as e:
        # logger.error(e)
        return False


def get_size(path: str) -> bytes:
    """
    Given the path to the file, return the file size in bytes.

    Args:
        path (str): Path to a file or directory.

    Returns:
        bytes: Size of the file in bytes.
    """
    try:
        if is_file(path):
            return os.path.getsize(path)
        else:
            return sum([os.path.getsize(p) for p in paths_in_dir(path, recursive=True)])
    except Exception as e:
        # logger.error(e)
        return False


def make_dir(path: str, overwrite: bool = False):
    """
    Given the path, create a directory.

    Args:
        path (str): Path to the directory to be created.
        overwrite (bool): True to overwrite the directory if it exists, False otherwise.

    Returns:
        None
    """
    try:
        if is_directory(path) and overwrite:
            delete(path)
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        # logger.error(e)
        return False


def move(src_path: str, tgt_path: str) -> str:
    """
    Move the file from the source path to the target path.

    Args:
        src_path (str): Source path of the file to be moved.
        tgt_path (str): Target path where the file will be moved to.

    Returns:
        str: The new path of the moved file.
    """
    try:
        return shutil.move(src_path, tgt_path)
    except Exception as e:
        # logger.error(e)
        return False


def copy(src_path, tgt_path: str) -> str:
    """
    Copy the file from the source path to the target path.

    Args:
        src_path (str): Source path of the file to be copied.
        tgt_path (str): Target path where the file will be copied to.

    Returns:
        str: The new path of the copied file.
    """
    try:
        if is_file(src_path):
            return shutil.copy2(src_path, tgt_path)
        elif is_directory(src_path):
            return shutil.copytree(src_path, tgt_path, dirs_exist_ok=True)
        # else:
            # logger.error("not a valid file path")
    except Exception as e:
        # logger.error(e)
        return False


def rename(src_path, new_name: str) -> str:
    """
    Rename the file in the source path to the new name.

    Args:
        src_path (str): Source path of the file to be renamed.
        new_name (str): New name for the file.

    Returns:
        str: The new path of the renamed file.
    """
    try:
        return str(Path(src_path).with_name(new_name).resolve())
    except Exception as e:
        # logger.error(e)
        raise FileExistsError


def delete(path: str) -> None:
    """
    Given a path, delete the file or directory.

    Args:
        path (str): Path to the file or directory to be deleted.

    Returns:
        None
    """
    try:
        if is_file(path):
            Path(path).unlink(missing_ok=True)
        elif is_directory(path):
            shutil.rmtree(path)
        else:
            # logger.error("not a valid path")
            return False
    except Exception as e:
        # logger.error(e)
        return False


def read_json(path: str) -> List[dict]:
    """
    Given a path, read the JSON data stored in the file and return it as a dictionary.

    Args:
        path (str): Path to the JSON file.

    Returns:
        Dict: Dictionary containing the JSON data.
    """
    if is_file(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        raise FileExistsError


def write_json(path: str, data: List[Dict], overwrite: bool = True) -> None:
    """
    Given the path to a file and a list of dictionaries, output the data to the file in JSON format.

    Args:
        path (str): Path to the JSON file.
        data (List[Dict]): List of dictionaries to be stored in the JSON file.
        overwrite (bool): True to overwrite the file if it exists, False to update it.

    Returns:
        None
    """
    if not overwrite:
        d = read_json(path)
        d.update(data)
    else:
        d = data
    try:
        with open(path, "w+") as f:
            json.dump(d, f)
    except Exception as e:
        raise Exception(e)


def read_txt(path: str) -> List:
    """
    Given the path to a text file, return the content of the file as a list of strings.

    Args:
        path (str): Path to the text file.

    Returns:
        List: List of strings containing the file's content.
    """
    if is_file(path):
        with open(path, "r") as f:
            text = f.readlines()
        text = [s.strip() for s in text]
        return text
    else:
        raise FileExistsError


def write_txt(path: str, data: List, overwrite: bool = True) -> bool:
    """
    Given the path to a text file and a list of data, output the list data to the file.

    Args:
        path (str): Path to the text file.
        data (List): List of data to be written to the file.
        overwrite (bool): True to overwrite the file if it exists, False to append to it.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    mode = "w+" if overwrite else "a"
    data = [s + "\n" for s in data]
    try:
        with open(path, mode) as f:
            f.writelines(data)
    except Exception as e:
        raise FileExistsError


def read_yaml(path: str) -> Dict:
    """
    Given a path to a YAML file, return a dictionary representation of the data stored in the YAML file.

    Args:
        path (str): Path to the YAML file.

    Returns:
        Dict: Dictionary containing the data from the YAML file.
    """

    if is_file(path):
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                if not data:
                    data = yaml.unsafe_load(path)
                if not isinstance(data, dict):
                    # logger.error(
                        # f"the data is not a valid dictionary: {data}, the file path is {path}"
                    # )
                    raise Exception
                return data
        except Exception as e:
            print(e)
            # logger.error(e, exc_info=e)
    else:
        # logger.error("not a valid YAML file")
        raise FileExistsError


def write_yaml(path: str, data: Dict, overwrite: bool = True) -> bool:
    """
    Given a path to a YAML file and data stored in a dictionary, output the data in YAML format to the file.

    Args:
        path (str): Path to the YAML file.
        data (Dict): Dictionary containing the data to be written to the YAML file.
        overwrite (bool): True to overwrite the file if it exists, False to update it.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    data = dict(data)
    if not overwrite:
        previous_data = read_yaml(path)
        previous_data.update(data)
        previous_data.update(data)
    else:
        previous_data = data
    try:
        with open(path, "w+") as f:
            yaml.dump(previous_data, f)
    except Exception as e:
        raise FileExistsError


def read_toml(path: str) -> Dict:
    """
    Given the path to a TOML file, return a dictionary representation of the data stored in the TOML file.

    Args:
        path (str): Path to the TOML file.

    Returns:
        Dict: Dictionary containing the data from the TOML file.
    """
    if is_file(path):
        return toml.load(path)
    else:
        # logger.error("not a valid TOML file")
        raise FileExistsError


def write_toml(path: str, data: Dict) -> bool:
    """
    Given the path to a TOML file and data stored in a dictionary, output the data in TOML format to the file.

    Args:
        path (str): Path to the TOML file.
        data (Dict): Dictionary containing the data to be written to the TOML file.

    Returns:
        bool: True if the operation is successful, False otherwise.
    """
    try:
        with open(path, "w+") as f:
            toml.dump(data, f)
    except Exception as e:
        raise FileExistsError


def write_csv(path: str, data: List[Dict[str, str]]):
    """
    Write data to a CSV file.

    Args:
        path (str): Path to the CSV file.
        data (List[Dict[str, str]]): List of dictionaries to be written to the CSV file.
    """
    if not data or len(data) == 0:
        with open(path, mode="w+", newline="") as file:
            pass
        return
    fields = list(data[0].keys())
    # Write the data to the CSV file
    with open(path, mode="w+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def read_csv(path: str) -> List[Dict[str, str]]:
    """
    Read data from a CSV file and return it as a list of dictionaries.

    Args:
        path (str): Path to the CSV file.

    Returns:
        List[Dict[str, str]]: List of dictionaries containing the data from the CSV file.
    """
    data = []
    with open(path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def run_cmd(cmd: List[str]) -> int:
    """
    Run a shell command and obtain a process identifier.

    Args:
        cmd (List[str]): A list of strings that stores the command.

    Returns:
        int: the return code of the process
    """
    cmd = " ".join(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode



def copy_dir_files(src_folder, dest_folder):
    """
    Copy files from the source folder to the destination folder recursively.

    Args:
        src_folder (str): The path to the source folder.
        dest_folder (str): The path to the destination folder.
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Walk through the source directory tree
    for root, dirs, files in os.walk(src_folder):
        # Create the corresponding subdirectories in the destination folder
        dest_root = root.replace(src_folder, dest_folder)
        for dir_name in dirs:
            dest_dir = os.path.join(dest_root, dir_name)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

        # Copy the files to the destination folder
        for filename in files:
            src_path = os.path.join(root, filename)
            dest_path = os.path.join(dest_root, filename)
            shutil.copy2(src_path, dest_path)
