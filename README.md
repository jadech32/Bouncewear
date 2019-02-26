# Bouncewear Helper
- Quickly creates [mollie](https://www.mollie.com/en/) payment invoice links for shoes on [Bouncewear](https://bouncewear.com/en/category/schoenen) to assist in fast checkout process for hyped drops.
## Installation:
    1. Clone via git or download as zip file
    2. Install the requirements (done once per install)
```
     pip install -r requirements.txt
```
    3. Insert information into `config.example.json` and rename file to `config.json`.
    4. Adjust product keywords and webhook URL as needed.
## Set Up and Configuration:
### Initial Script Setup
- Enter product keywords and Discord webhook URL (Slack not supported) into the object constructor parameters in `main.py`

Example: If you wanted to search for `Under Armour Curry 6 'Yellow'`

```
c = Converse(["under","armour","curry","6","yellow"])
c.webhook("URL HERE")
```
- Insert profile and size information in `config.json`

### Proxy Support

- Create a ```config``` folder, and under that please create a ```proxies.txt``` and paste your HTTP proxies line by line.
- Now supports ```user:pass``` proxies as well as non auth proxies.
- Does not have support for non proxy scraping (use localhost).

### Config File
- Each profile in the array represents one item. To create checkouts for two items, insert two items into the array, and so on.
