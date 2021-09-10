import json
f = open('./config.json')
config = json.load(f)

# URL = "https://24h.pchome.com.tw/prod/DGBJC0-A9009NXHL?fq=/S/DGBJC0"
URL = config["URL"]
# DRIVER_PATH = "chromedriver.exe"
# CHROME_PATH = r"--user-data-dir=C:\\<chrome 設定檔路徑>"  # 可透過網址列輸入 chrome://version/ 找到
CHROME_PATH = r"--user-data-dir=/Users/jetec-rd/Library/Application Support/Google/Chrome/Default"  # 可透過網址列輸入 chrome://version/ 找到

### Only for Mac ###
DRIVER_PATH = "/usr/local/bin/chromedriver"
### Only for Mac (End) ###

# 請注意！以下皆為機密個資，請小心謹慎，勿上傳至公開平台
ACC = config["ACC"]
PWD = config["PWD"]
BuyerSSN = config["SSN"]
BirthYear, BirthMonth, BirthDay = config["Birth"]["Year"], config["Birth"]["Month"], config["Birth"]["Day"]
multi_CVV2Num = config["Credit"]["CVV"]
