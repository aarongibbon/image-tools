import logging


class CustomStdoutFormatter(logging.Formatter):

    COLOURS = {
        logging.WARNING: "\x1b[33;20m",
        logging.ERROR: "\x1b[31;20m"
    }

    RESET = "\x1b[0m"

    def format(self, record):

        colour = self.COLOURS.get(record.levelno, None)
        if colour:
            fmt = logging.Formatter(colour+self._fmt+self.RESET)
            return fmt.format(record)
        return super().format(record)


class CustomStdoutEmailFormatter(logging.Formatter):

    COLOURS = {
        logging.WARNING: "yellow",
        logging.ERROR: "red"
    }

    RESET = "</span>"

    def format(self, record):
        colour = self.COLOURS.get(record.levelno, 'black')
        fmt = logging.Formatter(f"<span style='color: {colour};'>"+self._fmt+"</span>")
        return fmt.format(record)
