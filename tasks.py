"""
Download reports from BI
"""
import json
import os
from datetime import date, timedelta

from invoke import call, task
import requests

from biredirect.boxstores import BoxKeysStoreRedis
from biredirect.reportserver import ReportFormat, ReportServer
from biredirect.settings import (BOX_DESTINATION_FOLDER, DOWNLOAD_PATH,
                                 FILE_LIST, HEROKU_APP_NAME, REPORT_PASSWORD,
                                 REPORT_SERVER, REPORT_USERNAME)
from biredirect.utils import parse_date, print_prof_data, profile
from boxsync.bifile import BiFile
from boxsync.boxsync import BoxSync


@task
def create_pip_requirements(ctx):
    """
    pip freeze to requirements.txt
    """
    ctx.run("pip freeze > requirements.txt")


@task
def download_files(ctx, open_date, update_date):
    """
    Download report files to DOWNLOAD_PATH folder.

    :param open_date:
        Earliest open date.
    :param update_date:
        Earliest update date.
    """

    open_date = parse_date(open_date)
    update_date = parse_date(update_date)

    report_download = _get_report_download()
    temp_path = DOWNLOAD_PATH
    timestamp = update_date.strftime('%Y%m%d')
    str_open_date = open_date.strftime('%m/%d/%Y')
    str_update_date = update_date.strftime('%m/%d/%Y')
    # Ticket_dump
    print("Downloading Ticket_dump...")
    report_args = {'Date': str_open_date, 'LastUpdate': str_update_date}
    filename = os.path.join(temp_path, f'Ticket_dump_{timestamp}.xml')
    report_download.download_report('My Reports/Ticket_dump_BI',
                                    ReportFormat.XML,
                                    filename, report_args)
    # Task_dump
    print("Downloading Task_dump...")
    report_args = {'LastUpdate': str_update_date}
    filename = os.path.join(temp_path, f'Task_dump_{timestamp}.csv')
    report_download.download_report('My Reports/Task_dump_BI',
                                    ReportFormat.CSV,
                                    filename, report_args)
    # Call_dump
    print("Downloading Call_dump...")
    report_args = {'LastUpdate': str_update_date}
    filename = os.path.join(temp_path, f'IncomingCall_dump_{timestamp}.csv')
    report_download.download_report('My Reports/IncomingCall_dump_BI',
                                    ReportFormat.CSV,
                                    filename, report_args)


def _get_report_download():
    """
    >>> from Crypto.Cipher import AES
    >>> obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    >>> message = "The answer is no"
    >>> ciphertext = obj.encrypt(message)
    >>> ciphertext
    '\xd6\x83\x8dd!VT\x92\xaa`A\x05\xe0\x9b\x8b\xf1'
    >>> obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    >>> obj2.decrypt(ciphertext)
    'The answer is no'
    """
    report_download = ReportServer(REPORT_SERVER)
    print("Login into report server")
    report_download.login(REPORT_USERNAME, REPORT_PASSWORD)
    print("Login successful")
    return report_download


@task
def delete_local_files(ctx, folder=DOWNLOAD_PATH):
    """
    Delete local files

    :param path:
        Directory to clean
    """
    print("Deleting tmp files")
    for the_file in os.scandir(folder):
        try:
            if the_file.is_file():
                os.unlink(the_file.path)
        except OSError as ex:
            print(ex)


@profile
@task
def sync_to_box(ctx, delete_files_remotely=False):
    """
    Upload local files to be processed by PowerBi
    """
    # Create client
    client = BoxSync(keys_store=BoxKeysStoreRedis,
                     authenticate_method=_authenticate_box)

    if delete_files_remotely:
        # Create a local file_list file
        _create_file_list(client)

    # Sync folder to Box
    client.sync_folder(local_path=DOWNLOAD_PATH,
                       box_folder_id=BOX_DESTINATION_FOLDER,
                       create_link=True,
                       delete_files_remotely=delete_files_remotely)

    file_list = _create_file_list(client)

    # Upload new file
    client.upload_file_to_box(destination_folder=BOX_DESTINATION_FOLDER,
                              fichero=file_list)


@profile
@task(pre=[delete_local_files],
      post=[call(sync_to_box, False), delete_local_files])
def daily_download(ctx, open_date="01/01/2017"):
    """
    Download daily delta

    :param open_date:
        Earliest open date.
    """
    parsed_date = parse_date(open_date)
    yesterday = date.today() - timedelta(days=1)
    download_files(ctx, open_date=parsed_date, update_date=yesterday)


@profile
@task(pre=[delete_local_files],
      post=[call(sync_to_box, True), delete_local_files])
def weekly_download(ctx, open_date="01/01/2017"):
    """
    Downloads full data

    :param open_date:
        Earliest open date.
    """
    parsed_date = parse_date(open_date)
    download_files(ctx, open_date=parsed_date,
                   update_date=parsed_date)


@task(pre=[delete_local_files], post=[delete_local_files])
def daily_update(ctx, open_date="01/01/2017"):
    """
    Executes the daily job. If Monday downloads the full data
    :param open_date:
        Earliest open date.
    """
    if date.today().weekday() == 0:
        weekly_download(ctx, open_date)
        sync_to_box(ctx, True)
    else:
        daily_download(ctx, open_date)
        sync_to_box(ctx, False)
    msg = print_prof_data()
    requests.post("https://nosnch.in/bb9030fe27", data={"m": msg})
    print(msg)


def _authenticate_box(oauth):
    raise Exception(f"Go to https://{HEROKU_APP_NAME}.herokuapp.com/"
                    f"authenticate to login")


def _create_file_list(client):
    # Get files on the Box folder
    local_filenames_json = client.list_box_folder_to_json(
        BOX_DESTINATION_FOLDER)

    # Dump to a json file
    file_list = BiFile(filename=FILE_LIST,
                       path=os.path.join(DOWNLOAD_PATH, FILE_LIST))
    with open(file_list.path, 'w') as outfile:
        json.dump(local_filenames_json, outfile)

    return file_list
