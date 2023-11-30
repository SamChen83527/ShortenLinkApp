import argparse
import logging
import os
import sys
from pathlib import Path
from time import sleep

import pandas as pd
from dotenv import load_dotenv

from utils import AibafuTool, output_file

# create log folder
Path("./log").mkdir(parents=True, exist_ok=True)
# output log to file with now time
logging.basicConfig(
    filename=f"./log/{pd.Timestamp.now().strftime('%Y%m%d_%H')}.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
dev_logger: logging.Logger = logging.getLogger(name="dev")
dev_logger.setLevel(logging.DEBUG)
handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
dev_logger.addHandler(handler)

load_dotenv(".env")

VERSION = "V00.01.01"


if __name__ == "__main__":
    dev_logger.info(f"APP Version: {VERSION}")
    
    # prepare input args
    parser = argparse.ArgumentParser(description="Shorten URL APP")
    parser.add_argument("--version", "-V", action="version", version=f"{VERSION}")
    parser.add_argument("--file", "-f", type=str, help="input file path")
    parser.add_argument(
        "--gid",
        type=str,
        help="group id, if not input, default create new group by today",
    )
    parser.add_argument(
        "--key", type=str, help="api key, if not input, default use default key"
    )

    args = parser.parse_args()
    file_path = args.file

    if file_path is None:
        file_path = os.getenv("FILE_PATH")
        if file_path is None or file_path == "":
            dev_logger.error("Please input file path")
            sys.exit(0)
    else:
        if not Path(file_path).exists():
            dev_logger.error(f"File path not exists: {file_path}")
            sys.exit(0)
    file_path = Path(file_path)

    api_key = None
    group_id = None
    if args.key is not None:
        api_key = args.key
    if args.gid is not None:
        group_id = args.gid
    
    # init aibafu
    try:
        aibabu = AibafuTool(api_key, group_id)
    except Exception as e:
        dev_logger.error(f"{str(e)}")
        sys.exit(0)
        
    dev_logger.info(f"API_KEY: {aibabu.api_key}")
    dev_logger.info(f"GROUP_ID: {aibabu.group_id}")
    dev_logger.info(f"Input file: {file_path}")

    df = pd.read_excel(file_path)
    output_path = str(file_path).replace(
        ".xlsx", f'_shorten_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

    shorten_url_list = pd.DataFrame(columns=["Link", "shorten link"])
    created_today = 0
    cnt = 0
    for target_url in df["Link"]:
        # add time sleep
        sleep(0.21)  # API接口调用频率限制为5次/秒
        try:
            shorten_url = aibabu.get_shorten_url(target_url)
            shorten_url_list = pd.concat(
                [
                    shorten_url_list,
                    pd.DataFrame(
                        {
                            "Link": [target_url],
                            "shorten link": [shorten_url["render_url"]],
                        }
                    ),
                ],
                ignore_index=True,
            )
            created_today = shorten_url["created_today"]
            cnt += 1
            dev_logger.info(f'Count({cnt}): {shorten_url["render_url"]}')
            if cnt % 50 == 0:
                output_file(df, shorten_url_list, output_path)
        except Exception as e:
            dev_logger.error(f"{str(e)}")
            continue
    output_file(df, shorten_url_list, output_path)

    dev_logger.info(f"Process {cnt} urls")
    dev_logger.info(f"Created {created_today} urls today")
    dev_logger.info(f"Write to {output_path}")
