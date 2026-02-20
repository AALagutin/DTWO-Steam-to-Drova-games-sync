import drovaData
import localData
import pathlib


print("DT 2025")

localGames=localData.getLocalGamesList()
drovaGames=drovaData.getDrovaStationGamesList()
drovaFullGamesList=drovaData.getDrovaFullGamesList()

#print(drovaFullGamesList[:2]  )
#print(dict(list(localGames.items())[:2])  )
#print(drovaGames[:2]  )

# Проходим по всем играм в localGames
for game_name, game_data in localGames.items():
    steam_id = game_data.get('appid')
    if steam_id:  # Если steam_id не None
        # Ищем соответствующий продукт в drovaFullGamesList
        for drova_game in drovaFullGamesList:
            if drova_game.get('productId')=="c9af5926-118e-4c5b-87d4-204099ceb6fb": continue # пропускаем дубль киберпанк без dlc
            if drova_game.get('steamId') == steam_id:
                # Добавляем productId в данные игры
                game_data['productId'] = drova_game.get('productId')
                break  # Прерываем цикл после нахождения совпадения
            else:
                game_data['productId'] =None

print("-------------------------------")
print (f"Кэш полного списка игр {drovaData.fullListCacheMinutes} минут")
print (f"Кэш списка личного кабинета {drovaData.cacheMinutes} минут")
print (f"Кэш локального списка {localData.localCacheMinutes} минут")
print("-------------------------------")
print (f"Всего в базе игр: {len(drovaFullGamesList)}")
print (f"В лк станции игр: {len(drovaGames)}")
print (f"Нашлось установленных: {sum(1 for v in localGames.values() if isinstance(v, dict) )}") #and 'productId' in v


product_ids_in_station_profile = {item['productId'] for item in drovaGames}
notSetInStation = {
    key: value 
    for key, value in localGames.items() 
    if value.get('productId') is not None 
    and value['productId'] not in product_ids_in_station_profile
}


changes=False
for key,value in notSetInStation.items():
    print(f"Добавляю в лк {key} / {value["productId"]}")
    print (drovaData.addGameToStation(value["productId"]))
    changes=True

if changes:
    pathlib.Path.unlink(drovaData.getStationDataFilename())

noDrovaId = {    key: value for key, value in localGames.items()     if value.get('productId') is None  }
#print(noDrovaId)
if noDrovaId:
    print("-------------------------------")
    print("Нет в базе дров:")
    for game in sorted(noDrovaId): #.keys()
        print(game)

local_ids = {v["productId"] for v in localGames.values() if "productId" in v}
missing_in_local = [game for game in drovaGames if "productId" in game and game["productId"] not in local_ids]
#print(missing_in_local)
if missing_in_local:
    print("-------------------------------")
    print("Не нашлось среди установленных:")
    for game in sorted(missing_in_local, key=lambda x: x["title"]):
        print(game['title'])