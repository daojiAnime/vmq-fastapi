import logging
import sys
from types import TracebackType

import structlog
from structlog.types import EventDict, Processor


def drop_color_message_key(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:  # noqa: ARG001
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging(json_logs: bool = False, log_level: str = "INFO") -> None:
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S%Z.%f", utc=False)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        # structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
        # `message` key but the pretty ConsoleRenderer looks for `event`
        shared_processors.append(structlog.processors.EventRenamer("message"))
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors
        + [
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if json_logs:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer(
            exception_formatter=structlog.dev.RichTracebackFormatter(show_locals=False)  # width=120, max_frames=5,
        )

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    # logger_name_list = [name for name in logging.root.manager.loggerDict]
    # rich.print(f"logger_name_list: {logger_name_list}")
    # for name, logger in logging.root.manager.loggerDict.items():
    #     if isinstance(logger, logging.PlaceHolder):
    #         continue
    #     logger.handlers.clear()
    #     logger.addHandler(handler)
    # for _log in ["uvicorn", "uvicorn.error"]:
    #     logging.getLogger(_log).handlers.clear()
    #     logging.getLogger(_log).propagate = True
    #
    logging.getLogger("uvicorn").handlers.clear()
    # logging.getLogger("uvicorn").addHandler(handler)
    # logging.getLogger("uvicorn").propagate = False
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.addHandler(handler)
    uvicorn_error.propagate = False
    uvicorn_error.setLevel(logging.ERROR)

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.addHandler(handler)
    uvicorn_access.setLevel(logging.INFO)
    uvicorn_access.propagate = False

    def handle_exception(
        exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # 将自定义错误处理程序注册为全局异常处理程序
    sys.excepthook = handle_exception
