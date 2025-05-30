from .clear_history import clear_history


def prepare_chat(
    self,
    recipient: "BaseAgent",
    should_clear_history: bool,
    prepare_recipient: bool = True,
    reply_at_receive: bool = True,
) -> None:

    self.reply_at_receive[recipient] = reply_at_receive
    if should_clear_history:
        clear_history(self, recipient)
    if prepare_recipient:
        prepare_chat(recipient, self, should_clear_history, False, reply_at_receive)
