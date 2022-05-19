from github import Repository, GitTree
import logging

class Utils:
    LOGGER = logging.getLogger('my_logger')
    LOGGER.setLevel(level=logging.DEBUG)
    STREAM_HANDLER = logging.StreamHandler()
    STREAM_HANDLER.setLevel(logging.DEBUG)
    LOG_FORMATTER = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s')
    STREAM_HANDLER.setFormatter(LOG_FORMATTER)
    LOGGER.addHandler(STREAM_HANDLER)

    @staticmethod
    def get_git_tree(repo: Repository, recursive: bool = True) -> GitTree:
        sha = repo.get_commits()[0].sha
        git_tree = repo.get_git_tree(sha, recursive=recursive)
        return git_tree

    @staticmethod
    def find_config_by_tool_name(phrase: str, git_tree: GitTree) -> bool:
        for tree_element in git_tree.tree:
            file_path = tree_element.path
            if phrase.lower() in file_path.lower():
                return True

        return False

    @staticmethod
    def exception_handler(e: Exception) -> list:
        try:
            Utils.LOGGER.error(e)
            if e.data['message'] == 'Repository access blocked':
                value = 'access_blocked'
            elif e.data['message'] == 'Not Found':
                value = 'not_found'
            elif 'No commit found for SHA' in e.data['message']:
                value = 'no_commit_found'
            else:
                value = 'repeat'
        except Exception as e:
            Utils.LOGGER.error("Exception inside except: {}".format(e))
            value = 'error'
        return [value]
