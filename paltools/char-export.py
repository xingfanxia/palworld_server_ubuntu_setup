import json
import os
import subprocess
import sys
import zlib
import array

UESAVE_TYPE_MAPS = [
    ".worldSaveData.CharacterSaveParameterMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.Key=Struct",
    ".worldSaveData.FoliageGridSaveDataMap.ModelMap.InstanceDataMap.Key=Struct",
    ".worldSaveData.MapObjectSpawnerInStageSaveData.Key=Struct",
    ".worldSaveData.ItemContainerSaveData.Key=Struct",
    ".worldSaveData.CharacterContainerSaveData.Key=Struct",
]

def main():
    
    # Warn the user about potential data loss.
    print('WARNING: Running this script WILL change your save files and could \
potentially corrupt your data. It is HIGHLY recommended that you make a backup \
of your save folder before continuing. Press enter if you would like to continue.')
    input('> ')
    
   
    uesave_path = sys.argv[1]
    save_path = sys.argv[2]
    host_guid = sys.argv[3]
    targ_guid = sys.argv[4]
    
    #
    #
    #testpath = save_path + '/LevelMeta.sav'
    #sav_to_json(uesave_path, testpath)
    #json_to_sav(uesave_path, testpath)
    #exit()
    # Apply expected formatting for the GUID.
    host_guid_formatted = '{}-{}-{}-{}-{}'.format(host_guid[:8], host_guid[8:12], host_guid[12:16], host_guid[16:20], host_guid[20:]).lower()
    
    level_sav_path = save_path + '/Save/Level.sav'
    host_sav_path = save_path + '/Save/Players/' + host_guid + '.sav'
    host_new_sav_path = save_path + '/Save/Players/' + host_guid + '.sav'
    level_json_path = level_sav_path + '.json'
    host_json_path = host_sav_path + '.json'
    
    # save_path must exist in order to use it.
    if not os.path.exists(save_path):
        print('ERROR: Your given <save_path> of "' + save_path + '" does not exist. Did you enter the correct path to your save folder?')
        exit(1)
    
    # Convert save files to JSON so it is possible to edit them.
    sav_to_json(uesave_path, level_sav_path)
    sav_to_json(uesave_path, host_sav_path)
    print('Converted save files to JSON')
    
    # Parse our JSON files.
    with open(host_json_path) as f:
        host_json = json.load(f)
    with open(level_json_path) as f:
        level_json = json.load(f)
    print('JSON files have been parsed')
    
    #Container key at key/struct/struct/id/struct/value/guid
    
    host_instance_id = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["IndividualId"]["Struct"]["value"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
    
    # Search for and replace the final instance of the 00001 GUID with the InstanceId.
    instance_ids_len = len(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"])
    
    
    count = 0
    found = 0
    expected_containers = 7
    exported_map = {}
    param_maps = []
    palcount = 0
    for i in range(instance_ids_len):
        instance_id = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
        if instance_id == host_instance_id:
            #level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] = host_guid_formatted
            exported_map = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]
            count = count + 1
            found = 1
        elif level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] == host_guid_formatted or level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] == "00000000-0000-0000-0000-000000000000":
            param_maps.append(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i])
            palcount += 1
            
    if not found:
        print("Couldn't find character instance data to export")
        exit()
    print("Found Character Parameter Map")
    print("Read " + str(palcount) + " pals from source save")
    
    print("Searching for container data")
    inv_info = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["inventoryInfo"]
    inv_main = inv_info["Struct"]["value"]["Struct"]["CommonContainerId"]
    inv_key = inv_info["Struct"]["value"]["Struct"]["EssentialContainerId"]
    inv_weps = inv_info["Struct"]["value"]["Struct"]["WeaponLoadOutContainerId"]
    inv_armor = inv_info["Struct"]["value"]["Struct"]["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["Struct"]["value"]["Struct"]["FoodEquipContainerId"]
    inv_pals = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PalStorageContainerId"]
    inv_otomo = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["OtomoCharacterContainerId"]
    
    host_main = {}
    host_key = {}
    host_weps = {}
    host_armor = {}
    host_foodbag = {}
    host_pals = {}
    host_otomo = {}
    count = 0
    
    container_ids_len = len(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"])
    
    for i in range(container_ids_len):
        container = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]
        container_id = container["key"]["Struct"]["Struct"]["ID"]["Struct"]["value"]["Guid"]
        if container_id == inv_pals["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host pal inventory")
            host_pals = container
            count = count + 1
        elif container_id == inv_otomo["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host otomo inventory")
            host_otomo = container
            count = count + 1
        if count >= 2:
            print("Found all pal containers")
            break
            
    container_ids_len = len(level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"])
    
    for i in range(container_ids_len):
        container = level_json["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]
        container_id = container["key"]["Struct"]["Struct"]["ID"]["Struct"]["value"]["Guid"]
        if container_id == inv_main["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host main inventory")
            host_main = container
            count = count + 1
        elif container_id == inv_key["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host key inventory")
            host_key = container
            count = count + 1
        elif container_id == inv_weps["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host weapon inventory")
            host_weps = container
            count = count + 1
        elif container_id == inv_armor["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host armor inventory")
            host_armor = container
            count = count + 1
        elif container_id == inv_foodbag["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found host food bag inventory")
            host_foodbag = container
            count = count + 1
        if count >= expected_containers:
            print("Found all target containers")
            break
        
    if count < expected_containers:
        print("Missing container info! Only found " + str(count))
        exit()
        
    
    t_level_sav_path = save_path + '/Target/Level.sav'
    t_host_sav_path = save_path + '/Target/Players/' + targ_guid + '.sav'
    
    t_guid_formatted = '{}-{}-{}-{}-{}'.format(targ_guid[:8], targ_guid[8:12], targ_guid[12:16], targ_guid[16:20], targ_guid[20:]).lower()
    
    t_level_json_path = t_level_sav_path + '.json'
    t_host_json_path = t_host_sav_path + '.json'
    
    sav_to_json(uesave_path, t_level_sav_path)
    sav_to_json(uesave_path, t_host_sav_path)
    
    input("Confirm proceed after checking files> ")
    
    with open(t_host_json_path) as f:
        targ_json = json.load(f)
    with open(t_level_json_path) as f:
        targ_lvl = json.load(f)
        
    host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"]
    host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["IndividualId"]["Struct"]["value"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"] = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["IndividualId"]["Struct"]["value"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
    
    targ_id_as_bytes = []
    targ_id_str = ""
    for i in range(8):
        targ_id_as_bytes.append(int(targ_guid[(7-i)*2:(7-i)*2+2],16))
    print("Target ID as bytes is " + str(targ_id_as_bytes))
    
    instance_ids_len = len(targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"])
    char_instanceid = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["IndividualId"]["Struct"]["value"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
    
    print("Transferring profile data...")
    if "TechnologyPoint" in host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]:
        targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["TechnologyPoint"] = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["TechnologyPoint"]
    else:
        if "TechnologyPoint" in targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]:
            targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["TechnologyPoint"]["Int"]["value"] = 0
            
    if "bossTechnologyPoint" in host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]:
        targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["bossTechnologyPoint"] = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["bossTechnologyPoint"]
    else:
        if "bossTechnologyPoint" in targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]:
            targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["bossTechnologyPoint"]["Int"]["value"] = 0
    targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["UnlockedRecipeTechnologyNames"] = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["UnlockedRecipeTechnologyNames"]
    targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["RecordData"] = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["RecordData"]
    targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PlayerCharacterMakeData"] = host_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PlayerCharacterMakeData"]

    
    found = 0
    index = 0
    for i in range(instance_ids_len):
        instance_id = targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][i]["key"]["Struct"]["Struct"]["InstanceId"]["Struct"]["value"]["Guid"]
        if instance_id == char_instanceid:
            found = 1
            index = i
            break
            
    if found > 0:
        print("Existing character parameter map found, overwriting")
        targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"][index]["value"] = exported_map["value"]
    else:
        print("Couldn't find character paramater map, aborting")
        exit()

    maps_length = len(param_maps)
    target_id = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"]
    palcount = 0
    for i in range(maps_length):
        #param_maps[i]["key"]["Struct"]["Struct"]["PlayerUId"]["Struct"]["value"]["Guid"] = target_id
        #for j in range(8):
            #param_maps[i]["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"]["Byte"]["Byte"][1350+j] = targ_id_as_bytes[j]
            #param_maps[i]["value"]["Struct"]["Struct"]["RawData"]["Array"]["value"]["Base"]["Byte"]["Byte"][1515+j] = targ_id_as_bytes[j]
        targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterSaveParameterMap"]["Map"]["value"].append(param_maps[i])
        palcount += 1
    print("Appended " + str(palcount) + " pals of data")

        
    print("Searching for target containers")
    container_ids_len = len(targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"])
    
    inv_info = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["inventoryInfo"]
    inv_main = inv_info["Struct"]["value"]["Struct"]["CommonContainerId"]
    inv_key = inv_info["Struct"]["value"]["Struct"]["EssentialContainerId"]
    inv_weps = inv_info["Struct"]["value"]["Struct"]["WeaponLoadOutContainerId"]
    inv_armor = inv_info["Struct"]["value"]["Struct"]["PlayerEquipArmorContainerId"]
    inv_foodbag = inv_info["Struct"]["value"]["Struct"]["FoodEquipContainerId"]
    inv_pals = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["PalStorageContainerId"]
    inv_otomo = targ_json["root"]["properties"]["SaveData"]["Struct"]["value"]["Struct"]["OtomoCharacterContainerId"]
    
    count = 0
    for i in range(container_ids_len):
        container = targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]
        container_id = container["key"]["Struct"]["Struct"]["ID"]["Struct"]["value"]["Guid"]
        if container_id == inv_pals["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found pal inventory in target")
            print("Doing it the hard way...")
            pal_length = len(targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"])
            for j in range(pal_length):
                targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"][j]["Struct"]["RawData"] = host_pals["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"][j]["Struct"]["RawData"]
            
            #targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"] = host_pals["value"]
            count = count + 1
        elif container_id == inv_otomo["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found otomo inventory in target")
            #targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"] = host_otomo["value"]
            print("Doing it the hard way...")
            pal_length = len(targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"])
            for j in range(pal_length):
                targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["CharacterContainerSaveData"]["Map"]["value"][i]["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"][j]["Struct"]["RawData"] = host_otomo["value"]["Struct"]["Struct"]["Slots"]["Array"]["value"]["Struct"]["value"][j]["Struct"]["RawData"]
                print("Writing otomo slot no. " + str(j))
            count = count + 1
        if count >= 2:
            print("Found all pal containers")
            break
            
    container_ids_len = len(targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"])
    
    for i in range(container_ids_len):
        container = targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]
        container_id = container["key"]["Struct"]["Struct"]["ID"]["Struct"]["value"]["Guid"]
        if container_id == inv_main["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found main inventory in target")
            targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]["value"] = host_main["value"]
            count = count + 1
        elif container_id == inv_key["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found key inventory in target")
            targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]["value"] = host_key["value"]
            count = count + 1
        elif container_id == inv_weps["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found weapon inventory in target")
            targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]["value"] = host_weps["value"]
            count = count + 1
        elif container_id == inv_armor["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found armor inventory in target")
            targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]["value"] = host_armor["value"]
            count = count + 1
        elif container_id == inv_foodbag["Struct"]["value"]["Struct"]["ID"]["Struct"]["value"]["Guid"]:
            print("Found food bag inventory in target")
            targ_lvl["root"]["properties"]["worldSaveData"]["Struct"]["value"]["Struct"]["ItemContainerSaveData"]["Map"]["value"][i]["value"] = host_foodbag["value"]
            count = count + 1
        if count >= expected_containers:
            print("Found all target containers")
            break
            
            
            
    
    with open(t_host_json_path, 'w') as f:
        json.dump(targ_json, f, indent=2)
    with open(t_level_json_path, 'w') as f:
        json.dump(targ_lvl, f, indent=2)
        
    json_to_sav(uesave_path, t_level_json_path)
    json_to_sav(uesave_path, t_host_json_path)
    
    print("Saved all data successfully. PLEASE DON'T BREAK")
    
    # Clean up miscellaneous GVAS and JSON files which are no longer needed.
    clean_up_files(level_sav_path)
    clean_up_files(host_sav_path)
    clean_up_files(t_level_sav_path)
    clean_up_files(t_host_sav_path)
    #print('Miscellaneous files removed')
    

