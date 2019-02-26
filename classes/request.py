import requests

class Request:

    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = requests.Session()
        self.jar = requests.cookies.RequestsCookieJar()

    def make_request(self, url, method="GET", payload=None, headers=None, redirect=False):
        if self.proxy is not None:
            if method == "GET":
                if headers is not None:
                    return self.session.get(url, cookies=self.jar, headers=headers, verify=False,
                                            allow_redirects=redirect, proxies=self.proxy)
                else:
                    return self.session.get(url, cookies=self.jar, verify=False, allow_redirects=redirect,
                                            proxies=self.proxy)
            if method == "POST":
                if headers is not None:
                    return self.session.post(url, data=payload, cookies=self.jar, headers=headers, verify=False,
                                             allow_redirects=redirect, proxies=self.proxy)
                else:
                    return self.session.post(url, data=payload, cookies=self.jar, verify=False,
                                             allow_redirects=redirect, proxies=self.proxy)
            if method == "OPTIONS":
                if headers is not None:
                    return self.session.options(url, cookies=self.jar, headers=headers, verify=False,
                                                allow_redirects=redirect, proxies=self.proxy)
                else:
                    return self.session.options(url, cookies=self.jar, verify=False, allow_redirects=redirect,
                                                proxies=self.proxy)
        else:
            if method == "GET":
                if headers is not None:
                    return self.session.get(url, cookies=self.jar, headers=headers, verify=False,
                                            allow_redirects=redirect)
                else:
                    return self.session.get(url, cookies=self.jar, verify=False, allow_redirects=redirect)
            if method == "POST":
                if headers is not None:
                    return self.session.post(url, data=payload, cookies=self.jar, headers=headers, verify=False,
                                             allow_redirects=redirect)
                else:
                    return self.session.post(url, data=payload, cookies=self.jar, verify=False,
                                             allow_redirects=redirect)
            if method == "OPTIONS":
                if headers is not None:
                    return self.session.options(url, cookies=self.jar, headers=headers, verify=False,
                                                allow_redirects=redirect)
                else:
                    return self.session.options(url, cookies=self.jar, verify=False, allow_redirects=redirect)

    def make_request_retry(self, url, method="GET", payload=None, headers=None, redirect=False):
        resp = self.make_request(url, method, payload, headers, redirect)
        while resp.status_code != 200:
            print(resp.status_code)
            resp = self.make_request(url, method, payload, headers, redirect)
        return resp
