from logging import FileHandler
import multiprocessing, threading, logging, sys, traceback

class MultiProcessingLogHandler(logging.Handler):
    def __init__(self, name, queue):
        logging.Handler.__init__(self)

        self._handler = FileHandler(name)
        self.queue = queue

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                if record == StopIteration:
                    break
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)
                break

        return

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self.queue.put_nowait(StopIteration)
        self._handler.close()
        logging.Handler.close(self)
        
class EasyLogger(object):
    def __init__(self, logpath, level=None):

        if level is None:
            level = logging.INFO

        self.logpath = logpath
        self.logger = multiprocessing.get_logger()

        self.queue = multiprocessing.Queue(-1)

        # Close any existing handlers
        self.close_handlers()
        
        # Remove any existing handlers
        self.logger.handlers = []
        self.logger.setLevel(level)

        handler = MultiProcessingLogHandler(logpath, self.queue)
        handler.setLevel(level)
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(name)s - %(processName)s - %(message)s')
        handler.setFormatter(formatter)
        # Add handler
        self.logger.addHandler(handler)
        
    def close_handlers(self):
        (hand.close() for hand in self.logger.handlers)
        
    def close_queue(self):
        self.queue.put_nowait(StopIteration)

    def close(self):
        self.close_handlers()
        self.close_queue()

    def __str__(self):
        return "Logging with MultiProcessingLogHandler in " + self.logpath
        
        
