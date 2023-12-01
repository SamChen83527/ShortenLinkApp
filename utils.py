import datetime
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(".env")


class Settings:
    API_KEY: str = os.getenv("API_KEY")
    CONNECTION: str = os.getenv("CONNECTION")
    GROUP_ID: int = int(os.getenv("GROUP_ID"))


aibafu_settins = Settings()


class AibafuTool:
    def __init__(self, api_key: str = None, group_id: int = None) -> None:
        self.connection_url = aibafu_settins.CONNECTION
        if api_key is None:
            self.api_key = aibafu_settins.API_KEY
        if group_id is None:
            self.group_id = aibafu_settins.GROUP_ID
        if self.group_id == 0:
            # get today date
            groups = self.get_group()
            """
            [
                {
                    "group_id": 481702,
                    "group_name": "默认分组",
                    "chain_num": 5968
                },
                {
                    "group_id": 489070,
                    "group_name": "RP SMS_20231121",
                    "chain_num": 0
                }
            ]
            """
            # get the group id which name is today
            today = datetime.datetime.today().strftime("%Y-%m-%d")
            group_id = [
                group["group_id"] for group in groups if group["group_name"] == today
            ]
            if len(group_id) == 0:
                # create group
                group_id = self.create_group(today)
                self.group_id = group_id
            else:
                self.group_id = group_id[0]

    def get_group(self):
        url = f"https://{self.connection_url}/v1/chainGroup/getChainGroup?apikey={self.api_key}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(response.text)
        if data["code"] == 1:
            return data["result"]
        else:
            raise Exception(data["msg"])

    def create_group(self, group_name: str):
        url = f"https://{self.connection_url}/v1/chainGroup/createChainGroup"
        payload = json.dumps({"apikey": self.api_key, "name": group_name})
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text)
        if data["code"] == 1:
            return data["result"]["group_id"]
        else:
            raise Exception(data["msg"])

    def get_shorten_url(self, target_url: str) -> dict:
        url = f"https://{self.connection_url}/v1/chain/createChain"
        payload = json.dumps(
            {
                "apikey": self.api_key,
                "target_url": target_url,
                "group_id": self.group_id,
            }
        )
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text)
        if data["code"] == 1:
            return data["result"]
        else:
            raise Exception(data["msg"])


def output_file(df, shorten_url_list, output_path):
    try:
        df = pd.merge(df, shorten_url_list, on="Link", how="left")
        df.to_excel(output_path, index=False)
    except Exception as e:
        from app import dev_logger

        dev_logger.error(f"{str(e)}")
        return
