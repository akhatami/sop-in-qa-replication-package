from __future__ import annotations
from github import Github
from github_quality_analytics.utils import Utils


class InstanceManager:
    __instance = None

    @staticmethod
    def getInstance() -> InstanceManager:
        """ Static access method. """
        if InstanceManager.__instance is None:
            InstanceManager()
        return InstanceManager.__instance

    def __init__(self, keys: list):
        """ Virtually private constructor. """
        if InstanceManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            InstanceManager.__instance = self
            self.keys = keys
            self.index = 0
            self.github = Github(self.keys[self.index])
            Utils.LOGGER.info('Instance manager created')

    def get_github(self) -> Github:
        return self.github

    def new_github(self):
        if self.index + 1 == len(self.keys):
            Utils.LOGGER.info('Max Github instances reached')
        self.index = (self.index + 1) % len(self.keys)
        self.github = Github(self.keys[self.index])
        Utils.LOGGER.info('Using new Github instance index: {}'.format(self.index))
