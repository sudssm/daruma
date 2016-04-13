from multiprocessing import Process, Pipe
from uuid import uuid4
from urlparse import urlparse, parse_qs
from custom_exceptions.exceptions import SandboxProcessFailure

APP_NAME = "daruma"
INTERNAL_SERVER_HOST = "localhost"
INTERNAL_SERVER_PORT = 28962  # This should be a free port

FILENAME_SIZE = 32


# create a length-32 string of random uppercase letters and numbers
def generate_random_name():
    return str(uuid4()).replace('-', '').upper()


def parse_url(url):
    """
    Parse a url to get its parameters
    Returns a map from parameter name to parameter value
    """
    params = parse_qs(urlparse(url).query)
    return {k: v[0] for k, v in params.items()}


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

    def function_wrapper(function, pipe_receiver, pipe_sender, args):
        """
        This function calls the user's function and then sends the returned
        data back on the provided pipe.
        """
        pipe_receiver.close()
        results = function(*args)
        for result in results:
            pipe_sender.send_bytes(result)
        pipe_sender.close()
    # Create a pipe to send data returned from the function.  This custom
    # serialization scheme is used because at least one application of the
    # sandbox uses untrusted data unsuitable for pickling.  If more diverse
    # applications crop up, using JSON for serialization may make sense.
    pipe_receiver, pipe_sender = Pipe(duplex=False)

    # Call the function wrapper in a new process
    process = Process(target=function_wrapper, args=(function, pipe_receiver, pipe_sender, args))
    process.start()
    pipe_sender.close()

    # Wait for the new process to exit
    process.join()

    # The status code will be non-zero on a crash or exception
    if process.exitcode is not EXIT_SUCCESS:
        raise SandboxProcessFailure(process.exitcode)

    # Reconstruct the returned data
    results = []
    while True:
        try:
            result = pipe_receiver.recv_bytes()
            results.append(result)
        except EOFError:
            break

    return results
