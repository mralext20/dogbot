import datetime
import urllib.parse
from html.parser import HTMLParser

import discord
import timeago


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def format_dict(d, *, style='equals') -> str:
    """ Formats a ``dict`` to look pretty. """
    code_block = '```{}\n'.format('ini' if style == 'ini' else '')
    padding = len(max(d.keys(), key=len))

    for name, value in d.items():
        if style == 'equals':
            code_block += '{name: <{width}} = {value}\n'.format(name=name, width=padding, value=value)
        elif style == 'ini':
            code_block += '{name: <{width}} {value}\n'.format(name=f'[{name}]', width=padding + 2, value=value)

    code_block += '```'
    return code_block


def prevent_codeblock_breakout(text: str) -> str:
    return text.replace('`', '\u200b`\u200b')


def make_profile_embed(member):
    """ Creates an embed with the author containing the name and icon of a `discord.Member`. """
    embed = discord.Embed()
    embed.set_author(name=str(member), icon_url=member.avatar_url)
    return embed


def codeblock(text: str, *, lang: str = '') -> str:
    """
    Formats a codeblock.

    Args:
        text: The text to be inside of the codeblock.
        lang: The language to use.

    Returns: The formatted message.
    """
    return f'```{lang}\n{text}\n```'


def strip_tags(text: str):
    """ Strips HTML tags from text. """
    s = MLStripper()
    s.feed(text)
    return s.get_data()


def urlescape(text: str):
    """ "Quotes" text using urllib. `" "` -> `"%20"` """
    return urllib.parse.quote_plus(text)


def standard_datetime(dt):
    """
    Formats a `datetime.datetime` to a modified standard style: ::

        YEAR-MONTH-DAY HOUR:MINUTE:SECOND
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_list(lst):
    return '\n'.join('`{:03d}`: {}'.format(index + 1, value)
                     for index, value in enumerate(lst))


def now():
    """ Returns an Semistandard-formatted datetime with a "UTC" suffix. """
    return standard_datetime(datetime.datetime.utcnow()) + ' UTC'


def ago(dt):
    """ Returns a `pretty_timedelta` since the provided `datetime.timedelta`. """
    return timeago.format(dt, datetime.datetime.utcnow())


def truncate(text: str, desired_length: int):
    """
    Truncates text, and adds `...` at the end if it surpasses the desired length.

    .. NOTE::

        The returned `str` is guaranteed to be `desired_length` long.
    """
    if len(text) > desired_length:
        return text[:desired_length - 3] + '...'
    return text


def commas(number: 'Union[int, float]'):
    """ Adds American-style commas to an number. """
    return '{:,d}'.format(number)


def filesize(bytes: int) -> str:
    """
    Converts a bytesize to a human-readable filesize.

    Only supports MB and KB.

    :param bytes: The amount of bytes.
    :return: The human-readable filesize.
    """
    if bytes > 10 ** 5 * 5:  # 0.5 MB
        return f'{round(bytes / 10 ** 6, 2)} MB'
    else:
        return f'{round(bytes / 1000, 2)} KB'


def describe(thing, *, mention=False, before='', created=False, joined=False, quote=False):
    """
    Returns a string representing an project. Usually consists of the object in string form,
    then the object's ID in parentheses after.
    """
    # get name, might be mention
    name = str(thing) if not mention else thing.mention

    # handle emoji specially
    if isinstance(thing, discord.Emoji):
        name = f'`{":" + thing.name + ":" if thing.require_colons else thing.name}`'

    if quote:
        name = '"' + name + '"'

    # name + id
    message = f'{name} (`{thing.id}`)'

    # objects have id only
    if isinstance(thing, discord.Object):
        message = f'`{thing.id}`'

    if before:
        message += ' ' + before
    if created:
        message += f', created {ago(thing.created_at)}'
    if joined and isinstance(thing, discord.Member):
        message += f', joined {ago(thing.joined_at)}'
    return message
