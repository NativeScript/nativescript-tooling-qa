class ProcessInfo(object):
    def __init__(self,
                 cmd=None,
                 pid=None,
                 exit_code=None,
                 output='',
                 log_file=None,
                 complete=True,
                 duration=None):
        self.commandline = cmd
        self.pid = pid
        self.output = output
        self.exit_code = exit_code
        self.log_file = log_file
        self.complete = complete
        self.duration = duration
