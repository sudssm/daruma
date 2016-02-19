from multiprocessing import Process, Pipe
from uuid import uuid4
from custom_exceptions.exceptions import SandboxProcessFailure

FILENAME_SIZE = 32


# create a length-32 string of random uppercase letters and numbers
def generate_filename():
    return str(uuid4()).replace('-', '').upper()


def sandbox_function(function, *args):
    """
    Runs a function liable to cause a crash in a separate process.

    Args:
        function: the function to run.  This function must return an array of
            strings OR exit with a non-zero status.
        args...: the arguments to be passed to the function

    Returns:
        The array of strings returned by the function.

    Raises:
        SandboxProcessFailure: the process the function was running in exited
            with a non-zero status (the exit code is included in the exception)
    """
    EXIT_SUCCESS = 0

    def function_wrapper(function, pipe, args):
        results = function(*args)
        for result in results:
            pipe.send_bytes(result)
        pipe.close()
    pipe_receiver, pipe_sender = Pipe(duplex=False)
    process = Process(target=function_wrapper, args=(function, pipe_sender, args))
    process.start()
    pipe_sender.close()
    process.join()

    if process.exitcode is not EXIT_SUCCESS:
        raise SandboxProcessFailure(process.exitcode)

    results = []
    while True:
        try:
            result = pipe_receiver.recv_bytes()
            results.append(result)
        except EOFError:
            break

    return results
