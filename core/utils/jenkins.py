"""
Jenkins utils.
"""
import os


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
        pr_id = os.environ.get('ghprbPullId', '')
        if pr_id == '':
            return False
        else:
            return True
