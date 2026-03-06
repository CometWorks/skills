#!/usr/bin/python3
# -*- coding: ascii -*-
""" Downloads blueprints to server one or more games

- Monitors a folder for download requests
- Executes the downloads requested
- Puts the downloaded blueprint bp.sbc file into a cache folders
- Periodically cleans old downloads from the cache

Started by a cron job every 10 minutes. Quits after 10 minutes.

"""
import os
import shutil
import ssl
import sys
import urllib.request
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
from time import time, sleep
from traceback import format_exc
from typing import Dict
from xml.sax.saxutils import prepare_input_source, XMLGenerator

from defusedxml.sax import parse

WINDOWS = (sys.platform == 'win32')

WORK_FOLDER = os.path.expanduser('~/.cache/blueprint_downloader')
REQUESTS_FOLDER = os.path.join(WORK_FOLDER, 'requests')
RESPONSES_FOLDER = os.path.join(WORK_FOLDER, 'responses')

STEAM_SPACE_ENGINEERS_APP_ID = '244850'
STEAM_WORKSHOP_URL = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
STEAMCMD_PATH = r'C:\SEServer\steamcmd\steamcmd.exe' if WINDOWS else '/usr/games/steamcmd'
STEAMCMD_CONTENT_DIR = r'C:\SEServer\steamcmd\steamapps\workshop\content' if WINDOWS else os.path.expanduser('~/.steam/steamapps/workshop/content')
STEAMCMD_TIMEOUT = 60  # seconds

URL_LENGTH_LIMIT = 1000
DOWNLOAD_SIZE_LIMIT = 10 * 1024 ** 2

WGET_HEADERS: Dict[str, str] = {
    'User-Agent': 'Wget/1.12 (cygwin)',
    'Accept': '*/*',
}

POLL_PERIOD = 0.77  # seconds
LIFETIME = 3600  # seconds
CACHE_TIMEOUT = 86400  # seconds

MAX_PROJECTION_DEPTH = 2


if WINDOWS:
    LIFETIME *= 1000


def log(level: str, message: str):
    timestamp = datetime.now().isoformat()[:19]
    print(f'{timestamp} {level}: {message}')


def info(message: str):
    log('INFO', message)


def warn(message: str):
    log('WARN', message)


def error(message: str):
    log('ERROR', message)


def exc(message: str):
    error(message + '\n' + format_exc())


class BlueprintCleaner(XMLGenerator):

    def __init__(self, out):
        # Space Engineers is using UTF-8 encoded XMLs without a BOM and supports shorting empty elements
        super().__init__(out, encoding='UTF-8', short_empty_elements=True)
        self.projection_depth = 0
        self.keep = True

    def startElement(self, name, attrs):
        if name == 'ProjectedGrids':
            self.projection_depth += 1
            self.update_decision()

        if self.keep:
            super().startElement(name, attrs)

    def endElement(self, name):
        if self.keep:
            super().endElement(name)

        if name == 'ProjectedGrids':
            self.projection_depth -= 1
            self.update_decision()

    def update_decision(self):
        self.keep = self.projection_depth <= MAX_PROJECTION_DEPTH

    def characters(self, content):
        if self.keep:
            super().characters(content)

    def ignorableWhitespace(self, content):
        if self.keep:
            super().ignorableWhitespace(content)

    def processingInstruction(self, target, data):
        if self.keep:
            super().processingInstruction(target, data)


def download_from_steam_workshop(response_path: str, url: str):
    info(f'Downloading from Stream Workshop: {url}')
    started = time()
    blueprint_id = url[len(STEAM_WORKSHOP_URL):]
    if not blueprint_id.isdigit():
        raise ValueError(f'Invalid Steam blueprint ID: {blueprint_id}')
    process = Popen([STEAMCMD_PATH, '+login', 'anonymous', '+workshop_download_item', STEAM_SPACE_ENGINEERS_APP_ID, blueprint_id, '+quit'], stdout=PIPE, stderr=STDOUT)
    output = process.communicate(timeout=STEAMCMD_TIMEOUT)[0].decode('ascii')
    steam_cache_path = os.path.join(STEAMCMD_CONTENT_DIR, STEAM_SPACE_ENGINEERS_APP_ID, blueprint_id, 'bp.sbc')
    if process.returncode or not os.path.isfile(steam_cache_path):
        message = f'Failed to download blueprint from Steam Workshop: {blueprint_id}'
        error(f'{message}\n{output}')
        raise IOError(message)
    shutil.copy(steam_cache_path, response_path)
    duration = time() - started
    info(f'Downloaded blueprint from Steam Workshop in {duration:.3f}s: {response_path}')


