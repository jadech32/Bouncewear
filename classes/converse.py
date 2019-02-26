from classes.logger import Logger
from classes.request import Request
from classes.proxies import Proxy

import requests
import json
import threading
from dhooks import Webhook, Embed
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers_ua = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/70.0.3538.75 Mobile/15E148 Safari/605.1",
}

headers_post_base = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://bouncewear.com"
        }


class Converse:

    def __init__(self, kw):
        self.request_g = Request()
        self.proxy = Proxy()
        self.kw = kw
        self.url = None
        self.log = Logger("Main").log
        self.webhook_url = None

    def webhook(self, url):
        self.webhook_url = url

    def load_config(self):
        with open('config/config.json', 'r') as f:
            s = f.read()
            return json.loads(s)

    def search_kw(self):
        url = "https://bouncewear.com/en/category/schoenen"

        resp = self.request_g.make_request_retry(url, "GET", headers=headers_ua)
        soup = BeautifulSoup(resp.content, 'html.parser')
        shoe_list = soup.find_all("div", {"class": "product-overview-grid__item"})

        for shoe in shoe_list:
            url = shoe.find("a")["href"]
            details = shoe.find("div", {"class": "product__details"})
            name = details.find("p", {"class": "product__name"}).text.strip()
            if all(i in name.lower() for i in self.kw):
                self.url = url
                self.log("Product Found: " + name, "success")
                return True

        return False

    def run(self):
        self.log("Scraping for keywords: " + str(self.kw), "yellow")

        found_shoe = False

        while not found_shoe:
            found_shoe = self.search_kw()

        self.log("Starting Tasks", "success")

        proxy_list = self.proxy.getProxy()
        count = 0
        for profile in self.load_config():
            i = Individual(profile, self.url, proxy_list[self.proxy.countProxy()], count, self.webhook_url)
            t = threading.Thread(target=i.start_flow, args=())
            count += 1
            t.start()


