import exc
import proc


def call(jar, args=None, vm_opts=None, output_action=proc.OutputAction.RETURN):
    """Executes a jar and returns its exit code and output.

    :param str jar : Path to the jar.
    :param list[str] args : Jar arguments.
    :param list[str] vm_opts : Java VM options.
    :param proc.OutputAction output_action : What to do with the output.
    :rtype : proc.CallResult
    :return Call result object.
    """
    exc.raise_if_not_found(jar, file_type='file')

    java_args = [proc.find_executable('java')]

    if vm_opts:
        java_args.extend(vm_opts)

    java_args.extend(['-jar', jar])

    if args:
        java_args.extend(args)

    return proc.call(java_args, output_action=output_action)
