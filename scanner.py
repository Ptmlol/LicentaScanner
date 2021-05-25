#!usr/bin/env python

import vulnerability_scanner
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")


def main():
    # clears file if exits
    open('Report.txt', 'w').close()
    open('Web Application Link Map.txt', 'w').close()

    # appends to cleared file
    report_file = open("Report.txt", 'a')
    map_file = open('Web Application Link Map.txt', 'a')
    print("\t\t\t\t\t\t\t\t[@@@]\t\t\t\tREPORT\t\t\t\t[@@@]\n\n", file=report_file)
    print("\n\t\t[LOGIN REPORT]", file=report_file)
    ignored_list = [x.strip() for x in config_object["WEBURL"]["ignored"].split(',')]
    try_brute_force = vulnerability_scanner.LoginTests(
        config_object["CREDENTIAL"]["username"],
        config_object["WEBURL"]["login"],
        config_object["FILE"]["password_dict"],
        config_object["CREDENTIAL"]["wrong_username"],
        config_object["CREDENTIAL"]["known_password"],
        config_object["CREDENTIAL"]["certain_wrong_passwd"],
        config_object["WEBURL"]["logout"],
        report_file
    )
    found_password = try_brute_force.get_correct_password()

    if found_password:
        vuln_scanner = vulnerability_scanner.Scanner(
            config_object["WEBURL"]["target"],
            ignored_list,
            report_file,
            map_file
        )
        data_dict = {
            config_object["CREDENTIAL"]["username_field"]: config_object["CREDENTIAL"]["username"],
            config_object["CREDENTIAL"]["password_field"]: found_password,
            config_object["CREDENTIAL"]["login_field"]: config_object["CREDENTIAL"]["submit_field"]
        }
        vuln_scanner.session.post(config_object["WEBURL"]["login"], data=data_dict)
        vuln_scanner.run_scanner()
    else:
        report_file.write("OK! No Password Found From BruteForce Test!" + "\nProceeding With Manual Input Password\n")
        print("[END LOGIN REPORT]", file=report_file)
        vuln_scanner = vulnerability_scanner.Scanner(
            config_object["WEBURL"]["target"],
            ignored_list,
            report_file,
            map_file
        )
        data_dict = {
            config_object["CREDENTIAL"]["username_field"]: config_object["CREDENTIAL"]["username"],
            config_object["CREDENTIAL"]["password_field"]: config_object["CREDENTIAL"]["known_password"],
            config_object["CREDENTIAL"]["login_field"]: config_object["CREDENTIAL"]["submit_field"]
        }
        vuln_scanner.session.post(config_object["WEBURL"]["login"], data=data_dict)
        vuln_scanner.run_scanner()


if __name__ == "__main__":
    main()
