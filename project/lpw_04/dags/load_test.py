import os
import requests

OWNER = "SashaL01"
REPO = "online_retail_dataset"
FILE_PATH = "Online Retail.xlsx"

save_dir = os.path.join("dags", "data")
local_path = os.path.join(save_dir, "Online_Retail.xlsx")


os.makedirs(save_dir, exist_ok=True)

# link
raw_url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/{FILE_PATH.replace(' ', '%20')}"
print(f"Скачиваем файл с GitHub:\n{raw_url}\n")

# load
response = requests.get(raw_url)
response.raise_for_status()

# save
with open(local_path, "wb") as f:
    f.write(response.content)

print(f"Файл успешно скачан и сохранён по пути:\n{local_path}")
print(f"Размер файла: {len(response.content)} байт")