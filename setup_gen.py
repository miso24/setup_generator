#!/usr/bin/env python
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator 
from prompt_toolkit.styles import Style
import configparser
import os
import sys

raw_setup_py = "from setuptools import setup\n\nsetup()"

def validation_email(text):
    return "@" in text

email_validator = Validator.from_callable(
    validation_email,
    error_message="Not a valid email",
    move_cursor_to_end=True
)

style = Style.from_dict({
    '': '#aaaa00',
    'prompt': '#00aa00',
    'require': '#bb0000'
})

def input_prompt(mes, *args, **kwargs):
    inp = prompt([('class:prompt', mes)], style=style, **kwargs)
    return inp

def require_input_prompt(mes):
    inp = prompt([('class:require', mes)], style=style)
    if inp == "":
        return require_input_prompt(mes)
    return inp

def yes_no_prompt(message):
    user_input = input_prompt(message + " (y / n): ")
    if user_input in ["Y", "y", "yes", "Yes"]:
        return True
    elif user_input in ["N", "n", "no", "No"]:
        return False
    yes_no_prompt(message)

def gen_default_config(path):
    config = configparser.ConfigParser()
    config['Author']['author'] = ""
    config['Author']['author_email'] = ""
    config['GitHub']['github_url'] = ""
    with open(path, 'w') as f:
        config.write(f)

def config_common_data(conf):
    author = input_prompt("author name: ")
    author_email = input_prompt("author email: ", validator=email_validator, validate_while_typing=True)
    conf['Author']['author'] = author
    conf['Author']['author_email'] = author_email

    use_github_url = yes_no_prompt("use github as url?")
    if use_github_url:
        github_un = input_prompt("github user name: ")
        conf['GitHub']['github_url'] = f"https://github.com/{github_un}"

    with open('./config.ini', 'w') as f:
        conf.write(f)
    print("config updated!")

def gen_setup(conf):
    # input module name
    mod_name = require_input_prompt("module name: ")
    # input version
    version = input_prompt(f"version (default: {mod_name}.__version__): ")
    if version == "":
        version = f"attr: {mod_name}.__version__"
    # input url
    if conf['GitHub']['github_url'] == "":
        url = input_prompt("url: ")
    else:
        url = conf['GitHub']['github_url'] + "/" + mod_name
    # input description
    description = input_prompt("description: ")
    long_description = input_prompt("long description (default: README.md): ")
    if long_description == "":
        long_description = "file: README.md"

    setup_cfg = configparser.ConfigParser()
    setup_cfg['metadata'] = {
        "name": mod_name,
        "version": version,
        "url": url,
        "author": conf['Author']['author'],
        "author_email": conf['Author']['author_email'],
        "description": description,
        "long_description": long_description
    }
    setup_cfg["options"] = {
        "zip_safe": False,
        "packages": "find:"
    }

    with open('./setup.cfg', 'w') as f:
        setup_cfg.write(f)
    with open('./setup.py', 'w') as f:
        f.write(raw_setup_py)
    print("setup.cfg generated!")

def show_usage():
    print("Usage: setup_gen [config]")

if __name__ == "__main__":
    config_path = os.path.dirname(os.path.abspath(__file__)) + "/config.ini"
    if not os.path.exists(config_path):
        gen_default_config(config_path)
    # load config
    conf = configparser.ConfigParser()
    conf.read(config_path)
    # get args
    argv = sys.argv
    if len(argv) > 2:
        show_usage()

    if len(argv) == 2 and argv[1] in ["config", "conf"]:
        config_common_data(conf)
    elif len(argv) == 1:
        gen_setup(conf)
