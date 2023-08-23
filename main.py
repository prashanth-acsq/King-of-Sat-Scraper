import os
import re
import sys
import html
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore")

OUTPUT_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "output")


def save_info(sat_name: str, csv: bool=False) -> None:
    response: requests.Response = requests.get(f"https://en.kingofsat.net/sat-{sat_name}.php")
    html_doc = response.content
    soup = BeautifulSoup(html_doc, "html.parser")
    final_required_data_1: list = []
    final_required_data_2: list = []

    good_sat_data: list = soup.find_all(class_="frq")[1:]

    s_no: np.ndarray = np.arange(1, len(good_sat_data)+1)

    for k in range(len(good_sat_data)):
        sat_info: list = good_sat_data[k].find_all("td")[:-1]

        required_data_1: list = []
        for i in range(len(sat_info)):
            matches = re.findall("\>(.*?)\<", str(sat_info[i]))
            if i == 1:
                required_data_1.append(matches[4].strip())
            if i == 4:
                required_data_1.append(matches[1])
            if i == 5:
                required_data_1.append(matches[1])
            if i == 8:
                required_data_1.append(matches[1])
                required_data_1.append(matches[3])
            if i == 9:
                required_data_1.append("".join(matches[-1].split(",")))
            else:
                required_data_1.append(matches[0])
        required_data_1 = [k+1] + [ele.strip() for ele in required_data_1 if ele != ""]

        sat_ch_names: list = soup.find("div", {"id" : f"m{k}"}).find_all(class_="A3")
        required_data_2: list = []
        for i in range(len(sat_ch_names)):
            matches = re.findall("\>(.*?)\<", str(sat_ch_names[i]))
            required_data_2.append(matches[0])
        required_data_2 = ",\n".join([html.unescape(ele.strip()) for ele in required_data_2 if ele != ""])

        final_required_data_1.append(required_data_1)
        final_required_data_2.append(required_data_2)

    required_data_1_df = pd.DataFrame(data=final_required_data_1, columns=["S.No", "Pos", "Satellite", "Frequency", "Pol", "Txp", "Beam", "Standard", "Modulation", "SR/FEC_1", "SR/FEC_2", "Network_Bitrate", "NID", "TID"], index=None)
    required_data_2_df = pd.DataFrame(data=None, columns=["S.No", "Channel Name"], index=None)
    required_data_2_df["S.No"] = s_no
    required_data_2_df["Channel Name"] = final_required_data_2

    if csv:
        required_data_1_df.to_csv(f"{OUTPUT_PATH}/satellite_info_{sat_name}.csv", index=False)
        required_data_2_df.to_csv(f"{OUTPUT_PATH}/channels_{sat_name}.csv", index=False)
        required_data_1_df["Channels"] = final_required_data_2
        required_data_1_df.to_csv(f"{OUTPUT_PATH}/satellite_and_channels_info_{sat_name}.csv", index=False)
    else:
        required_data_1_df.to_excel(f"{OUTPUT_PATH}/satellite_info_{sat_name}.xlsx", index=False)
        required_data_2_df.to_excel(f"{OUTPUT_PATH}/channels_{sat_name}.xlsx", index=False)
        required_data_1_df["Channels"] = final_required_data_2
        required_data_1_df.to_excel(f"{OUTPUT_PATH}/satellite_and_channels_info_{sat_name}.xlsx", index=False)


def main():
    satellites: list = [
        "nilesat201",
        "nilesat301",
        "e25b",
        "eshail2",
        "badr4",
        "badr5",
        "badr6",
        "badr7",
	"arabsat5c",
    ]

    for satellite in satellites[:2]:
        save_info(satellite)

    
if __name__ == "__main__":
    sys.exit(main() or 0)