"""
SDU Console Application
Version 0.1.0
"""
import cmd
import requests
import getpass
from termcolor import colored
from tabulate import tabulate
from bs4 import BeautifulSoup

START_URL = "https://obs.sdu.edu.tr/index.aspx"
GRADES_URL = "https://obs.sdu.edu.tr/Birimler/Ogrenci/Derslerim.aspx"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/37.0.2062.120 Safari/537.36"}
FIELDS = ("__EVENTTARGET", "__EVENTARGUMENT", "__VIEWSTATEFIELDCOUNT",
          "__VIEWSTATE", "__VIEWSTATE1", "__EVENTVALIDATION",
          "__PREVIOUSPAGE", "buttonTamam")


LOG_TYPES = {"debug": "white", "info": "blue", "error": "red"}


def print_log(msg, level="debug"):
    print colored(">>> {0}".format(msg), LOG_TYPES[level])

def print_logv(msg, level="debug"):
    print colored("{0}".format(msg), LOG_TYPES[level])

def status_formatter(pred, tmsg="Success", fmsg="Error"):
    return tmsg.upper() if pred else fmsg.upper()


class SDUCMD(cmd.Cmd):
    """
    SDU Console Client Class
    """

    def __init__(self):
        """

        :return:
        """
        cmd.Cmd.__init__(self)

        self.intro = """\n\t $$$$$$\  $$$$$$$\  $$\   $$\  \n"""
        self.intro += """\t$$  __$$\ $$  __$$\ $$ |  $$ |\n"""
        self.intro += """\t$$ /  \__|$$ |  $$ |$$ |  $$ |\n"""
        self.intro += """\t\$$$$$$\  $$ |  $$ |$$ |  $$ |\n"""
        self.intro += """\t \____$$\ $$ |  $$ |$$ |  $$ |\n"""
        self.intro += """\t$$\   $$ |$$ |  $$ |$$ |  $$ |\n"""
        self.intro += """\t\$$$$$$  |$$$$$$$  |\$$$$$$  |\n"""
        self.intro += """\t \______/ \_______/  \______/ \n\n"""
        self.intro += """\tSuleyman Demirel University\n"""
        self.intro += """\t\tVersion: 0.1.0\n"""

        self.intro = colored(self.intro, "cyan")
        self.prompt = colored(">> ", "cyan")
        self.ruler = "-"
        self.doc_header = "Commands - type help <command> for more info"
        self.request_data = {}
        self.response = {}
        self.username = None
        self.is_login = False
        self.is_requested = False

    def __first_request(self):
        """
        Get the request and parse ASP.NET validators
        :return:
        """
        if not self.is_requested:
            self.session = requests.Session()
            self.session.headers.update(HEADERS)

            try:
                self.response['first_request'] = self.session.get(START_URL)
            except requests.ConnectionError:
                return False

            self.parsed = BeautifulSoup(self.response['first_request'].content)

            for field in FIELDS:
                data = self.parsed.find(id=field)['value']
                self.request_data[field] = data
            return True
        else:
            return True

    def do_login(self, line):
        """
        Do login with username and password.
        :param line:
        :return:
        """
        self.is_requested = self.__first_request()
        if not self.is_requested:
            print_log("Connection error.", "error")
            return
        if not self.is_login:
            self.username = raw_input("{0}Student ID: ".format(colored(">>> ", "cyan")))
            password = getpass.getpass("{0}Password: ".format(colored(">>> ", "cyan")))
            try:
                self.request_data["textKulID"] = self.username
                self.request_data["textSifre"] = password
                self.response['info_page'] = self.session.post(START_URL, data=self.request_data)
                if not self.response['info_page'].url == START_URL:
                    print_log("Login success.", "info")
                    self.is_login = True
                else:
                    print_log("Username or password wrong.", "error")
                    self.is_login = False
            except requests.ConnectionError:
                print_log("Connection error.", "error")
                self.is_login = False
        else:
            print_log("Already logon.", "info")

    def do_grades(self, line):
        """

        :return
        """
        if self.is_login:
            try:
                self.response['grades_page'] = self.session.get(GRADES_URL)
                parsed = BeautifulSoup(self.response['grades_page'].content)
                # @todo: print grades in table
            except:
                print_log("Connection error.", "error")
        else:
            print_log("Please login first.", "info")


    def do_info(self, line):
        """

        :return:
        """
        if self.is_login:
            self.parsed = BeautifulSoup(self.response['info_page'].content)
            name = self.parsed.find(id="ctl00_ContentPlaceHolder1_OgrenciTemelBilgiler1_textAdi").text
            surname = self.parsed.find(id="ctl00_ContentPlaceHolder1_OgrenciTemelBilgiler1_textSoyadi").text
            year = self.parsed.find(id="ctl00_ContentPlaceHolder1_OgrenciTemelBilgiler1_textSinif").text
            mail = self.parsed.find(id="ctl00_ContentPlaceHolder1_OgrenciTemelBilgiler1_textSDUMail").text

            table = [[self.username, name, surname, year, mail]]
            headers= ["Student ID", "Name", "Surname", "Year", "Mail"]

            tabulate(table, headers, tablefmt="grid")
            print_logv(tabulate(table, headers, tablefmt="grid"), "info")
        else:
            print_log("Please login first.", "info")

    def do_status(self, line):
        """

        """
        print_log("{0:20} {1:10}".format("Student ID:", status_formatter(self.username, self.username, "Empty")), "info")
        print_log("{0:20} {1:10}".format("First request:", status_formatter(self.is_requested)), "info")
        print_log("{0:20} {1:10}".format("Login:", status_formatter(self.is_login)), "info")

    def do_exit(self, line):
        """
        Exits from the console
        """
        return -1

    def do_quit(self, line):
        """
        Exits from the console
        """
        return self.do_exit(line)

    def do_EOF(self, line):
        """
        Exit on system end of file character
        """
        return self.do_exit(line)


if __name__ == "__main__":
    SDUCMD().cmdloop()