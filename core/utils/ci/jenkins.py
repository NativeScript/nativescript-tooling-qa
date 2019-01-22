"""
Jenkins utils.
"""
import os

from core.utils.ci.pr_info import PRInfo


class Jenkins(object):
    @staticmethod
    def is_ci():
        jenkins_home = os.environ.get('JENKINS_HOME', '')
        if jenkins_home == '':
            return False
        else:
            return True

    @staticmethod
    def is_pr():
        pr_info = Jenkins.get_pr_info()
        return bool(pr_info.pull_id is not None)

    @staticmethod
    def get_pr_info():
        return PRInfo(pull_id=os.environ.get('ghprbPullId', None),
                      author=os.environ.get('ghprbPullAuthorLogin', None),
                      title=os.environ.get('ghprbPullTitle', None),
                      description=os.environ.get('ghprbPullLongDescription', None),
                      target_branch=os.environ.get('ghprbTargetBranch', None),
                      source_branch=os.environ.get('ghprbSourceBranch', None))