class Individual:

    def __init__(self, profile, url, proxy, count, webhook):
        self.select_offset = count
        self.webhook_url = webhook
        self.sizes = None
        self.cookie_xsrf = None
        self.cookie_session = None
        self.cookie_cfduid = None
        self._token = None
        self.request_g = Request(proxy)
        self.profile = profile
        self.url = url
        self.proxy = proxy
        self.session = requests.Session()
        self.jar = requests.cookies.RequestsCookieJar()
        self.log = None
        self.selected_size = None
        self.selected_product = None

    def start_flow(self):
        # Init Variables
        checkout_shipping = False
        checkout_method = False
        checkout_payment = False

        self.log = Logger(threading.get_ident()).log

        added_to_cart = False

        while not added_to_cart:
            token = self.get_size_info()
            sizeId = self.choose_size()
            if sizeId is False:
                exit(1)
            added_to_cart = self.add_to_cart(token, sizeId)
        self.log("Successfully added to cart", "success")
        while not checkout_shipping:
            checkout_shipping = self.checkout_detail()

        while not checkout_method:
            checkout_method = self.checkout_method()

        while not checkout_payment:
            checkout_payment = self.checkout_payment()

    def get_size_info(self):
        resp = self.request_g.make_request_retry(self.url, "GET")
        soup = BeautifulSoup(resp.content, "html.parser")

        # Get Product Name
        self.selected_product = soup.find("h2", {"class": "product-detail__title"}).text

        sizes_list = soup.find("ul", {"id": "variationselect"}).find_all("li")
        dict = {}
        for size in sizes_list:
            size_name = size.find("input")["value"]
            size_value = size.find("input")["data-variationid"]
            availability = size.find("label").text
            if "not in stock" not in availability:
                self.selected_size = size_name
                dict[size_name] = size_value
        self.sizes = dict
        if len(self.sizes) == 0:
            self.log("Out of Stock, exiting.", "error")
            exit(1)
        else:
            self.log("Grabbed Size Information", "yellow")

        # Grab Token
        token = soup.find("input", {"name": "_token"})["value"]
        self._token = token
        self.log("Grabbed Session Token: " + token, "info")

        # Grab Cookies
        self.cookie_xsrf = resp.cookies.get("XSRF-TOKEN")
        self.cookie_cfduid = resp.cookies.get("__cfduid")
        self.cookie_session = resp.cookies.get("bouncewear_session")
        return token

    def choose_size(self):
        selected = None
        profile_size = self.profile["size"] + " - EU"
        list_len = len(self.sizes) - self.select_offset

        for size in self.sizes:
            if profile_size in size:
                selected = self.sizes[size]
                self.selected_size = size
            if list_len is 0:
                break
        if selected is None:
            selected = list(self.sizes.values())[len(self.sizes) - 1 - self.select_offset]
            self.log("Size " + profile_size + " not in stock. Exiting Thread", "error")
            return False

        self.log("Selected Size: " + self.selected_size + " - " + selected, "yellow")
        return selected

    def add_to_cart(self, token, size_id):

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "referer": self.url,
            "accept": "*/*",
            "x-requested-with": "XMLHttpRequest",
            "origin": "https://bouncewear.com"
        }

        payload = {
            "_token": token,
            "action": "add_item",
            "rafflecode": 0,
            "variations[]": int(size_id)
        }

        resp = self.request_g.make_request("https://bouncewear.com/shoppingcart", "POST", payload=payload, headers=headers, redirect=False)

        if resp.status_code == 200 and resp.json()["message"] == "Product toegevoegd":
            return True
        else:
            error_msg = resp.json()["message"]
            self.log("Unable to Add to Cart. Retrying - " + error_msg, "error")
            return False

    def checkout_detail(self):
        self.request_g.make_request_retry("https://bouncewear.com/en/checkout")
        # Send Shipping

        payload = {
            "_token": self._token,
            "buyer_email": self.profile["email"],
            "shipping_firstname": self.profile["firstname"],
            "shipping_name": self.profile["lastname"],
            "shipping_extra": "",
            "shipping_street": self.profile["street"],
            "shipping_number": self.profile["street_number"],
            "shipping_bus": "",
            "shipping_city": self.profile["city"],
            "shipping_zip": self.profile["zip"],
            "shipping_state": self.profile["state"],
            "shipping_country": self.profile["country"],
        }

        headers = headers_post_base
        headers["referer"] = "https://bouncewear.com/en/checkout/info"

        resp = self.request_g.make_request_retry("https://bouncewear.com/en/checkout/shipping", "POST", payload=payload, headers=headers, redirect=False)

        if resp.status_code == 200:
            self.log("Sent Shipping Details", "yellow")
            return True
        else:
            return False

    def checkout_method(self):
        # Select method: Ship

        payload = {
            "_token": self._token,
            "deliverymethod": "ship"
        }

        headers = headers_post_base
        headers["referer"] = "https://bouncewear.com/en/checkout/shipping"

        resp = self.request_g.make_request_retry("https://bouncewear.com/en/checkout/payment", "POST", payload=payload,
                                                 headers=headers, redirect=False)

        if resp.status_code == 200:
            self.log("Sent Shipping Method", "yellow")
            return True
        else:
            return False

    def checkout_payment(self):
        # Go to Payment

        payload_payment = {
            "_token": self._token,
            "payment_method": "creditcard",
            "billingaddress": "same",
            "billing_firstname": self.profile["firstname"],
            "billing_name": self.profile["lastname"],
            "billing_extra": "",
            "billing_vata": "",
            "billing_street": self.profile["street"],
            "billing_number": self.profile["street_number"],
            "billing_bus": "",
            "billing_city": self.profile["city"],
            "billing_zip": self.profile["zip"],
            "billing_state": self.profile["state"],
            "billing_country": self.profile["country"],
        }

        headers = headers_post_base
        headers["referer"] = "https://bouncewear.com/en/checkout/payment"

        resp = self.request_g.make_request("https://bouncewear.com/en/checkout/payment/go", "POST", payload=payload_payment,
                                                 headers=headers, redirect=True)

        if resp.status_code == 200:
            self.log("Got Payment link. Sending to Webhook", "success")
            self.log(resp.url, "success")
            self.send_webhook(resp.url)
            return True
        else:
            return False

    def send_webhook(self, link):
        try:
            hook = Webhook(self.webhook_url)

            embed = Embed(
                description='Bouncewear',
                color=0x1e0f3,
                timestamp='now'  # sets the timestamp to current time
            )
            embed.add_field(name="Product", value=self.selected_product)
            embed.add_field(name="Size", value=self.selected_size)
            embed.add_field(name="Link", value=link)

            hook.send(embed=embed)
        except:
            self.log("Invalid Webhook URL", "error")
