from abc import ABC, abstractmethod
from github_quality_analytics.utils import Utils
from github_quality_analytics.instance_manager import InstanceManager
from github import Repository
import datetime

class QualityAnalytics(ABC):
    def __init__(self):
        self.api_manager = InstanceManager.getInstance()
        self.github = self.api_manager.get_github()

    def gather_data(self, repo_name: str, sha: str="") -> list:
        while True:
            try:
                Utils.LOGGER.info("Gathering data for {0}".format(repo_name))
                repo = self.github.get_repo(repo_name)
                output = self.process(repo, sha)
            except Exception as e:
                output = Utils.exception_handler(e)
            finally:
                if not output or output[0] != 'repeat':
                    return output
                self.api_manager.new_github()
                self.github = self.api_manager.get_github()

    @abstractmethod
    def process(self, repo: Repository, sha: str) -> list:
        pass

class FileUsage(QualityAnalytics):
    def __init__(self, phrase: str, only_root: bool = False):
        super().__init__()
        self.phrase = phrase
        self.only_root = only_root

    def process(self, repo: Repository, sha: str) -> list:
        git_tree = Utils.get_git_tree(repo, recursive=not self.only_root)
        output = '1' if Utils.find_config_by_tool_name(self.phrase, git_tree) else '0'
        return [output]


class CodeReviewUsage(QualityAnalytics):
    def __init__(self):
        super().__init__()

    def process(self, repo: Repository, sha: str) -> list:
        all_pulls = repo.get_pulls(state='all')
        latest_pull_date = datetime.datetime(2021, 8, 1)
        output = []
        MAX_TRY = 100
        try_counter = 0
        for pull in all_pulls:
            # pulls should be merged and before 1st of August
            if pull.created_at < latest_pull_date:
                try_counter += 1
                if pull.is_merged():
                    try:
                        review_reqs = pull.get_review_requests()
                        users = review_reqs[0].get_page(0)
                        teams = review_reqs[1].get_page(0)
                        count_review_requests = len(users) + len(teams)
                        pull_number = pull.number
                        count_changed_files = pull.changed_files
                        count_all_reviews = pull.get_reviews().totalCount
                        count_all_review_comments = pull.review_comments
                        count_all_comments = pull.comments
                        count_total_changed_lines = 0
                        for commit in pull.get_commits():
                            count_total_changed_lines += commit.stats.total
                        output.append([pull_number, count_review_requests, count_all_reviews, count_all_review_comments, count_all_comments, count_changed_files, count_total_changed_lines])
                    except Exception as e:
                        print(e)
            Utils.LOGGER.info("Pull {0} of 20".format(len(output)))
            if len(output) == 20 or try_counter == MAX_TRY:
                return output
        return output
