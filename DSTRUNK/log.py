import logging, logging.handlers


loggingInitialized = False


def SetupLogging(logName, level = logging.INFO, logsize = 15 * 1024 * 1024, logbackups = 2):
    global loggingInitialized

    if not loggingInitialized:
	loggingInitialized = True

	# define a Handler which writes INFO messages or higher to files.  This
	# will write all build output to a single log file and keep 15 build logs
	# from the past around.
	files = logging.handlers.RotatingFileHandler(logName, 'a', logsize, logbackups)
	console = logging.StreamHandler()

	# set a format
	fileFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(thread)-4s %(message)s')
	consoleFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(thread)-4s %(message)s')

	# tell the handler to use this format
	files.setFormatter(fileFormatter)
	console.setFormatter(consoleFormatter)

	# for some reason, we all of a sudden now need to remove any default
	# handlers so we don't get duplicate console output.  This wasn't needed
	# yesterday.  I wonder what changed since then.
	for handler in logging.getLogger('').handlers:
	    logging.getLogger('').removeHandler(handler)

	# add the handler to the root logger
	logging.getLogger('').addHandler(files)
	logging.getLogger('').addHandler(console)
	logging.getLogger('').setLevel(level)
