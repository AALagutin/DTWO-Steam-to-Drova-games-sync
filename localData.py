from datetime import datetime, timedelta
import json
import os
import winreg
import vdf
import win32api
import xml.etree.ElementTree as ET

localCacheMinutes = 5
localFilename="localGamesList.json"

#Компьютер\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\1461564088
# DisplayName InstallLocation D:\Games\World_of_Warships

#Компьютер\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\2135834465
# DisplayName InstallLocation D:\Games\World_of_Tanks_EU

#Компьютер\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\LGC-2105438830
# DisplayName InstallLocation D:\Games\Korabli

#Компьютер\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\LGC-754406319
# DisplayName InstallLocation D:\Games\Tanki


localList={
    "Electronic Arts Launcher":{"skip":True,"exePaths":[r"C:\Program Files\Electronic Arts\EA Desktop\EA Desktop\EALauncher.exe"],"size":0.5},    
    "Epic Game Launcher":{"skip":True,"exePaths":[r"C:\Program Files (x86)\Epic Games\Launcher\Engine\Binaries\Win64\EpicGamesLauncher.exe"],"size":1},
    "Battlestate Games Launcher":{"skip":True,"exePaths":[r"C:\Battlestate Games\BsgLauncher\BsgLauncher.exe"],"size":0.5},    
    "Rockstar Games Launcher":{"skip":True,"exePaths":[r"C:\Program Files\Rockstar Games\Launcher\Launcher.exe"],"size":0.5},    
    "HoYoPlay Launcher":{"skip":True,"exePaths":[r"C:\Program Files\HoYoPlay\launcher.exe"],"size":0.4},    
    
    "Lesta Gamecenter":{"skip":True,"exePaths":[r"C:\ProgramData\Lesta\GameCenter\lgc.exe"],"size":0.35},
    "Wargaming Gamecenter":{"skip":True,"exePaths":[r"C:\ProgramData\Wargaming.net\GameCenter\wgc.exe"],"size":0.35},    

    "Wuthering Waves Launcher":{"skip":True,"exePaths":[r"C:\Program Files\Wuthering Waves\launcher.exe"],"size":0.2},    


    "Fortnite":{"productId": "d5f88d94-87d5-11e7-bb31-000000003778","skip":False,"exePaths":[r"C:\Program Files\Epic Games\Fortnite\FortniteGame\Binaries\Win64\FortniteClient-Win64-Shipping.exe"],"size":62},
    "Honkai: Star Rail":{"productId": "5e3c271e-da2a-4898-a420-9b49d74f2695","skip":False,"exePaths":[r"C:\Program Files\HoYoPlay\games\Star Rail Games\StarRail.exe"],"size":37},
    "Genshin Impact":{"productId": "b05acb00-93ab-4b6d-ab6c-792f72e43665","skip":False,"exePaths":[r"C:\Program Files\HoYoPlay\games\Genshin Impact game\GenshinImpact.exe"],"size":76},
    "Zenless Zone Zero":{"productId": "0864eddb-d20d-437d-a322-329ccda51ad0","skip":False,"exePaths":[r"C:\Program Files\HoYoPlay\games\ZenlessZoneZero Game\ZenlessZoneZero.exe"],"size":60},
    
    "Wuthering Waves":{"productId": "934386db-5b9e-4635-ab70-59d02b6a988d","skip":False,"exePaths":[r"C:\Program Files\Wuthering Waves\Wuthering Waves Game\Wuthering Waves.exe"],"size":20},
    "Escape from Tarkov":{"productId": "cdb6d8f4-6b6f-4f92-a240-56447ed9b42d","skip":False,"exePaths":[r"c:\Battlestate Games\EFT\EscapeFromTarkov.exe",r"c:\Battlestate Games\Escape from Tarkov\EscapeFromTarkov.exe"],"size":42},
    "Escape from Tarkov Arena":{"productId": "1b4253f2-11ae-4d14-92aa-b506a18cf247","skip":False,"exePaths":[r"c:\Battlestate Games\Escape from Tarkov Arena\EscapeFromTarkovArena.exe"],"size":30},

    "Мир кораблей":{"productId": "21d8c648-8d39-4b3f-8989-69d58fbe7dff","skip":False,"exePaths":[r"c:\Games\Korabli\lgc_api.exe",r"d:\Games\Korabli\lgc_api.exe"],"size":67},
    "ships(EU)":{"productId": "21d8c648-8d39-4b3f-8989-69d58fbe7e00","skip":False,"exePaths":[r"C:\games\World_of_Warships\wgc_api.exe",r"d:\games\World_of_Warships\wgc_api.exe"],"size":66}
}

