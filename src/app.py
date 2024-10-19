# app.py
# @Author: Dan Bergen, Eva Caro, Sophie Clemens, Marti Zentmaier
# @Date:   2024-06-26
# @Last Modified by:
# @Last Modified time: 

from PluginManager.pluginSuite import PluginSuiteTool
from PluginManager.pluginCreator import pluginCreator
from WorkspaceManager.ws_funcs import is_directory
import subprocess
import os
import shutil
from PluginUtils.S3_connect import S3Client

# Prompts user for plugs 
def main():

    print("Welcome to GailBot plugin suite maker. Type 'help' for a list of commands. ") 
    
    s3_client = S3Client()

    while True:
        # query = input().lower().strip()
        query = input()
        query_split = query.split()
        length_query = len(query_split)

        if query == 'quit':
            print("Exiting...")
            return
        elif query == 'create_suite':
            name = input("Please provide the name you would like to give your plugin suite: ")
            ps = PluginSuiteTool(name)
            suite_creation(ps)
        elif query == 'help':
            cmd_options = '''Command options:
    - quit: exits the program
    - create_suite: initiates the creation of a plugin suite
    - add [ID Number]: adds plugin with respective ID to the suite
    - remove [ID Number]: removes plugin with respective ID from the suite
    - finalize: ensures that the suite is valid and finalizes it 
    - create_plugin: creates a templated plugin on your Desktop
    - upload_plugin [path to folder]: uploads a plugin to the S3 Bucket (WILL REMOVE - EXCLUSIVE UPLOADING FROM WEBSITE)
    - upload_plugin_suite [path to folder]
    - download_plugin [ID] [destination path]
    - download_plugin_suite [ID] [destination path]'''
            print(cmd_options)
        elif query == 'create_plugin':
            name = input("Please provide a unique name for your new plugin: ")
            desc = input("Please describe what your plugin will accomplish: ")
            new_plugin = pluginCreator(name= name, description= desc)
            print(f"Done! Here is the path to the new folder with all the starter files you need to create your plugin: {new_plugin.parent_dir}!")
        elif query_split[0] == 'upload_plugin' and len(query_split) == 2:
            plugin_folder = query_split[1]
            s3_client.upload_plugin(plugin_folder, 'gailbot-plugins')
        elif query_split[0] == 'upload_plugin_suite' and len(query_split) == 2:
            suite_folder = query_split[1]
            s3_client.upload_plugin_suite(suite_folder, 'gailbot-plugins')
        elif query_split[0] == 'download_plugin' and len(query_split) == 3:
            plugin_id = query_split[1]
            destination_folder = query_split[2]
            s3_client.download_file('gailbot-plugins', plugin_id, destination_folder)
        elif query_split[0] == 'download_plugin_suite' and len(query_split) == 3:
            # instead of downloading the files, should only download the docker files, compose, and toml
            suite_id = query_split[1]
            destination_folder = query_split[2]
            s3_client.download_file('gailbot-plugins', suite_id, destination_folder, is_suite=True)
        else:
            print("Initiate suite or plugin creation to continue. ")
       
          
def suite_creation(ps: PluginSuiteTool):
    """
    Queries user for commands for suite creation (add, remove, validate, etc.)
    """
    print(f"Plugin Suite {ps.name} created! Start adding plugins to your suite (by typing 'add [ID]') and enter 'finalize' once all plugins have been added. Enter 'print' to see the plugins that have bbeen added. To remove, type 'remove [ID]'.")
    while True:
        # query = input().lower().strip()
        query = input()
        query_split = query.split()
        length_query = len(query_split)

        if query_split[0] == 'add':
            if length_query == 1:
                id = input("Please provide the ID number of the plugin you wish to add: ")
            else:
                id = query_split[1]
            try:
                ps.add_plugin(id)
                # s3_client.download_file(bucket= "gailbot-plugins", plugin_id= id, destination_folder= )
            except Exception as e:
                print(f"Couldn't add plugin {id}. ")
        elif query == 'print':
            ps.print_plugins()
        elif query == 'finalize':
            if not ps.validate():
                print("The following plugins are listed as requirements but were not provided: \n")
                print('\n'.join(f"{id}" for id in ps.not_included))
                retrieve = input("Do you wish to retrieve these? y/n ")
                if retrieve.lower() == 'y':
                    for plugin in ps.not_included:
                        ps.add_plugin(plugin)
                else:
                    print("Either remove invalid plugins or add required plugins to create a valid plugin suite.")
                    continue
            print("Your suite is valid! Nice!\n")
            ps.finalize()
        elif query_split[0] == 'remove':
            if length_query == 1:
                id = input("Please provide the ID number of the plugin you wish to remove: ")
            else:
                id = query_split[1]
            try:
                ps.remove_plugin(id)
            except Exception as e:
                print(f"Couldn't remove plugin {id}. ")
        else:
            print(f"{query} is not a valid command. Enter 'help' to see the list of acceptable commands. ")


if __name__ == "__main__":
    main()