def download_from_url(response_path: str, url: str):
    info(f'Downloading blueprint from URL: {url}')
    started = time()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    http_request = urllib.request.Request(url, method='GET', headers=WGET_HEADERS)
    with urllib.request.urlopen(http_request, context=ctx) as connection:
        data = connection.read(DOWNLOAD_SIZE_LIMIT + 1)
    if len(data) > DOWNLOAD_SIZE_LIMIT:
        raise IOError(f'Blueprint download is over the size limit of {DOWNLOAD_SIZE_LIMIT} bytes')
    with open(response_path, 'wb') as f:
        f.write(data)
    duration = time() - started
    info(f'Downloaded blueprint from URL in {duration:.3f}s: {response_path}')


def download(response_path: str, url: str):
    steam_workshop = url.startswith(STEAM_WORKSHOP_URL)

    if os.path.isfile(response_path):
        if steam_workshop:
            age = time() - os.stat(response_path).st_mtime
            if age < CACHE_TIMEOUT:
                info(f'Returning cached workshop blueprint: {response_path}')
                return
            info(f'Removing expired workshop blueprint: {response_path}')

        try:
            os.remove(response_path)
        except (IOError, OSError) as e:
            warn(f'Failed to remove blueprint: {response_path}; [{e.__class__.__name__}] {e}')

    if url.startswith(STEAM_WORKSHOP_URL):
        download_from_steam_workshop(response_path, url)
    else:
        download_from_url(response_path, url)


def handle(request_path: str, response_path: str):
    taken_path = request_path + '.taken'
    try:
        os.rename(request_path, taken_path)
    except (IOError, OSError):
        return

    with open(taken_path, 'rt') as f:
        request = f.readline().strip()

    os.remove(taken_path)

    if len(request) > URL_LENGTH_LIMIT:
        raise ValueError(f'URL in request {request_path} is longer than {URL_LENGTH_LIMIT} characters: {request}...')

    info(f'Request: {request}')

    if not request:
        return

    if request.isdigit():
        request = STEAM_WORKSHOP_URL + request

    dirty_response_path = f'{response_path}.dirty'
    if request.startswith('http://') or request.startswith('https://'):
        download(dirty_response_path, request)
    else:
        raise ValueError(f'Request is not a URL or Steam Workshop file ID: {request}')

    clean_response_path = f'{response_path}.clean'
    clean_blueprint(clean_response_path, dirty_response_path)

    os.remove(dirty_response_path)

    if os.path.exists(response_path):
        os.remove(response_path)

    os.rename(clean_response_path, response_path)


def clean_blueprint(clean_response_path, dirty_response_path):
    with open(dirty_response_path, 'rt', encoding='utf8') as dirty_xml:
        reader = prepare_input_source(dirty_xml)
        with open(clean_response_path, 'wt', encoding='utf8') as clean_xml:
            content_handler = BlueprintCleaner(clean_xml)
            parse(reader, content_handler)


def main():
    info('Started')
    os.makedirs(REQUESTS_FOLDER, exist_ok=True)
    os.makedirs(RESPONSES_FOLDER, exist_ok=True)
    run_until = time() + LIFETIME
    while time() < run_until:
        requests = os.listdir(REQUESTS_FOLDER)
        if not requests:
            sleep(POLL_PERIOD)
            continue
        for filename in requests:
            request_path = os.path.join(REQUESTS_FOLDER, filename)
            response_path = os.path.join(RESPONSES_FOLDER, filename)
            # noinspection PyBroadException
            try:
                handle(request_path, response_path)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                exc(f'Failed to handle request: {filename}')
                try:
                    with open(response_path, 'wt') as f:
                        f.write(f'ERROR: [{e.__class__.__name__}] {e}')
                except (IOError, OSError):
                    pass
            if time() < run_until:
                break
    info('Finished')


if __name__ == '__main__':
    main()
