import pandas as pd
from utils import get_domain, replace_special_char, save_data
from googlesearch import search
import time
from utils import AVOID


unavoidable = pd.read_csv("1001_2000_unavoidable.csv")
# del names, emails, owners, tags
start = 403
stop = len(unavoidable)
names = unavoidable.loc[start:stop, "name"]
emails = unavoidable.loc[start:stop, "mail"]
owners = unavoidable.loc[start:stop, "owner"]
tags = unavoidable.loc[start:stop, "tag"]

for name, email, owner, tag in zip(names, emails, owners, tags):
    # print(type(str(name)), email)
    if (name in AVOID) or( str(name) == "nan"):
        query = f"{get_domain(email)[0]} {get_domain(email)[-1]} linkedin profile"
        query = replace_special_char(query)
    else:
        query = f"{name} {get_domain(email)[-1]} linkedin profile"
        query = replace_special_char(query)
        
    print(query)
    try:
        results = search(query, num_results=10)
        links = []

        for result in results:
            links.append(result)
        # print(links)
        print(links[0])
        save_data([links[0],name, email, owner, tag], "u-1001_2000.csv")
    except Exception as e:
        print(e)
        time.sleep(510)
        results = search(query, num_results=10)
        for result in results:
            links.append(result)
        print(links[0])
        save_data([links[0],name, email, owner, tag], "u-1001_2000.csv")
    
    # sys.exit()