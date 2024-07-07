import sys
import logging
import re
import xml.etree.ElementTree as ET
import itertools

def to_ranges(iterable):
    iterable = sorted(set(iterable))
    for key, group in itertools.groupby(enumerate(iterable),
                                        lambda t: t[1] - t[0]):
        group = list(group)
        yield group[0][1], group[-1][1]


def text_to_bytes(text):
    l = [int(h, 16) for h in text.split()]
    r = list(to_ranges(l))
    if len(l) > 6 and len(r) == 1:
        return eval("range(%s, %s)" % (r[0][0], r[0][1]+1))
    return l


def text_to_dict(text):
    b = text_to_bytes(text)
    return {b[i]: b[i + 1] for i in range(0, len(b), 2)}

def generate_config(config, full, printer_model):
    waste_string = [
        "main_waste", "borderless_waste", "third_waste", "fourth_waste"
    ]
    irc_pattern = r'Ink replacement counter %-% (\w+) % \((\w+)\)'
    tree = ET.parse(config)
    root = tree.getroot()
    printer_config = {}
    for printer in root.iterfind(".//printer"):
        title = printer.attrib.get("title", "")
        if printer_model not in title:
            continue
        specs = printer.attrib["specs"].split(",")
        logging.info(
            "Tag: %s, Attributes: %s, Specs: %s",
            printer.tag, printer.attrib, printer.attrib['specs']
        )
        printer_name = printer.attrib["short"]
        chars = {}
        for spec in specs:
            logging.debug("SPEC: %s", spec)
            for elm in root.iterfind(".//" + spec):
                for item in elm:
                    logging.debug("item.tag: %s", item.tag)
                    if item.tag == "information":
                        for info in item:
                            if info.tag == "report":
                                chars["stats"] = {}
                                fatal = []
                                irc = ""
                                for number in info:
                                    if number.tag == "fatals":
                                        for n in number:
                                            if n.tag == "registers":
                                                for j in text_to_bytes(n.text):
                                                    fatal.append(j)
                                        chars["last_printer_fatal_errors"] = (
                                            fatal
                                        )
                                    if number.tag in ["number", "period"]:
                                        stat_name = ""
                                        for n in number:
                                            if n.tag == "name":
                                                stat_name = n.text
                                            if (
                                                n.tag == "registers"
                                                and stat_name
                                            ):
                                                match = re.search(irc_pattern, stat_name)
                                                if match:
                                                    color = match.group(1)
                                                    identifier = f"{match.group(2)}"
                                                    if "ink_replacement_counters" not in chars:
                                                        chars["ink_replacement_counters"] = {}
                                                    if color not in chars["ink_replacement_counters"]:
                                                        chars["ink_replacement_counters"][color] = {}
                                                    chars["ink_replacement_counters"][color][identifier] = int(n.text, 16)
                                                else:
                                                    chars["stats"][stat_name] = text_to_bytes(n.text)
                    if item.tag == "waste":
                        for operations in item:
                            if operations.tag == "reset":
                                chars["raw_waste_reset"] = text_to_dict(
                                    operations.text
                                )
                            if operations.tag == "query":
                                count = 0
                                for counter in operations:
                                    waste = {}
                                    for ncounter in counter:
                                        if ncounter.tag == "entry":
                                            if "oids" in waste:
                                                waste["oids"] += text_to_bytes(
                                                    ncounter.text
                                                )
                                            else:
                                                waste["oids"] = text_to_bytes(
                                                    ncounter.text
                                                )
                                        if ncounter.tag == "max":
                                            waste["divider"] = (
                                                int(ncounter.text) / 100
                                            )
                                        if full:
                                            for filter in ncounter:
                                                waste["filter"] = filter.text
                                    chars[waste_string[count]] = waste
                                    count += 1
                    if item.tag == "serial":
                        chars["serial_number"] = text_to_bytes(item.text)
                    if full and item.tag == "headid":
                        chars["headid"] = text_to_bytes(item.text)
                    if full and item.tag == "memory":
                        for mem in item:
                            if mem.tag == "lower":
                                chars["memory_lower"] = int(mem.text, 16)
                            if mem.tag == "upper":
                                chars["memory_upper"] = int(mem.text, 16)
                    if item.tag == "service":
                        for s in item:
                            if s.tag == "factory":
                                chars["read_key"] = text_to_bytes(s.text)
                            if s.tag == "keyword":
                                chars["write_key"] = (
                                    "".join(
                                        [
                                            chr(b - 1)
                                            for b in text_to_bytes(s.text)
                                        ]
                                    )
                                ).encode()
                            if full and s.tag == "sendlen":
                                chars["sendlen"] = int(s.text, 16)
                            if full and s.tag == "readlen":
                                chars["readlen"] = int(s.text, 16)
        printer_config[printer_name] = chars
    return printer_config


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        epilog='Generate printer configuration from devices.xml'
    )

    parser.add_argument(
        '-m',
        '--model',
        dest='printer_model',
        action="store",
        help='Printer model. Example: -m XP-205',
        required=True)

    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Print debug information')

    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        action='store_true',
        help='Print verbose information')

    parser.add_argument(
        '-f',
        '--full',
        dest='full',
        action='store_true',
        help='Generate additional tags')

    parser.add_argument(
        '-c',
        "--config",
        dest='config_file',
        type=argparse.FileType('r'),
        help="use the XML configuration file to generate the configuration",
        default=0,
        nargs=1,
        metavar='CONFIG_FILE'
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.INFO)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.config_file:
        args.config_file[0].close()

    if args.config_file:
        config = args.config_file[0].name
    else:
        config = "devices.xml"

    printer_config = generate_config(
        config=config,
        full=args.full,
        printer_model=args.printer_model
    )
    try:
        import black
        mode = black.Mode(line_length=120)
        dict_str = black.format_str(repr(printer_config), mode=mode)
        print(dict_str)
    except Exception:
        from pprint import pprint
        pprint(printer_config)