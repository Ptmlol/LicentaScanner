#!usr/bin/env python

import vulnerability_scanner

def main():
    login_url = "http://192.168.0.171/dvwa/login.php"
    target_url = "http://192.168.0.171/dvwa/"
    links_to_ignore = ["http://192.168.0.171/dvwa/logout.php"]
    username = "admin"
    wrong_username = "certainwrong"
    username_field = "username"
    password_field = "password"
    login_field = "Login"
    pw_file = "passwd.txt"
    known_password = "password"
    certain_wrong_passwd = "onlyfortest"
    logout_url = "http://192.168.0.171/dvwa/logout.php"
    try_brute_force = vulnerability_scanner.login_tests(username, login_url, pw_file, wrong_username, known_password, certain_wrong_passwd, logout_url).get_correct_password() # in acelasi timp verifica multe..
    password = try_brute_force
    if try_brute_force:
        vuln_scanner = vulnerability_scanner.Scanner(target_url, links_to_ignore)
        data_dict = {username_field: username, password_field: password, login_field: "submit"}
        vuln_scanner.session.post(login_url, data=data_dict)
        vuln_scanner.run_scanner()
    else:
        print("\n[~~] No Password Found From BruteForce Test!\n" + "[~~] Proceeding With Manual Input Password\n")
        vuln_scanner = vulnerability_scanner.Scanner(target_url, links_to_ignore)
        data_dict = {username_field: username, password_field: known_password, login_field: "submit"}
        vuln_scanner.session.post(login_url, data=data_dict)
        vuln_scanner.run_scanner()
if __name__ == "__main__":
    main()