import json

f = open('./config.json')
config = json.load(f)

print(config['URL'])
for k, v in config.items() :
    print(k, ":", v)

