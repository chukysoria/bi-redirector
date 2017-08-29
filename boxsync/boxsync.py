"""
BoxSync
"""
import json
import os
import webbrowser

from boxsdk import Client, OAuth2
from boxsdk.exception import BoxAPIException, BoxOAuthException

from boxsync.bifile import BiFile
from boxsync.boxresponse import FLASK_APP


class BoxKeysStoreFile:
    """
    Class to be extended with default read/save tokens
    """
    def __init__(self, keys_path='keys.json'):
        self.keys_path = keys_path

    def get_oauth(self):
        """
        Creates an Oauth object

        :return:
            oauth object.
        :rtype:
            :class:`boxsdk.Oauth2`
        """
        values = self._read_token()
        oauth = OAuth2(
            client_id=values['clientID'],
            client_secret=values['clientSecret'],
            access_token=values['accessToken'],
            refresh_token=values['refreshToken'],
            store_tokens=self._store_tokens
        )
        return oauth

    def _read_token(self):
        """Read token values from keys file"""
        with open(self.keys_path) as data_file:
            return json.load(data_file)

    def _store_tokens(self, access_token, refresh_token):
        """
        Store token values in keysfile.
        :param access_token:
            Box Access token
        :param refresh_token:
            Box Refresh token
        """
        data = self._read_token()
        data['accessToken'] = access_token
        data['refreshToken'] = refresh_token
        with open(self.keys_path, 'w') as outfile:
            json.dump(data, outfile)


class BoxAuthenticateInteractive:
    """
    Class to be called if client is not authenticated

    :param server_hostname:
        Host of the webserver
    :param server_port:
        Port of thhe webserver
    """

    def __init__(self, server_hostname='localhost', server_port='5000'):
        self.server_hostname = server_hostname
        self.server_port = server_port

    def authenticate(self, oauth):
        """
        Launch a webrowser to authenticate the client.

        :param oauth:
            Oauth object.
        :return:
            An oauth valid box.
        :rtype:
            :class:`boxsdk.OAuth2`
        """
        redirect_url = (f"http://{self.server_hostname}:"
                        f"{self.server_port}/boxauth")
        auth_url, csrf_token = oauth.get_authorization_url(redirect_url)
        # Launch web browser
        webbrowser.open(auth_url)
        # Create web server and pass the info
        FLASK_APP.config['csrf_token'] = csrf_token
        FLASK_APP.config['oauth'] = oauth
        # Server will shutdown after receiving the token
        FLASK_APP.run(self.server_hostname, port=self.server_port)
        return oauth


