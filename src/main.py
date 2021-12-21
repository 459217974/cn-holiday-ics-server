#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# Created by CaoDa on 2021/12/21 09:48
import datetime
import os
import base64
from io import BytesIO
from cachetools import TTLCache, cached
from flask import Flask, render_template, request, send_file
from fetch_holidays import fetch_holiday
from generate_ics import generate_ics
from google_auth import GoogleAuth

BASE_DIR = os.path.dirname(__file__)
app = Flask('CNHolidayICSServer', template_folder=os.path.join(BASE_DIR, '../templates'))
SECRET_FILE_PATH = os.path.join(BASE_DIR, '../data/google_auth_secret.txt')
app.GOOGLE_AUTH_SECRET = ''
if os.path.exists(SECRET_FILE_PATH):
    with open(SECRET_FILE_PATH, 'r', encoding='utf8') as secret_file:
        app.GOOGLE_AUTH_SECRET = secret_file.read()

HOLIDAY_ICS = os.path.join(BASE_DIR, '../data/holiday.ics')
WORKDAY_ICS = os.path.join(BASE_DIR, '../data/workday.ics')
HOLIDAY_AND_WORKDAY_ICS = os.path.join(BASE_DIR, '../data/holiday_and_workday.ics')


@app.route('/holiday')
def get_holiday_ics():
    refresh_ics_with_ttl_cache()
    return send_file(HOLIDAY_ICS)


@app.route('/workday')
def get_workday_ics():
    refresh_ics_with_ttl_cache()
    return send_file(WORKDAY_ICS)


@app.route('/holiday_and_workday')
def get_holiday_and_workday_ics():
    refresh_ics_with_ttl_cache()
    return send_file(HOLIDAY_AND_WORKDAY_ICS)


@app.route('/force_refresh', methods=['GET'])
def force_fresh():
    gcode = request.args.get('gcode', '')
    if GoogleAuth.verify(app.GOOGLE_AUTH_SECRET, gcode):
        refresh_ics()
        return {'code': 200, 'message': 'ok'}
    else:
        return {'code': 401, 'message': 'Invalid gcode'}


@app.route('/google_auth_qrcode')
def get_google_auth_qrcode():
    qrcode_base64 = ''
    if not os.path.exists(SECRET_FILE_PATH):
        app.GOOGLE_AUTH_SECRET = GoogleAuth.new_secret()
        with open(SECRET_FILE_PATH, 'w', encoding='utf8') as f:
            f.write(app.GOOGLE_AUTH_SECRET)
        qrcode = BytesIO()
        GoogleAuth.get_qrcode(app.GOOGLE_AUTH_SECRET, app.name).save(qrcode)
        qrcode.seek(0)
        qrcode_base64 = base64.b64encode(qrcode.read()).decode('utf8')
    return render_template('google_auth_qrcode.html', **{'qrcode': qrcode_base64})


def refresh_ics():
    now = datetime.datetime.now()
    last_year = now.year - 1
    next_year = now.year + 1
    current_year_holiday_and_workday = fetch_holiday(now.year)
    last_year_holiday_and_workday = fetch_holiday(last_year)
    next_year_holiday_and_workday = fetch_holiday(next_year)
    holiday = list(filter(
        lambda x: x['isOffDay'],
        last_year_holiday_and_workday['days'] +
        current_year_holiday_and_workday['days'] +
        next_year_holiday_and_workday['days']
    ))
    workday = list(filter(
        lambda x: not x['isOffDay'],
        last_year_holiday_and_workday['days'] +
        current_year_holiday_and_workday['days'] +
        next_year_holiday_and_workday['days']
    ))
    holiday_and_workday = (
            last_year_holiday_and_workday['days'] +
            current_year_holiday_and_workday['days'] +
            next_year_holiday_and_workday['days']
    )
    generate_ics(holiday, HOLIDAY_ICS)
    generate_ics(workday, WORKDAY_ICS)
    generate_ics(holiday_and_workday, HOLIDAY_AND_WORKDAY_ICS)


@cached(TTLCache(maxsize=1, ttl=datetime.timedelta(hours=1).seconds))
def refresh_ics_with_ttl_cache():
    refresh_ics()


if __name__ == '__main__':
    app.run(
        host='127.0.0.1', port=8080, debug=True
    )
    import urllib.request
    urllib.request.urlopen()