localWoTList={
    "Мир танков":{"productId": "d5f88d94-87d5-11e7-bb31-000000002432","skip":False,"infoPaths":[r"C:\Games\Tanki\game_info.xml",r"D:\Games\Tanki\game_info.xml"],"size":73},
    "tanks(EU)":{"productId": "c1661a7c-4950-4346-a193-103fb385b6d6","skip":False,"infoPaths":[r"C:\Games\World_of_Tanks_EU\game_info.xml",r"D:\Games\World_of_Tanks_EU\game_info.xml"],"size":72},
}


def storeData(filename,data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e: 
        print(e)
        pass

def loadData(filename,cacheMinutes=0):
    try:
        if os.path.isfile(filename):
            if cacheMinutes>0:
                filetime= datetime.fromtimestamp(os.path.getmtime(filename))
                filedelta= datetime.now() - filetime
                if filedelta < timedelta(minutes=cacheMinutes):
                    with open(filename, 'r') as f:
                        return json.load(f)
            else:
                with open(filename, 'r') as f:
                    return json.load(f)
    except Exception as e: 
        print(e)
        pass

def checkLocalGame(steamGames):
    for gameName in localList:
        for exePath in localList[gameName]["exePaths"]:
            if os.path.exists(exePath):
                gameInfo={"SizeOnDisk":localList[gameName]["size"]
                          ,"SkipInGames":localList[gameName]["skip"]
                          ,"productId":localList[gameName].get("productId",None)}
                gameInfo["fileVersion"]="0"
                try:
                    fileInfo = win32api.GetFileVersionInfo(exePath, '\\')
                    ms = fileInfo['FileVersionMS']
                    ls = fileInfo['FileVersionLS']
                    gameInfo["fileVersion"]=f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                except:
                    #print(exePath)
                    pass
                steamGames[gameName]=gameInfo

def checkWoTGame(steamGames):
    for gameName in localWoTList:
        for infoPath in localWoTList[gameName]["infoPaths"]:
            if os.path.exists(infoPath):
                gameInfo={"SizeOnDisk":localWoTList[gameName]["size"]
                          ,"SkipInGames":localWoTList[gameName]["skip"]
                          ,"productId":localWoTList[gameName].get("productId",None)}
                gameInfo["fileVersion"]="0"
                try:
                    tree = ET.parse(infoPath)
                    root = tree.getroot()
                    gameInfo["fileVersion"]= root.find('.//version_name').text                
                except:
                    #print(exePath)
                    pass
                steamGames[gameName]=gameInfo

def getLocalGamesList():
    data=loadData(localFilename,localCacheMinutes)
    if data!=None:
        return data

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\WOW6432Node\\Valve\\Steam")
        steamFolder = winreg.QueryValueEx(key, "InstallPath")[0]
    except:
        steamFolder=None

    steamGames={}

    checkLocalGame(steamGames)
    checkWoTGame(steamGames)
   


    if steamFolder is not None and os.path.isdir(steamFolder):
        steamFolders=[]
        
        with open(os.path.join(steamFolder,"steamapps","libraryfolders.vdf"), 'r') as f:
            steamLibraries=vdf.load(f)
            for key in steamLibraries['libraryfolders'].keys():
                library=os.path.join(steamLibraries['libraryfolders'][key]['path'],"steamapps")
                steamFolders.append(library)
            for folder in steamFolders:
                if os.path.isdir(folder):
                    for filename in os.listdir(folder):
                        if filename.endswith('.acf'):

                            filepath = os.path.join(folder, filename)

                            with open(filepath, 'r') as f:
                                acf_data = vdf.load(f)

                                app_id = acf_data['AppState']['appid']
                                name = acf_data['AppState']['name']
                                #print(name)
                                AutoUpdateBehavior = int(acf_data['AppState']['AutoUpdateBehavior'])
                                SizeOnDisk =round( float(acf_data['AppState']['SizeOnDisk'])/1073741824,1)

                                #buildid=int(acf_data['AppState']['buildid'])
                                #TargetBuildID=0
                                #if "TargetBuildID" in acf_data['AppState']:
                                #    TargetBuildID=int(acf_data['AppState']['TargetBuildID'])
                                #if "LastUpdated" in acf_data['AppState']:
                                #    lastupdated=int(acf_data['AppState']['LastUpdated'])
                                #else:
                                #    lastupdated=int(acf_data['AppState']['lastupdated'])
                                

                                if name=="Steamworks Common Redistributables": # hardcoded values
                                    continue

                                steamGames[name]={"appid":app_id,"AutoUpdateBehavior":AutoUpdateBehavior,"SizeOnDisk":SizeOnDisk}  #,"LastUpdated":lastupdated,"buildid":buildid,"TargetBuildID":TargetBuildID

                                #steamGames.append({name:{"AutoUpdateBehavior":AutoUpdateBehavior}})
                                #installdir = '"' +                                     os.path.join(folder, 'common',                                                acf_data['AppState']['installdir'])+'"'
        
            #print(len( steamGames))
            if len( steamGames)>0:
                storeData(localFilename,steamGames)
                return steamGames
    return None