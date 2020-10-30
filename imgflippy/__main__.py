from __future__ import print_function
import sys
import logging
import argparse
import textwrap

import imgflippy
from imgflippy import Config, MemeTemplate, model, utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(imgflippy.__name__)


class TemplateAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-i', '-id']:
            template = utils.get_template_by_id(values)
        elif option_string in ['-n', '--name']:
            template = utils.get_template_by_name(values)
        elif option_string in ['-r', '--regex']:
            template = utils.get_template_by_regex(values)
        setattr(namespace, self.dest, template or values)


class BoxesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        boxes_ = getattr(namespace, 'boxes', [])

        consumed = False

        for box in boxes_:
            if self.dest in box:
                continue

            box.update({self.dest: values})
            consumed = True
            break

        if not consumed:
            boxes_.append({self.dest: values})

        setattr(namespace, 'boxes', boxes_)


def format_help(self, command_parsers):
    # self == parser
    formatter = self._get_formatter()

    # usage
    formatter.add_usage(self.usage, self._actions,
                        self._mutually_exclusive_groups)

    # description
    formatter.add_text(self.description)

    # positionals, optionals and user-defined groups
    for action_group in self._action_groups:
        #print("action_group ", action_group[0])
        #print(dir(action_group[0]))
        #print("action_group ", dir(action_group))
        formatter.start_section(action_group.title)
        if(action_group.title == 'positional arguments'):
            #for command in command_parsers:
                #print("tite2 ", action_group)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            #print("action_group._group_actions ", action_group._group_actions)
        else:
            print("tite ", action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
        formatter.end_section()

    # epilog
    #formatter.add_text(self.epilog)
    formatter.add_text('FLUFFY CATS')

    # determine help from format above
    return formatter.format_help()

def main():

    parser_ = argparse.ArgumentParser(
        prog=imgflippy.__name__,
        description=textwrap.dedent('''\
            An unofficial and open source Python interface for the imgflip 
            RESTful API (https://api.imgflip.com/).'''),
        formatter_class=argparse.RawTextHelpFormatter)

    parser_.add_argument(
        '-v',
        '--version',
        action='store_true',
        default=argparse.SUPPRESS,
        help='display the program\'s version and exit.')

    get_memes_parser = argparse.ArgumentParser(
        prog='get_memes',
        description='Display a list of available meme templates and exit.')

    add_caption_parser = argparse.ArgumentParser(
        prog='add_caption',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Add a caption to meme template and print the resulting meme\'s '
             'image URL.')

    add_caption_parser.add_argument('-d', '--debug', action='store_true')

    template_group = add_caption_parser.add_mutually_exclusive_group(
        required=True)

    template_group.add_argument(
        '-i',
        '--id',
        action=TemplateAction,
        help='Find meme template by id.',
        metavar='ID',
        dest='template')

    template_group.add_argument(
        '-n',
        '--name',
        action=TemplateAction,
        help='Find meme template by name.',
        metavar='NAME',
        dest='template')

    template_group.add_argument(
        '-r',
        '--regex',
        action=TemplateAction,
        help='Find meme template by regular expression.',
        metavar='REGEX',
        dest='template')

    add_caption_parser.add_argument(
        '-u',
        '--username',
        default=Config.imgflip_username,
        help='Username of a valid imgflip account.\nThis is used to track '
             'where API requests are coming from.')

    add_caption_parser.add_argument(
        '-p',
        '--password',
        default=Config.imgflip_password,
        help='Password for the imgflip account.')

    add_caption_parser.add_argument(
        '-t0',
        '--text0',
        default=argparse.SUPPRESS,
        help='Top text for the meme (do not use this argument if you are '
             'using the boxes "text" argument below).',
        metavar='TEXT',
        dest='text0')

    add_caption_parser.add_argument(
        '-t1',
        '--text1',
        default=argparse.SUPPRESS,
        help='bottom text for the meme (do not use this argument if you are \n'
             'using the boxes \'text\' argument below).',
        metavar='TEXT',
        dest='text1')

    add_caption_parser.add_argument(
        '-f',
        '--font',
        default=argparse.SUPPRESS,
        choices=model.Fonts.valid(),
        help='The font family to use for the text.\nCurrent options are '
             '"impact" and "arial" (defaults to impact)',
        metavar='FONT')

    add_caption_parser.add_argument(
        '-m',
        '--max-font-size',
        default=argparse.SUPPRESS,
        type=int,
        help='Maximum font size in pixels (defaults to 50px).',
        metavar='SIZE')

    boxes_group = add_caption_parser.add_argument_group(
        title='boxes',
        description=textwrap.dedent('''\
            For creating memes with more than two text boxes, or for further 
            customization.
            
            If boxes arguments are specified, text0 and text1 will be ignored,
            and text will not be automatically converted to uppercase, so
            you'll have to handle capitalization yourself if you want the
            standard uppercase meme text. You may specify up to 5 text boxes.
            All options below are optional, except "text". The exception is
            that you may leave the first box completely empty, so that the
            second box will automatically be used for the bottom text.
            
            Arguments x, y, width and height are for the bounding box of the
            text box. Arguments x and y are the coordinates of the top left
            corner. If you specify bounding coordinates, be sure to specify all
            four (x, y, width, height), otherwise your text may not show up
            correctly. If you do not specify bounding box coordinates, the same
            automatic default coordinates from imgflip.com/memegenerator will
            be used, which is very useful for memes with special text box
            positioning other than the simple top/bottom.'''))

    boxes_group.add_argument('-t',
                             '--text',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             dest='text')

    boxes_group.add_argument('-x',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             type=int,
                             dest='x')

    boxes_group.add_argument('-y',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             type=int,
                             dest='y')

    boxes_group.add_argument('-w',
                             '--width',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             type=int,
                             dest='width')

    boxes_group.add_argument('-H',
                             '--height',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             type=int,
                             dest='height')

    boxes_group.add_argument('-c',
                             '--color',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             dest='color')

    boxes_group.add_argument('-o',
                             '--outline-colour',
                             action=BoxesAction,
                             default=argparse.SUPPRESS,
                             dest='outline_color')

    args, extras = parser_.parse_known_args()

    if hasattr(args, 'version'):
        message = '{} v{}'.format(imgflippy.__name__, imgflippy.__version__)
        parser_.exit(status=0, message=message)

    # Display a table of the templates available for captioning.
    if 'get_memes' in extras:
        return parser_.exit(status=0, message=utils.get_meme_template_info())

    elif 'add_caption' in extras:
        args, extras = add_caption_parser.parse_known_args(extras[1:])
        if not isinstance(args.template, MemeTemplate):
            raise RuntimeError

        if args.debug:
            logger.setLevel(logging.DEBUG)

        kwargs = {k: v for k, v in vars(args).items() if
                  k not in ['debug', 'template']}

        result = args.template.add_caption(**kwargs)
        print(result.url)
    else:
        print(format_help(parser_, [add_caption_parser, get_memes_parser]))
        # Display help if no valid command is passed
        #parser_.print_help()

    sys.exit(0)


main()
