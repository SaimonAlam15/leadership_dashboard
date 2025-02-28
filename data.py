import os

from dotenv import load_dotenv

import streamlit as st

from zoho_api import ZohoAPIClient

load_dotenv()

client_id = os.getenv('ZOHO_CLIENT_ID')
client_secret = os.getenv('ZOHO_CLIENT_SECRET')
refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')

zoho_client = ZohoAPIClient(client_id, client_secret)

@st.cache_data(ttl=3600)
def get_access_token():
    return zoho_client.get_access_token(refresh_token)


def get_job_openings():
    # current_datetime = datetime.now(timezone.utc)
    # six_months_ago = current_datetime - timedelta(days=6*30)
    access_token = get_access_token()
    if not zoho_client.is_token_valid(access_token):
        access_token = get_access_token()
    # date_range_string = f"{six_months_ago.strftime('%Y-%m-%d')}T00:00:00Z,{current_datetime.strftime('%Y-%m-%d')}T23:59:59Z"
    # date_range_string_encoded = urllib.parse.quote(date_range_string)
    # search_criteria = f"(Created_Time:between:{date_range_string_encoded})"
    all_records = []
    page = 1
    while True:
        url = f'https://recruit.zoho.com/recruit/v2/Job_Openings?page={page}&per_page=200'
        response = zoho_client.get(access_token, url)
        if response.status_code != 200:
            break
        records = response.json().get('data', [])
        if not records:
            break
        all_records.extend(records)
        page += 1
    return all_records


def get_referrals(search_criteria):
    # current_datetime = datetime.now(timezone.utc)
    # six_months_ago = current_datetime - timedelta(days=6*30)
    access_token = get_access_token()
    if not zoho_client.is_token_valid(access_token):
        access_token = get_access_token()
    # date_range_string = f"{six_months_ago.strftime('%Y-%m-%d')}T00:00:00Z,{current_datetime.strftime('%Y-%m-%d')}T23:59:59Z"
    # date_range_string_encoded = urllib.parse.quote(date_range_string)
    # search_criteria = f"(Created_Time:between:{date_range_string_encoded})"
    all_records = []
    page = 1
    while True:
        url = f'https://recruit.zoho.com/recruit/v2/IReferrals/search?criteria={search_criteria}&page={page}&per_page=200'
        response = zoho_client.get(access_token, url)
        if response.status_code != 200:
            break
        records = response.json().get('data', [])
        if not records:
            break
        all_records.extend(records)
        page += 1
    return all_records


def get_candidates(search_criteria):
    access_token = get_access_token()
    if not zoho_client.is_token_valid(access_token):
        access_token = get_access_token()
    # date_range_string = f"{six_months_ago.strftime('%Y-%m-%d')}T00:00:00Z,{current_datetime.strftime('%Y-%m-%d')}T23:59:59Z"
    # date_range_string_encoded = urllib.parse.quote(date_range_string)
    # search_criteria = f"(Created_Time:between:{date_range_string_encoded})"
    all_records = []
    page = 1
    while True:
        url = f'https://recruit.zoho.com/recruit/v2/Candidates/search?criteria={search_criteria}&page={page}&per_page=200'
        response = zoho_client.get(access_token, url)
        if response.status_code != 200:
            break
        records = response.json().get('data', [])
        if not records:
            break
        all_records.extend(records)
        page += 1
    return all_records


def get_associated_candidates(job_id):
    access_token = get_access_token()
    if not zoho_client.is_token_valid(access_token):
        access_token = get_access_token()
    all_records = []
    page = 1
    while True:
        url = f'https://recruit.zoho.com/recruit/v2/Job_Openings/{job_id}/Candidates?page={page}&per_page=200'
        response = zoho_client.get(access_token, url)
        if response.status_code != 200:
            break
        records = response.json().get('data', [])
        if not records:
            break
        all_records.extend(records)
        page += 1
    return all_records
