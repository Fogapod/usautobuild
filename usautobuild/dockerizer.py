from .config import Config
from logging  import Logger
from subprocess import Popen, PIPE
import os
import shutil
from pathlib import Path

class Dockerizer:
    def __init__(self, config: Config, logger: Logger):
        self.logger = logger
        self.output_dir = config.output_dir
        self.username = config.docker_username
        self.password = config.docker_password
        self.forkname = config.forkname
        self.build_number = config.build_number

    def copy_dockerfile(self):
        self.logger.debug("Preparing Docker folder")
        if os.path.isdir("Docker"):
            shutil.rmtree("Docker")
        shutil.copytree("local_repo/Docker", "Docker")

    def copy_server_build(self):
        self.logger.debug("Copying server build")
        if os.path.isdir("Docker/server"):
            shutil.rmtree("Docker/server")

        shutil.copytree(Path(self.output_dir, "linuxserver"), "Docker/server")

    def make_images(self):
        self.logger.debug("Creating images...")
        try:
            cmd = Popen(f"docker build -t unitystation/unitystation:{self.build_number} "
                        f"-t unitystation/unitystation:{self.forkname} Docker",
                        stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
            for line in cmd.stdout:
                self.logger.debug(line)

            for line in cmd.stderr:
                raise Exception(line)

            cmd.wait()
        except Exception as e:
            self.logger.error(str(e))
            raise e

    def push_images(self):
        self.logger.debug("Pushing images...")
        try:
            cmd = Popen(f"docker login -p {self.password} -u {self.username}",
                        stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)

            for line in cmd.stdout:
                self.logger.debug(line)
            for line in cmd.stderr:
                raise Exception(line)
            cmd.wait()
        except Exception as e:
            self.logger.error(str(e))
            raise e

        try:
            cmd = Popen("docker push unitystation/unitystation --all-tags",
                        stdout=PIPE,
                        stderr=PIPE,
                        universal_newlines=True,
                        shell=True)
            for line in cmd.stdout:
                self.logger.debug(line)
            for line in cmd.stderr:
                raise Exception(line)
            cmd.wait()

        except Exception as e:
            self.logger.error(str(e))
            raise e


    def start_dockering(self):
        self.logger.debug("Starting docker process")
        self.copy_dockerfile()
        self.copy_server_build()
        self.push_images()
        self.logger.info("Process finished, a new staging build has been deployed and should shortly be present on the server.")
