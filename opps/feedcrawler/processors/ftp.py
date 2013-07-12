#coding: utf-8
from ftplib import FTP
import urllib

from .base import BaseProcessor


class EFEXMLProcessor(BaseProcessor):

    TEMP_FOLDER = "/tmp"

    def connect(self):
        self.ftp = FTP(self.feed.source_url)
        self.ftp.login(self.feed.source_username, self.feed.source_password)
        if self.verbose:
            print self.ftp.getwelcome()
        return self.ftp

    def process_file(self, s):
        s = s.strip()
        s = s.replace("\n", "")
        ext = s.split('.')[-1]
        if ext not in ['XML', 'xml']:
            if self.verbose:
                print("Skipping non xml %s" % s)
            return
        if self.verbose:
            print("Retrieving file %s" % s)

        source_root_folder = self.feed.source_root_folder
        if not source_root_folder.endswith('/'):
            source_root_folder += "/"

        url = "ftp://{0}:{1}@{2}{3}{4}".format(self.feed.source_username,
                                               self.feed.source_password,
                                               self.feed.source_url,
                                               source_root_folder,
                                               s)
        if self.verbose:
            print url

        urllib.urlretrieve(url, filename="{}/{}".format(self.TEMP_FOLDER, s))

    def process(self):
        print self.connect()
        self.ftp.cwd(self.feed.source_root_folder)
        if self.verbose:
            print("Root folder changed to: %s" % self.feed.source_root_folder)
        # print self.ftp.retrlines('LIST')
        # self.ftp.retrbinary('RETR 20130703_22_BAS-Y-BRASIL.XML', open('/tmp/20130703_22_BAS-Y-BRASIL.XML', 'wb').write)
        self.ftp.retrlines('NLST', self.process_file)



# LIST retrieves a list of files and information about those files.
# NLST retrieves a list of file names.
# On some servers, MLSD retrieves a machine readable list of files and information
# about those files
