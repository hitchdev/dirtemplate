class DirTemplateException(Exception):
    pass


class TemplateError(DirTemplateException):
    def __init__(self, filename, error_type, lineno, message, source):
        super(TemplateError, self).__init__((
            "{error_type} in {filename} on line {lineno}:\n\n"
            "{message}\n\n{source}\n"
        ).format(
            filename=filename,
            error_type=error_type,
            lineno=lineno,
            message=message,
            source=source,
        ))
