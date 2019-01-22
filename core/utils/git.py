"""
A wrapper around GitHub commands.
"""
from core.log.log import Log
from core.settings import Settings
from core.utils.file_utils import Folder
from core.utils.run import run


def get_repo_url(repo_url, ssh_clone=False):
    if ssh_clone:
        org = repo_url.split('/')[3]
        repo = repo_url.split('/')[4]
        return 'git@github.com:{0}/{1}.git'.format(org, repo)
    else:
        return repo_url


class Git(object):
    @staticmethod
    def clone(repo_url, local_folder, branch='master'):
        """Clone GitHub repo to local folder.
        :param repo_url: HTTPs url of the repo.
        :param branch: Branch.
        :param local_folder: Local folder to clone the repo.
        """
        if Folder.exists(folder=local_folder):
            Folder.clean(folder=local_folder)
        repo_url = get_repo_url(repo_url=repo_url, ssh_clone=Settings.SSH_CLONE)
        command = 'git clone --depth 1 {0} -b {1} "{2}"'.format(repo_url, branch, str(local_folder))
        Log.info(command)
        result = run(cmd=command)
        assert "fatal" not in result.output, "Failed to clone: " + repo_url
        assert result.exit_code == 0, "Failed to clone: " + repo_url
