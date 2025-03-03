from datetime import datetime, timedelta, timezone

import streamlit as st
import pandas as pd

from data import get_job_openings, get_referrals, get_candidates


def dashboard():
    today = datetime.now(timezone.utc)
    job_openings = get_job_openings()

    job_openings_df = pd.DataFrame(job_openings)

    job_openings_df['Client_Name'] = job_openings_df['Client_Name'].apply(
        lambda x: x['name'] if isinstance(x, dict) and 'name' in x else x
    )
    job_openings_df['Account_Manager'] = job_openings_df['Account_Manager'].apply(
        lambda x: x['name'] if isinstance(x, dict) and 'name' in x else x
    )
    job_openings_df['Created_Time'] = pd.to_datetime(job_openings_df['Created_Time']).dt.tz_localize(None)
    job_openings_df['Last_Activity_Time'] = pd.to_datetime(job_openings_df['Last_Activity_Time']).dt.tz_localize(None)
    
    open_jobs_df = job_openings_df[job_openings_df['Job_Opening_Status'] == 'In-progress']

    start_of_week = pd.to_datetime('today').normalize() - pd.DateOffset(days=pd.to_datetime('today').normalize().weekday())

    total_open_jobs = len(open_jobs_df)

    total_filled_jobs = len(
        job_openings_df[
            (job_openings_df['Job_Opening_Status'] == 'Filled') &
            (job_openings_df['Last_Activity_Time'] >= start_of_week)
        ]
    )
    total_cancelled_jobs = len(
        job_openings_df[
            (job_openings_df['Job_Opening_Status'] == 'Cancelled') &
            (job_openings_df['Last_Activity_Time'] >= start_of_week)
        ]
    )
    total_filled_elswhere_jobs = len(
        job_openings_df[
            (job_openings_df['Job_Opening_Status'] == 'Closed - Client Filled Elsewhere') &
            (job_openings_df['Last_Activity_Time'] >= start_of_week)
        ]
    )
    st.subheader("Weekly Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("# Open Jobs", total_open_jobs)
    col2.metric("# Filled Jobs", total_filled_jobs)
    col3.metric("# Cancelled Jobs", total_cancelled_jobs)
    col4.metric("# Jobs Filled Elsewhere", total_filled_elswhere_jobs)

    # TODO: only get referrals for open jobs, using the search API; Construct the search criteria here
    open_job_ids = open_jobs_df['id'].tolist()
    search_criteria = f"(JobID:in:{','.join(open_job_ids)})"
    referrals_df = pd.DataFrame(get_referrals(search_criteria))

    unique_referrals_df = referrals_df.drop_duplicates(subset=['Email'])

    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    start_of_last_month = last_day_of_last_month.replace(day=1)
    search_criteria = f"(Created_Time:between:{start_of_last_month.strftime('%Y-%m-%d')}T00:00:00Z,{today.strftime('%Y-%m-%d')}T23:59:59Z)"

    candidates_df = pd.DataFrame(get_candidates(search_criteria))
    candidates_df['Created_Time'] = pd.to_datetime(candidates_df['Created_Time']).dt.tz_localize(None)

    total_referrals = len(referrals_df)
    referrals_df['Created_Time'] = pd.to_datetime(referrals_df['Created_Time']).dt.tz_localize(None)
    start_of_week = pd.to_datetime('today').normalize() - pd.DateOffset(days=pd.to_datetime('today').normalize().weekday())
    total_referrals_created_this_week = len(
        referrals_df[referrals_df['Created_Time'] >= start_of_week]
    )
    average_referrals_per_job = round(total_referrals/len(open_jobs_df), 2)
    
    ref1, ref2, ref3 = st.columns(3)
    ref1.metric("# Total Referrals", total_referrals)
    ref2.metric("# Referrals Submitted This Week", total_referrals_created_this_week)
    ref3.metric("Average Referrals per Job", average_referrals_per_job)

    # unique_associated_candidates = set()
    # for job_id in open_job_ids:
    #     associated_candidates = get_associated_candidates(job_id)
    #     for candidate in associated_candidates:
    #         unique_associated_candidates.add(candidate['id'])
    ref4, ref5 = st.columns(2)

    presented_search_criteria = f"(Candidate_Status:equals:Submitted-to-client)" #AND (Last_Activity_Time:greater_equal:{start_of_week.strftime('%Y-%m-%d')}T00:00:00Z)

    presented_candidates = get_candidates(presented_search_criteria)
    ref4.metric("# Total Candidates Presented", len(presented_candidates))

    presented_candidates_df = pd.DataFrame(presented_candidates)
    presented_candidates_df['Email'] = presented_candidates_df['Email'].str.lower()
    referrals_df['Email'] = referrals_df['Email'].str.lower()

    matched_presented_candidates = presented_candidates_df[
        presented_candidates_df['Email'].isin(referrals_df['Email'])
    ]
    matched_presented_candidates_as_percentage_of_all_presented = round(
        (len(matched_presented_candidates) / len(presented_candidates)) * 100, 2
    )
    ref5.metric("% Of Presented Candidates From Referrals", matched_presented_candidates_as_percentage_of_all_presented)
    
    st.subheader("Monthly Metrics")
    start_of_this_month = pd.to_datetime('today').replace(day=1)

    start_of_last_month = start_of_this_month - pd.DateOffset(months=1)
    candidates_created_this_month = len(candidates_df[candidates_df['Created_Time'] >= start_of_this_month])
    candidates_created_last_month = len(candidates_df[(candidates_df['Created_Time'] >= start_of_last_month) & (candidates_df['Created_Time'] < start_of_this_month)])
    percentage_change = round(((candidates_created_this_month - candidates_created_last_month) / candidates_created_last_month) * 100, 2)
    percentage_change = 0 if percentage_change < 0 else percentage_change
    new_job_openings_this_month = len(job_openings_df[job_openings_df['Created_Time'] >= start_of_this_month])
    total_filled_jobs_this_month = len(job_openings_df[(job_openings_df['Job_Opening_Status'] == 'Filled') & (job_openings_df['Last_Activity_Time'] >=  start_of_this_month)])
    total_cancelled_jobs_this_month = len(job_openings_df[(job_openings_df['Job_Opening_Status'] == 'Cancelled') & (job_openings_df['Last_Activity_Time'] >= start_of_this_month)])
    total_filled_elswhere_jobs_this_month = len(job_openings_df[(job_openings_df['Job_Opening_Status'] == 'Closed - Client Filled Elsewhere') & (job_openings_df['Last_Activity_Time'] >= start_of_this_month)])

    mon1, mon2, mon3 = st.columns(3)
    mon1.metric("# New members added to network", candidates_created_this_month)
    mon2.metric("% Increase in network size", percentage_change)
    mon3.metric("# New Job Openings", new_job_openings_this_month)

    mon4, mon5, mon6 = st.columns(3)
    mon4.metric("# Filled Jos", total_filled_jobs_this_month)
    mon5.metric("# Cancelled Jobs", total_cancelled_jobs_this_month)
    mon6.metric("# Jobs Filled Elsewhere", total_filled_elswhere_jobs_this_month)

    open_jobs_df['Days_Open'] = (pd.to_datetime('today') - pd.to_datetime(open_jobs_df['Date_Opened'])).dt.days
    open_jobs_df = open_jobs_df[['id', 'Posting_Title', 'Client_Name', 'Account_Manager', 'Date_Opened', 'Days_Open', 'Target_Date', 'Job_Type', 'Industry', 'Required_Skills', 'Salary', 'Location', 'Referral', 'Number_of_Positions', 'No_of_Candidates_Associated', 'No_of_Candidates_Hired', 'Stage', 'Job_Opening_Status', ]]
    def highlight_rows(row):
        return ['background-color: red' if row['Days_Open'] > 60 else '' for _ in row]

    referrals_per_job = referrals_df.groupby('JobID').size().reset_index(name='Referral_Count')
    referrals_per_job = referrals_per_job.rename(columns={'JobID': 'id'})
    referrals_per_job['Referral_Count'] = referrals_per_job['Referral_Count'].astype(int)
    open_jobs_df = open_jobs_df.merge(referrals_per_job, on='id', how='left').fillna({'Referral_Count': 0})
    open_jobs_df['Referral_Count'] = open_jobs_df['Referral_Count'].astype(int)
    open_jobs_df = open_jobs_df[['id', 'Posting_Title', 'Client_Name', 'Account_Manager', 'Date_Opened', 'Days_Open', 'Referral_Count', 'Target_Date', 'Job_Type', 'Industry', 'Required_Skills', 'Salary', 'Location', 'Referral', 'Number_of_Positions', 'No_of_Candidates_Associated', 'No_of_Candidates_Hired', 'Stage', 'Job_Opening_Status', ]]
    open_jobs_df.index = range(1, len(open_jobs_df) + 1)
    styled_df = open_jobs_df.style.apply(highlight_rows, axis=1)
    st.markdown("#### Open Jobs")
    st.write(styled_df)

    # referrals_per_job = referrals_df.groupby('JobID').size().reset_index(name='Referral_Count')
    # referrals_per_job = referrals_per_job.rename(columns={'JobID': 'ID'})
    # job_openings_with_referrals = _df.merge(referrals_per_job, left_on='id', right_on='ID', how='left').fillna({'Referral_Count': 0})
    # job_openings_with_referrals = job_openings_with_referrals[['Posting_Title', 'Client_Name', 'Account_Manager', 'Referral_Count']]
    # job_openings_with_referrals = job_openings_with_referrals.sort_values(by='Referral_Count', ascending=False)
    # st.markdown("#### Referrals per Job Opening")
    # st.dataframe(job_openings_with_referrals)


