import exc
import proc


def call(jar, args=None, output_action=proc.OutputAction.RETURN):
    """Executes a jar and returns its exit code and output.

    :param str jar : Path to the jar.
    :param list args : Jar arguments.
    :param proc.OutputAction output_action : What to do with the output.
    :rtype : proc.CallResult
    :return Call result object.
    """
    exc.raise_if_not_found(jar, file_type='file')

    java_args = [proc.find_executable('java'), '-jar', jar] + args
    return proc.call(java_args, output_action=output_action)
