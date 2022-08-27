import os
import json
from pathlib import Path

database_folder = "./Database"
if not os.path.exists(database_folder):
    os.makedirs(database_folder)
    print(f"Made a directory: {database_folder}")
else:
    print(f"{database_folder} already exists")

with open('DataBase.json') as file:
    data = json.load(file)

server_count = 0
for server in data['servers']:
    try:
        os.mkdir(f"{database_folder}/{server}")
        print(f"Made a directory: {database_folder}/{server}")
        server_count += 1
    except:
        print(f"{database_folder}/{server} already exists")
        server_count += 1

if server_count > 0:
    folder_name_list = next(os.walk(database_folder))[1]
    for folder_name in folder_name_list:
        # First write general.json
        base = Path(database_folder)
        json_path = base / (f"{folder_name}") / ('general.json')
        general_data = {
            "chat_log_channel_id": data['servers'][f"{folder_name}"]['chat_log_channel_id'],
            "welcome_channel_id": data['servers'][f"{folder_name}"]['welcome_channel_id'],
        }
        json_path.write_text(json.dumps(general_data, indent=4))
        print(f"Wrote {database_folder}/{folder_name}/general.json")

        # Second write moderation.json
        base = Path(database_folder)
        json_path = base / (f"{folder_name}") / ('moderation.json')
        moderation_data = data['servers'][f"{folder_name}"]['moderation']
        json_path.write_text(json.dumps(moderation_data, indent=4))
        print(f"Wrote {database_folder}/{folder_name}/moderation.json")

        # Third write role_messages.json
        base = Path(database_folder)
        json_path = base / (f"{folder_name}") / ('role_messages.json')
        role_messages_data = data['servers'][f"{folder_name}"]['role_messages']
        json_path.write_text(json.dumps(role_messages_data, indent=4))
        print(f"Wrote {database_folder}/{folder_name}/role_messages.json")
    print(f"Converted the database for {server_count} servers")
else:
    print(f"There is nothing to convert, please invite the bot to a server")

input = input("Delete DataBase.json?\n")
if input.lower() in ('y', 'ye', 'yes', 'yay'):
    os.remove('DataBase.json')