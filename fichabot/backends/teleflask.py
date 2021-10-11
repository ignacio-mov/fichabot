from pytgbot.api_types.receivable.updates import Update
from teleflask.server.base import TeleflaskMixinBase, TeleflaskBase
from teleflask.server.mixins import StartupMixin, BotCommandsMixin, MessagesMixin, UpdatesMixin

import logging

logger = logging.getLogger(__name__)


class BotCallbacksMixin(TeleflaskMixinBase):

    def __init__(self, *args, **kwargs):
        self.callbacks = dict()
        super(BotCallbacksMixin, self).__init__(*args, **kwargs)

    # end def

    def on_callback(self, callback, exclusive=False):
        """
        Decorator to register a command.

        :param callback: The command to be registered. Omit the slash.
        :param exclusive: Stop processing the update further, so no other listenere will be called if this command triggered.

        Usage:
import fichabot            >>> @app.on_callback("foo")
            >>> def foo(update, text):
            >>>     assert isinstance(update, Update)
            >>>     fichabot.bot.send_message(update.message.chat.id, "bar:" + text)

            If you now receiva a callback query with "foo", it will reply with "bar:hey"

            You can set to ignore other registered listeners to trigger.

            >>> @app.on_callback("bar", exclusive=True)
            >>> def bar(update, text)
            >>>     return "Bar command happened."

            >>> @app.on_callback("bar")
            >>> def bar2(update, text)
            >>>     return "This function will never be called."

        @on_callback decorator. Actually is an alias to @callback.
        :param callback: the data of the callback query
        """
        return self.callback(callback, exclusive=exclusive)

    # end if

    def callback(self, callback, exclusive=False):
        """
        Decorator to register a command.

        Usage:
import fichabot            >>> @app.callback("foo")
            >>> def foo(update, text):
            >>>     assert isinstance(update, Update)
            >>>     fichabot.bot.send_message(update.message.chat.id, "bar:" + text)

            If you now receiva a callback query with "foo", it will reply with "bar:hey"

        :param callback: the data of the callback query
        """

        def register_callback(func):
            self.add_callback(callback, func, exclusive=exclusive)
            return func

        return register_callback

    # end def

    def add_callback(self, callback, function, exclusive=False):
        """
        Adds `/callback`

        Will overwrite existing callbacks.

        Arguments to the functions decorated will be (update, text)
            - update: The update from telegram. :class:`pytgbot.api_types.receivable.updates.Update`
            - text: The text after the command (:class:`str`), or None if there was no text.
        Also see :def:`BotCallbacksMixin._dispatch_callbacks()`

        :param callback: The command
        :param function:  The function to call. Will be called with the update and the text after the /command as args.
        :return: Nothing
        """
        self.callbacks[callback] = (function, exclusive)

    # end def add_command

    def remove_callback(self, callback=None, function=None):
        """
        :param callback: remove them by command, e.g. `test`
        :param function: remove them by function
        :return:
        """
        if callback:
            del self.callbacks[callback]
        # end if
        if function:
            for key, value in self.callbacks.items():
                func, exclusive = value
                if func == function:
                    del self.callbacks[key]
                # end if
            # end for
        # end if
        if not callback and not function:
            raise ValueError("You have to specify a command or a function to remove. Or both.")
        # end if

    # end def remove_command

    def process_update(self, update):
        """
        If the message is a registered callback it will be called.
        Arguments to the functions will be (update, text)
            - update: The :class:`pytgbot.api_types.receivable.updates.Update`
        Also see ._dispatch_callback()

        :param update: incoming telegram update.
        :return: nothing.
        """
        assert isinstance(update, Update)
        try:
            data = update.callback_query.data
            logger.debug(f'Llamado callback {data}')
        except Exception:
            data = None

        func = None
        if data in self.callbacks:
            logger.debug("Running callback {input} (no text).".format(input=data))
            func, exclusive = self.callbacks[data]
            self._dispatch_callback(func, update, data)
        else:
            logging.debug("No fitting registered callback function found.")
            exclusive = False  # so It won't abort.
        # end if
        if exclusive:
            logger.debug(
                "Command function {func!r} marked exclusive, stopping further processing.".format(func=func)
            )  # not calling super().process_update(update)
            return
        # end if
        super().process_update(update)

    # end def process_update

    def do_startup(self):  # pragma: no cover
        super().do_startup()

    # end if

    def _dispatch_callback(self, func, update, callback):
        try:
            self.process_result(update, func(update))
        except Exception:
            logger.exception("Failed calling callback {cmd!r} ({func}):".format(cmd=callback, func=func))
        # end try

    # end def


class CallbackBot(StartupMixin, BotCallbacksMixin, BotCommandsMixin, MessagesMixin, UpdatesMixin, TeleflaskBase):
    pass
