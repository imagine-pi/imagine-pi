###########
# Stdlib

import argparse
import sys

###########
# Stdlib

from . import raspi_os


def cli():
    ROOT_KEY = "_"
    command_name = ROOT_KEY
    subcommand_name = ROOT_KEY
    parsers = {}
    subparsers = {}
    parsers[ROOT_KEY] = {}
    # root parser
    parsers[ROOT_KEY][ROOT_KEY] = argparse.ArgumentParser(
        prog="imagine-pi", description="A Pi imaging tool"
    )
    subparsers[ROOT_KEY] = parsers[ROOT_KEY][ROOT_KEY].add_subparsers(
        title="subcommands", dest="command_name"
    )

    # parser for [os] command
    parsers["os"] = {}
    parsers["os"][ROOT_KEY] = subparsers[ROOT_KEY].add_parser(
        "os", help="os information"
    )
    subparsers["os"] = parsers["os"][ROOT_KEY].add_subparsers(
        title="subcommands", dest="subcommand_name"
    )

    # parser for [os list] command
    parsers["os"]["list"] = subparsers["os"].add_parser(
        "list", help="get a list"
        + "of available operating systems for raspberry pi"
    )
    parsers["os"]["list"].add_argument(
        "-u", "--url",
        action="store_true",
        help="show only urls of operating systems"
    )
    parsers["os"]["list"].set_defaults(func=cli_os_list)

    # parser for [os get] command
    parsers["os"]["show"] = subparsers["os"].add_parser(
        "show", help="show detailed information on a single os"
    )
    os_show_param_group = parsers["os"]["show"].add_mutually_exclusive_group(
        required=True
    )
    os_show_param_group.add_argument(
        "-n", "--name",
        type=str,
        help="name of the os to show, "
        + "use imagine-pi os list to show known names",
    )
    os_show_param_group.add_argument(
        "-u", "--url",
        type=str,
        help="url of the os to show, "
        + "use imagine-pi os list to show known urls",
    )
    parsers["os"]["show"].set_defaults(func=cli_os_get)

    # parser for [device] command
    parsers["device"] = {}
    parsers["device"][ROOT_KEY] = subparsers[ROOT_KEY].add_parser(
        "device", help="local device interaction"
    )
    subparsers["device"] = parsers["device"][ROOT_KEY].add_subparsers(
        title="subcommands", dest="subcommand_name"
    )

    # parser for [device list] command
    parsers["device"]["list"] = subparsers["device"].add_parser(
        "list", help="list available devices"
    )
    parsers["device"]["list"].set_defaults(func=cli_device_list)

    # parser for [device get] command
    parsers["device"]["get"] = subparsers["device"].add_parser(
        "get", help="get detailed information on a single device"
    )
    parsers["device"]["get"].add_argument(
        "path", type=str, help="name of the device to get"
    )
    parsers["device"]["get"].set_defaults(func=cli_device_get)

    # parser for [device init] command
    parsers["device"]["init"] = subparsers["device"].add_parser(
        "init", help="initialize a device for imaging"
    )
    parsers["device"]["init"].add_argument(
        "path", type=str, help="name of the device to init"
    )
    parsers["device"]["init"].set_defaults(func=cli_device_init)

    args = parsers[ROOT_KEY][ROOT_KEY].parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print(args)
        if hasattr(args, "command_name") and args.command_name:
            command_name = args.command_name
            if hasattr(args, "subcommand_name") and args.subcommand_name:
                subcommand_name = args.subcommand_name
        parsers[command_name][subcommand_name].print_help()


def cli_os_list(args):
    os_list = raspi_os.get_raspi_os_list()

    if args.url:
        format_table(obj_list=os_list, show_headers=False, properties=["url"])
    else:
        format_table(
            obj_list=os_list,
            show_headers=True,
            properties=["name", "url"],
        )


def cli_os_get(args):
    try:
        if args.url:
            os_obj = raspi_os.get_raspi_os_from_url(args.url)
        else:
            os_obj = raspi_os.get_raspi_os_from_name(args.name)
    except Exception as e:
        print("Unexpected error:", str(e))
        sys.exit(1)

    format_obj(os_obj, "name")


def cli_device_list(args):
    print("todo cli_device_list")


def cli_device_get(args):
    print("todo cli_device_get")


def cli_device_init(args):
    print("todo cli_device_init")


if __name__ == "__main__":
    cli()


def format_table(obj_list, properties, show_headers=False):
    property_length = {}
    if len(properties) == 0 or properties[0] == "*":
        properties = []
        obj = obj_list[0]
        if "__dict__" in obj:
            for property, value in vars(obj).items():
                properties.append(property)

    for property in properties:
        prop_length_max = len(property)
        for obj in obj_list:
            prop_len = len(str(getattr(obj, property)))
            if prop_len > prop_length_max:
                prop_length_max = prop_len

        property_length[property] = prop_length_max

    if show_headers:
        strings = []
        for property in properties:
            strings.append("-" * property_length[property])
        lines = " ".join(strings)

        print(lines)
        strings = []
        for property in properties:
            strings.append(property.ljust(property_length[property], " "))
        print(" ".join(strings))
        print(lines)

    for obj in obj_list:
        strings = []
        for property in properties:
            strings.append(
                str(getattr(obj, property)).ljust(
                    property_length[property],
                    " "
                )
            )

        print(" ".join(strings))


def format_obj(obj, title_property, properties=[]):

    if len(properties) == 0 or properties[0] == "*":
        properties == []
        for property in dir(obj):
            try:
                index = property.index("_")
            except Exception:
                index = -1
            if property != title_property or index != 0:
                properties.append(property)

    prop_name_length_max = len(property)
    for property in properties:
        if len(property) > prop_name_length_max:
            prop_name_length_max = len(property)

    print("{0}: {1}".format(title_property, obj.__dict__[title_property]))
    for property in properties:
        print(
            "    - {0}: {1}".format(
                property.ljust(prop_name_length_max, " "),
                getattr(obj, property)
            )
        )