def sav_to_json(uesave_path, file):
    with open(file, 'rb') as f:
        # Read the file
        data = f.read()
        uncompressed_len = int.from_bytes(data[0:4], byteorder='little')
        compressed_len = int.from_bytes(data[4:8], byteorder='little')
        magic_bytes = data[8:11]
        save_type = data[11]
        # Check for magic bytes
        if magic_bytes != b'PlZ':
            print(f'File {file} is not a save file, found {magic_bytes} instead of P1Z')
            return
        # Valid save types
        if save_type not in [0x30, 0x31, 0x32]:
            print(f'File {file} has an unknown save type: {save_type}')
            return
        # We only have 0x31 (single zlib) and 0x32 (double zlib) saves
        if save_type not in [0x31, 0x32]:
            print(f'File {file} uses an unhandled compression type: {save_type}')
            return
        if save_type == 0x31:
            # Check if the compressed length is correct
            if compressed_len != len(data) - 12:
                print(f'File {file} has an incorrect compressed length: {compressed_len}')
                return
        # Decompress file
        uncompressed_data = zlib.decompress(data[12:])
        if save_type == 0x32:
            # Check if the compressed length is correct
            if compressed_len != len(uncompressed_data):
                print(f'File {file} has an incorrect compressed length: {compressed_len}')
                return
            # Decompress file
            uncompressed_data = zlib.decompress(uncompressed_data)
        # Check if the uncompressed length is correct
        if uncompressed_len != len(uncompressed_data):
            print(f'File {file} has an incorrect uncompressed length: {uncompressed_len}')
            return
        # Save the uncompressed file
        with open(file + '.gvas', 'wb') as f:
            f.write(uncompressed_data)
        print(f'File {file} uncompressed successfully')
        # Convert to json with uesave
        # Run uesave.exe with the uncompressed file piped as stdin
        # Standard out will be the json string
        uesave_run = subprocess.run(uesave_to_json_params(uesave_path, file+'.json'), input=uncompressed_data, capture_output=True)
        # Check if the command was successful
        if uesave_run.returncode != 0:
            print(f'uesave.exe failed to convert {file} (return {uesave_run.returncode})')
            print(uesave_run.stdout.decode('utf-8'))
            print(uesave_run.stderr.decode('utf-8'))
            return
        print(f'File {file} (type: {save_type}) converted to JSON successfully')

