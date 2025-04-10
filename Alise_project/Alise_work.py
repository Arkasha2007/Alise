from flask import Flask, request, jsonify
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'Москва': ['1652229/e56bf0a048375942a63d', '997614/6189229a4de486bde754'],
    'Нью-Йорк': ['997614/d3c4a603b4a2f3a5690c', '1652229/8646e12621403e80ba7f'],
    'Париж': ["1030494/89f4f32b8ee68b32ae9e", '1656841/1137b685cfea5b6c7b77']
}

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'РџСЂРёРІРµС‚! РќР°Р·РѕРІРё СЃРІРѕС‘ РёРјСЏ!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False

        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'РќРµ СЂР°СЃСЃР»С‹С€Р°Р»Р° РёРјСЏ. РџРѕРІС‚РѕСЂРё, РїРѕР¶Р°Р»СѓР№СЃС‚Р°!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response'][
                'text'] = f'РџСЂРёСЏС‚РЅРѕ РїРѕР·РЅР°РєРѕРјРёС‚СЊСЃСЏ, {first_name.title()}. РЇ РђР»РёСЃР°. РћС‚РіР°РґР°РµС€СЊ РіРѕСЂРѕРґ РїРѕ С„РѕС‚Рѕ?'
            res['response']['buttons'] = [
                {
                    'title': 'Р”Р°',
                    'hide': True
                },
                {
                    'title': 'РќРµС‚',
                    'hide': True
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'РґР°' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = 'РўС‹ РѕС‚РіР°РґР°Р» РІСЃРµ РіРѕСЂРѕРґР°!'
                    res['end_session'] = True
                else:
                    # РµСЃР»Рё РµСЃС‚СЊ РЅРµРѕС‚РіР°РґР°РЅРЅС‹Рµ РіРѕСЂРѕРґР°, С‚Рѕ РїСЂРѕРґРѕР»Р¶Р°РµРј РёРіСЂСѓ
                    sessionStorage[user_id]['game_started'] = True
                    # РЅРѕРјРµСЂ РїРѕРїС‹С‚РєРё, С‡С‚РѕР±С‹ РїРѕРєР°Р·С‹РІР°С‚СЊ С„РѕС‚Рѕ РїРѕ РїРѕСЂСЏРґРєСѓ
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'РЅРµС‚' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'РќСѓ Рё Р»Р°РґРЅРѕ!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'РќРµ РїРѕРЅСЏР»Р° РѕС‚РІРµС‚Р°! РўР°Рє РґР° РёР»Рё РЅРµС‚?'
                res['response']['buttons'] = [
                    {
                        'title': 'Р”Р°',
                        'hide': True
                    },
                    {
                        'title': 'РќРµС‚',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Р§С‚Рѕ СЌС‚Рѕ Р·Р° РіРѕСЂРѕРґ?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'РўРѕРіРґР° СЃС‹РіСЂР°РµРј!'
    else:
        # СЃСЋРґР° РїРѕРїР°РґР°РµРј, РµСЃР»Рё РїРѕРїС‹С‚РєР° РѕС‚РіР°РґР°С‚СЊ РЅРµ РїРµСЂРІР°СЏ
        city = sessionStorage[user_id]['city']
        # РїСЂРѕРІРµСЂСЏРµРј РµСЃС‚СЊ Р»Рё РїСЂР°РІРёР»СЊРЅС‹Р№ РѕС‚РІРµС‚ РІ СЃРѕРѕР±С‰РµРЅРёРµ
        if get_city(req) == city:
            res['response']['text'] = 'РџСЂР°РІРёР»СЊРЅРѕ! РЎС‹РіСЂР°РµРј РµС‰С‘?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            return
        else:
            # РµСЃР»Рё РЅРµС‚
            if attempt == 3:
                res['response']['text'] = f'Р’С‹ РїС‹С‚Р°Р»РёСЃСЊ. РС‚Рѕ {city.title()}. РЎС‹РіСЂР°РµРј РµС‰С‘?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                # РёРЅР°С‡Рµ РїРѕРєР°Р·С‹РІР°РµРј СЃР»РµРґСѓСЋС‰СѓСЋ РєР°СЂС‚РёРЅРєСѓ
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card'][
                    'title'] = 'РќРµРїСЂР°РІРёР»СЊРЅРѕ. Р’РѕС‚ С‚РµР±Рµ РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅРѕРµ С„РѕС‚Рѕ'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'Рђ РІРѕС‚ Рё РЅРµ СѓРіР°РґР°Р»!'
    # СѓРІРµР»РёС‡РёРІР°РµРј РЅРѕРјРµСЂ РїРѕРїС‹С‚РєРё РґРѕР»СЏ СЃР»РµРґСѓСЋС‰РµРіРѕ С€Р°РіР°
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    # РїРµСЂРµР±РёСЂР°РµРј РёРјРµРЅРѕРІР°РЅРЅС‹Рµ СЃСѓС‰РЅРѕСЃС‚Рё
    for entity in req['request']['nlu']['entities']:
        # РµСЃР»Рё С‚РёРї YANDEX.GEO, С‚Рѕ РїС‹С‚Р°РµРјСЃСЏ РїРѕР»СѓС‡РёС‚СЊ РіРѕСЂРѕРґ(city), РµСЃР»Рё РЅРµС‚, С‚Рѕ РІРѕР·РІСЂР°С‰Р°РµРј None
        if entity['type'] == 'YANDEX.GEO':
            # РІРѕР·РІСЂР°С‰Р°РµРј None, РµСЃР»Рё РЅРµ РЅР°С€Р»Рё СЃСѓС‰РЅРѕСЃС‚Рё СЃ С‚РёРїРѕРј YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # РїРµСЂРµР±РёСЂР°РµРј СЃСѓС‰РЅРѕСЃС‚Рё
    for entity in req['request']['nlu']['entities']:
        # РЅР°С…РѕРґРёРј СЃСѓС‰РЅРѕСЃС‚СЊ СЃ С‚РёРїРѕРј 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
