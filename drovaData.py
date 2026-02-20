from datetime import datetime, timedelta
import json
import os
import winreg
import requests
import sys

manualIds=[
    {
        "productId":"b6346f52-f780-42a9-98a2-1c7d6c4b4473",
        "title":"PlanetSide 2",
        "steamId":"218230"
    },
    {
        "productId":"7d628e11-0bb1-442c-98a4-8106176b13b8",
        "title":"The Walking Dead: Season Two",
        "steamId":"261030"
    }
]


cacheMinutes = 10
fullListCacheMinutes=60*2

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


def addGameToStation(productId):
    global dvAuthToken,dvServerID,dvUserID
    
    url=f"https://services.drova.io/server-manager/serverproduct/add/{dvServerID}/{productId}"

    try:
        response=requests.post(
                url,
                params={"user_id": dvUserID},
                headers={"X-Auth-Token": dvAuthToken},timeout=2
        )
        return response
    except Exception as e: 
        print(f"drova game add {e}")
        pass

def getDrovaData(url):
    try:
        response = requests.get(
            url,
            params={"user_id": dvUserID},
            headers={"X-Auth-Token": dvAuthToken},timeout=2
        )
        if response.status_code == 200:
            servers=response.json()
            return servers
        else:
            print (f"{url} error: "+str(response.status_code))
    except Exception as e: 
        print(f"drova get err {e}")
        pass


def tryLoadGetData(filename,url,cacheTime=cacheMinutes,setIds=False):
    data=loadData(filename,cacheTime)
    if data==None:
        print(f"no cache {filename}")

        data=getDrovaData(url)

        if data!=None:
            if setIds:
                data=fullListSetSteamIds(data)
            storeData(filename,data)
        else:
            print("\033[32mNo drova data, load cache\033[0m")
            data=loadData(filename)
    return data


def isDrovaTokenCorrect(token:str)->bool:
    """ Проверяет, токен на ключевые слова и его длину. 
    Возвращает True, если токен похож на правильный.
    """
    if token:
        if "TEST" in token:
            return False
        if "NONE" in token:
            return False
        if len(token)>=32:
            return True
    return False

def initTokens():
    global dvAuthToken,dvServerID,dvUserID

    #print(sys.argv)
    if len(sys.argv) > 1:
        dvAuthToken = sys.argv[1]
        if not isDrovaTokenCorrect(dvAuthToken):
            print("Добавьте правильный токен в аргументе командной строки")
            return None
    else:
        print("Добавьте правильный токен в аргументе командной строки")
        return None


    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\\ITKey\\Esme")
        dvServerID = winreg.QueryValueEx(key, "last_server")[0]
    except:
        print ("registry srvId err")
        return None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,f"SOFTWARE\\ITKey\\Esme\\servers\\{dvServerID}")
        #dvAuthToken = winreg.QueryValueEx(key, "auth_token")[0]
        dvUserID = winreg.QueryValueEx(key, "user_id")[0]
    except:
        print ("registry token/user err")
        return None
    return True

def fullListSetSteamIds(games):
    for game in games:
        if game["requiredAccount"] == "Steam" and not game["inShopUrl"] is None and "steampowered.com/app/" in game["inShopUrl"]:
            steam_id = game["inShopUrl"].split("/app/")[1].split("/")[0]
            #print(f"Название: {game['title']}, Steam ID: {steam_id}")
            game["steamId"]=steam_id
        elif game["requiredAccount"] == "Steam":
                #print(f"Название: {game['title']} — ссылка не найдена")
                idFromManual=next((item["steamId"] for item in manualIds if item["productId"] == game["productId"]), None)
                #print(f"id из списка {idFromManual}")
                if idFromManual!=None:
                    game["steamId"]=idFromManual
    return games


def getDrovaFullGamesList():
    global dvAuthToken,dvServerID,dvUserID

    fullGamesList=tryLoadGetData("fullList.json", "https://services.drova.io/product-manager/product/listfull2",fullListCacheMinutes,setIds=True)
    return fullGamesList

def getStationDataFilename():
    global dvServerID
    return f"{dvServerID}.json"

def getDrovaStationGamesList():
    global dvAuthToken,dvServerID,dvUserID

    if initTokens() is None:
        print("ошибка id или токена")
        sys.exit(1)

    #fullGamesList=tryLoadGetData("products.json", "https://services.drova.io/product-manager/product/listfull2")
    stationGamesList=tryLoadGetData(getStationDataFilename(), f"https://services.drova.io/server-manager/serverproduct/list4edit2/{dvServerID}")
    return stationGamesList