def json_to_sav(uesave_path, file):
    # Convert the file back to binary
    gvas_file = file.replace('.sav.json', '.sav.gvas')
    sav_file = file.replace('.sav.json', '.sav')
    uesave_run = subprocess.run(uesave_from_json_params(uesave_path, file, gvas_file))
    if uesave_run.returncode != 0:
        print(f'uesave.exe failed to convert {file} (return {uesave_run.returncode})')
        return
    # Open the old sav file to get type
    with open(sav_file, 'rb') as f:
        data = f.read()
        save_type = data[11]
    # Open the binary file
    with open(gvas_file, 'rb') as f:
        # Read the file
        data = f.read()
        uncompressed_len = len(data)
        compressed_data = zlib.compress(data)
        compressed_len = len(compressed_data)
        if save_type == 0x32:
            compressed_data = zlib.compress(compressed_data)
        with open(sav_file, 'wb') as f:
            f.write(uncompressed_len.to_bytes(4, byteorder='little'))
            f.write(compressed_len.to_bytes(4, byteorder='little'))
            f.write(b'PlZ')
            f.write(bytes([save_type]))
            f.write(bytes(compressed_data))
    print(f'Converted {file} to {sav_file}')

def clean_up_files(file):
    os.remove(file + '.json')
    os.remove(file + '.gvas')

def uesave_to_json_params(uesave_path, out_path):
    args = [
        uesave_path,
        'to-json',
        '--output', out_path,
    ]
    for map_type in UESAVE_TYPE_MAPS:
        args.append('--type')
        args.append(f'{map_type}')
    return args

def uesave_from_json_params(uesave_path, input_file, output_file):
    args = [
        uesave_path,
        'from-json',
        '--input', input_file,
        '--output', output_file,
    ]
    return args

if __name__ == "__main__":
    main()