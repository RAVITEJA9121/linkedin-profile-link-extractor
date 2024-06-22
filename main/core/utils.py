import pandas as pd
import csv

def get_mail_id(path:str, start= 0, stop = 10):
    try:
        data = pd.read_csv("coditas_contacts.csv")
        emails = list(data.loc[start:stop,"e-mail"])
    except Exception as e:
        return e
    
    return emails

def save_data(data: list, file_name:str):
    try:
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            # print("saving....")
            writer.writerows([data])
    except Exception as e:
        return e
    return True

def exists(all_ids: list, partial_ids: list):
    pending_mails = []
    for mail in partial_ids:
        if mail not in all_ids:
            pending_mails.append(mail)
    return pending_mails

def get_domain(mail_id: str):
    name = mail_id.split("@")[0]
    domain = mail_id.split("@")[-1].split(".")[0]
    # user_name = f"{name} {domain}"
    return name, domain