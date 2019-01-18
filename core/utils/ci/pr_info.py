# pylint: disable=too-many-arguments
class PRInfo(object):

    def __init__(self, pull_id=None, author=None, title=None, description=None, target_branch=None,
                 source_branch=None):
        self.pull_id = pull_id
        self.author = author
        self.title = title
        self.description = description
        self.target_branch = target_branch
        self.source_branch = source_branch
