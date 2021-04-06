from seleniumwire import webdriver


class Interceptor:

    def __init__(self, url):
        self.driver = webdriver.Chrome('D:\\Python\\Vulnerability\\chromedriver.exe')
        self.target_url = url

    def need_intercept(self, header_name, new_header_value):
        def interceptor(request):
            if request.headers[header_name]:
                del request.headers[header_name]
            request.headers[header_name] = new_header_value
        self.driver.request_interceptor = interceptor
        self.driver.get(self.target_url)
        for request in self.driver.requests:
            if str(request.url).find("http://192.168.108.143/dvwa/") != -1:
                print("\nRequest URL:\n\n" + str(request.url))
                #print("\nRequest Headers:\n\n" + str(request.headers))
                print("\nResponse Headers:\n\n" + str(request.response.headers))
        self.driver.close()

