import errno
import re

import exc
import proc


# Public classes


class BenchResult(proc.CallResult):
    """Contains the results of a benchmark."""

    def __init__(self, proc_name, exit_code, stdout=None, stderr=None, max_memory=0):
        """
        :param str proc_name : Name of the called process.
        :param int exit_code : Exit code.
        :param str stdout : Standard output.
        :param str stderr : Standard error.
        :param long max_memory : Max memory used by the process.
        """
        super(BenchResult, self).__init__(proc_name=proc_name,
                                          exit_code=exit_code,
                                          stdout=stdout,
                                          stderr=stderr)

        self.max_memory = max_memory

    @staticmethod
    def create_with(call_result, max_memory=0):
        """Factory method.

        :param proc.CallResult call_result : CallResult instance.
        :param long max_memory : Max memory.
        :rtype : BenchResult
        """
        return BenchResult(proc_name=call_result.proc_name,
                           exit_code=call_result.exit_code,
                           stdout=call_result.stdout,
                           stderr=call_result.stderr,
                           max_memory=max_memory)


# Public functions


def benchmark(args, timeout=None):
    """Runs a benchmark with the specified arguments.

    :param list[str] args : Process arguments.
    :param float timeout : Timeout (s).
    :rtype : BenchResult
    :return Benchmark result.
    """
    exc.raise_if_falsy(args=args)

    bench_args = [proc.find_executable('time'), '-lp']
    bench_args.extend(args)

    call_result = proc.call(bench_args, proc.OutputAction.RETURN, timeout)

    stderr = call_result.stderr
    exc.raise_if_falsy(stderr=stderr)

    idx = stderr.rfind('real ')

    if idx < 0:
        exc.raise_ioerror(errno.ENODATA, message='Benchmark failed.')

    time_output = stderr[idx:]
    call_result.stderr = stderr[:idx]

    result = re.search(r'[ ]*([0-9]+)[ ]+maximum resident set size', time_output)
    exc.raise_if_falsy(result=result)
    max_memory = long(result.group(1))

    return BenchResult.create_with(call_result, max_memory)