class BoxSync:
    """
    Sync objects from PC to Box

    :param keys_store:
        Path to Box keys file
    :param authenticate_method:
        Fuunction
    """

    def __init__(self, keys_store=None, authenticate_method=None):
        if keys_store is None:
            self.keys_store = BoxKeysStoreFile()
        else:
            self.keys_store = keys_store

        if authenticate_method is None:
            self.authenticate = BoxAuthenticateInteractive().authenticate
        else:
            self.authenticate = authenticate_method

        # Authenticate client
        self.oauth = self.keys_store.get_oauth()
        print("Authenticating...")
        self.client = self._validate_auth(self.oauth)
        print("Authenticated.")

    def _validate_auth(self, oauth):
        """
        Validates and oauth and return a client object. If it fails launch
        the authentication process.

        :param oauth:
            Oauth object.
        :type oauth:
            :class:`boxsdk.Oauth2`
        :return:
            A validated Client object
        :rtype:
            :class:`boxsdk.Client`
        """
        try:
            client = Client(oauth)
            client.user(user_id='me').get(fields='login')
            return client
        except (BoxOAuthException, BoxAPIException):
            # Reauthenticate
            oauth = self.authenticate(oauth)
            return Client(oauth)

    def sync_folder(self, local_path, box_folder_id, create_link=False,
                    delete_files_remotely=True):
        """
        Sync a local folder to the designated Box folder.
        :param local_path:
            Path of the folder to sync.
        :param box_folder_id:
            ID of Box Folder to upload to.
        :param create_link:
            (optional) Creates a Shared Link to the file. Default `False`
        :param delete_files_remotely:
            Deletes in Box files not found in local folder. Defaul `True`
        """
        # Read current local files
        local_filenames = {}
        print(f"Searching files on {local_path}...")
        for fichero in os.scandir(local_path):
            local_file = BiFile()
            local_file.path = fichero.path
            local_file.filename = fichero.name
            local_filenames[fichero.name] = local_file
        print(f"Found {len(local_filenames)} files.")

        # Delete online files not present offline
        if delete_files_remotely:
            # Read online files
            box_files = self.list_box_folder(box_folder_id=box_folder_id,
                                             fields=['name'])
            for boxfile in box_files:
                if boxfile.name not in local_filenames.keys():
                    # Delete file if not found locally
                    boxfile.delete()
                    print(f"{boxfile.name} deleted.")

        # Upload new and modified files to box
        for fichero in local_filenames.values():
            self.upload_file_to_box(destination_folder=box_folder_id,
                                    fichero=fichero,
                                    create_link=create_link)

    def list_box_folder_to_json(self, box_folder_id):
        """
        List the contents of a folder and returns a json file.

        :param box_folder_id:
            ID of Box Folder to upload to.
        :type box_folder_id:
            `unicode`
        :return:
            Serialized list of items on BoxFolder
        :type create_link:
            `list`
        """
        # List box files
        box_files = self.list_box_folder(box_folder_id=box_folder_id,
                                         fields=['name', 'shared_link'])
        # Fulfill sharedlinks
        folder_list = {}
        for boxfile in box_files:
            bifile = BiFile(filename=boxfile.name,
                            shared_link=boxfile.shared_link['download_url'])
            folder_list[bifile.filename] = bifile

        local_filenames_json = {}
        for key, fichero in folder_list.items():
            local_filenames_json[key] = fichero.to_json()

        return local_filenames_json

    def list_box_folder(self, box_folder_id, fields=None):
        """
        List the contents of a folder

        :param box_folder_id:
            Box folder id
        :type box_folder_id:
            `unicode`
        :param fields:
            List of fields to download. Default: all
        :type fields:
            `list`
        :return:
            List of BoxItems
        :type create_link:
            `list`
        """
        fld = self.client.folder(box_folder_id)
        print("Searching files on Box...")
        box_files = fld.get_items(limit=100, fields=fields)
        print(f"Found {len(box_files)} files.")
        return box_files

    def upload_file_to_box(self, destination_folder, fichero,
                           create_link=False):
        """
        Uploads a file to a Box Folder.

        :param destination_folder:
            Box destination folder ID
        :type destination_folder:
            :class:`boxsdk.object.folder`
        :param fichero:
            File object to upload.
        :type fichero:
            :class:`BoxFile`
        :param create_link:
            Creates a Shared Link to the file. Default `False`
        :type create_link:
            `bool`
        """
        fld = self.client.folder(destination_folder)
        try:
            boxfile = fld.upload(file_path=fichero.path,
                                 upload_using_accelerator=True,
                                 preflight_check=True)
            print(f"{fichero.filename} uploaded.")
            # Create link
            if create_link:
                boxfile.get_shared_link_download_url(access='open')
        except BoxAPIException as ex:
            if ex.status == 409:  # Item_name_in_use
                file_hash = ex.context_info['conflicts']['sha1']
                # Check if file has locally changed
                if file_hash == fichero.sha1:
                    print(f"{fichero.filename} already exists.")
                else:
                    file_id = ex.context_info['conflicts']['id']
                    self.client.file(file_id).update_contents(
                        file_path=fichero.path,
                        upload_using_accelerator=True)
                    print(f"{fichero.filename} new version uploaded.")
            else:
                raise ex
        except PermissionError as ex:
            print(f"Permission denied: {ex.strerror}")
