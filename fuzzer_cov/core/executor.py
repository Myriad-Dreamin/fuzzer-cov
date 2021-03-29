
import subprocess

from .container import BuildContainer
from .logger import Logger

class CommandExecutor(object):
    def __init__(self, container: BuildContainer):
        self.logger = container.resolve(Logger)
    
    def must_exec(self, cmd, silent: int=1):
        code, out = self.exec(cmd, silent)
        if code:
            raise Exception(f"command executor exit with non-zero code: {code}")
        return out
    
    def exec(self, cmd, silent: int=1):

        self.logger.info(f"CMD: {cmd}", { 'cmd': cmd })

        process = subprocess.Popen(cmd, stdin=None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        lines = []
        mx = 0
        if silent == 2:
            print("")
        for stdout_line in iter(process.stdout.readline, ""):
            stdout_line = stdout_line.rstrip('\n')
            if silent == 0:
                print(stdout_line)
            elif silent == 2:
                mx = max(mx, len(stdout_line))
                if 'warning' in stdout_line.lower():
                    print((" "*mx)+"\r"+stdout_line)
                else:
                    print((" "*mx)+"\r"+stdout_line, end='')
            lines.append(stdout_line)
        process.stdout.close()
        exit_code = process.wait()
        if silent == 2:
            print("")

        if exit_code:
            self.logger.info(f"    Non-zero exit status '{exit_code}' for CMD: {cmd}", { 'exit_code': exit_code, 'cmd': cmd })
        return exit_code, lines
