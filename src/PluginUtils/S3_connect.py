# S3_Connect.py
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import toml


class S3Client:
    def __init__(self):
        access_key = "AKIA2J56H6CDIH4K22WK"
        secret_key = "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"
        self.s3_client = boto3.client(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )

    def upload_plugin(self, plugin_folder, bucket):
        self.upload_folder(plugin_folder, bucket, "plugins")

    def upload_plugin_suite(self, suite_folder, bucket):
        try:
            # Extract suite info from the suite_info.toml file
            suite_info = self.extract_plugin_info(
                os.path.join(suite_folder, "suite_info.toml"), is_suite=True
            )
            if suite_info:
                suite_id = suite_info["id"]
                for root, dirs, files in os.walk(suite_folder):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        # Create the S3 key based on the suite ID and the relative path of the file
                        relative_path = os.path.relpath(file_path, suite_folder)
                        s3_key = f"plugin_suites/{suite_id}/{relative_path}"
                        self.s3_client.upload_file(file_path, bucket, s3_key)
                        print(f"File {file_path} uploaded to {bucket}/{s3_key}")
            else:
                print("Suite ID not found in TOML file. Aborting upload.")
        except FileNotFoundError:
            print(f"The folder {suite_folder} was not found")
        except NoCredentialsError:
            print("Credentials not available")
        except ClientError as e:
            print(f"Client error: {e}")
            print(e.response)

    def upload_folder(self, folder, bucket, folder_type):
        # print("going to upload. flder : ", folder)
        try:
            plugin_id = None
            # print("Checking if folder exists:", os.path.exists("/Users/evacaro/Desktop/uniquenameforplugin"))

            # Recursively walk through all files and folders
            for root, _, files in os.walk(folder):
                print("files:", files)
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    print("filepath is ", file_path)

                    # Check for plugin ID in any ".toml" file
                    if file_name.endswith(".toml"):
                        plugin_info = self.extract_plugin_info(file_path)
                        if plugin_info:
                            plugin_id = plugin_info["id"]

                        if not plugin_id:
                            print("Plugin ID not found in TOML file. Aborting upload.")
                            return

                    # Generate the S3 key while preserving the directory structure
                    relative_path = os.path.relpath(file_path, folder)
                    s3_key = f"{folder_type}/{plugin_id}/{relative_path}"

                    # Upload the file to S3
                    print(f"Uploading {file_path} to {bucket}/{s3_key}...")
                    self.s3_client.upload_file(file_path, bucket, s3_key)

        except FileNotFoundError:
            print(f"The file was not found: {file_path}")
        except NoCredentialsError:
            print("AWS credentials not available")
        except ClientError as e:
            print(f"Client error: {e}")
            print(e.response)

    def extract_plugin_info(self, toml_file, is_suite=False):
        try:
            with open(toml_file, "r") as f:
                config = toml.load(f)
                if is_suite:
                    item_info = {
                        "id": config["suite"]["id"],
                        "name": config["suite"]["name"],
                        "description": config["suite"].get("description", ""),
                        "created_by": config["suite"]["created_by"],
                        "access": config["suite"].get("access", "ANY"),
                    }
                else:
                    # item_info = {
                    #     "id": config["plugin"]["id"],
                    #     "name": config["plugin"]["name"],
                    #     "description": config["plugin"].get("description", ""),
                    #     "created_by": config["plugin"]["created_by"],
                    #     "access": config["plugin"].get("access", "ANY"),
                    # }
                    item_info = {
                        "id": config.get("package", {}).get("id"),
                        "name": config.get("package", {}).get("name"),
                        "description": config.get("package", {}).get("description"),
                        # "created_by": config.get("package", {}).get("authors"),
                        # "access": config.get("package", {}).get("access"),
                    }
                return item_info
        except FileNotFoundError:
            print(f"The TOML file {toml_file} was not found")
            return None
        except KeyError as e:
            print(f"Key error: {e}")
            return None
        except toml.TomlDecodeError as e:
            print(f"Error parsing TOML file {toml_file}: {e}")
            return None


    def download_file(self, bucket, plugin_id, destination_folder, is_suite=False):
        try:
            # Check if the destination folder exists
            if not os.path.exists(destination_folder):
                print(f"Error: The folder '{destination_folder}' does not exist. Please provide a valid directory.")
                return  # Abort the operation

            s3_folder = f"plugin_suites/{plugin_id}" if is_suite else f"plugins/{plugin_id}"
            objects = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=s3_folder)
            item_name = None

            if "Contents" in objects:
                for obj in objects["Contents"]:
                    s3_key = obj["Key"]
                    file_name = os.path.basename(s3_key)

                    if file_name.endswith(
                        "suite_info.toml" if is_suite else "plugin_info.toml"
                    ):
                        local_toml_path = os.path.join(destination_folder, file_name)
                        self.s3_client.download_file(bucket, s3_key, local_toml_path)

                        plugin_info = self.extract_plugin_info(local_toml_path, is_suite)
                        if plugin_info:
                            item_name = plugin_info["name"]
                        else:
                            print(
                                f"Error extracting information from {local_toml_path}. Aborting download."
                            )
                            os.remove(local_toml_path)
                            return

                        os.remove(local_toml_path)

                if item_name:
                    item_folder = os.path.join(destination_folder, item_name)
                    os.makedirs(item_folder, exist_ok=True)

                    for obj in objects["Contents"]:
                        s3_key = obj["Key"]
                        file_name = os.path.basename(s3_key)
                        local_path = os.path.join(item_folder, file_name)
                        self.s3_client.download_file(bucket, s3_key, local_path)
                        print(f"File {file_name} downloaded to {local_path}")
                else:
                    print(f"Item name not found in TOML file.")
            else:
                print(
                    f"No files found for {'plugin suite' if is_suite else 'plugin'} {plugin_id} in S3"
                )
        except NoCredentialsError:
            print("Credentials not available")
        except ClientError as e:
            print(f"Client error: {e}")
            print(e.response)
        except FileNotFoundError as e:
            print(f"File not found error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")