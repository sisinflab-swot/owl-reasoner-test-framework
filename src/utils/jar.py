import exc
import proc


def proc_args(jar, args=None, vm_opts=None):
    """
    :param str jar : Path to the jar.
    :param list[str] args : Jar arguments.
    :param list[str] vm_opts : Java VM options.
    :rtype : list[str]
    :return : Arguments for the 'proc.call' function.
    """
    exc.raise_if_not_found(jar, file_type='file')

    java_args = [proc.find_executable('java')]

    if vm_opts:
        java_args.extend(vm_opts)

    java_args.extend(['-jar', jar])

    if args:
        java_args.extend(args)

    return java_args


def call(jar, args=None, vm_opts=None, output_action=proc.OutputAction.RETURN, timeout=None):
    """Executes a jar and returns its exit code and output.

    :param str jar : Path to the jar.
    :param list[str] args : Jar arguments.
    :param list[str] vm_opts : Java VM options.
    :param proc.OutputAction output_action : What to do with the output.
    :param float timeout : Timeout (s).
    :rtype : proc.CallResult
    :return Call result object.
    """
    return proc.call(proc_args(jar=jar, args=args, vm_opts=vm_opts), output_action=output_action, timeout=timeout)
