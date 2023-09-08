from github_scraper import get_repo_pull_requests_filterd_data
from github_analyzer import analyze_pr_data
from json import dumps

repo_url = 'https://github.com/burnash/gspread'
days_back = 30
strs_to_check = ['test', 'adjustment', 'invoice', 'refund', 'external', 'eshta', 'spreadsheet', 'google', 'api']

pr_filtered_data = get_repo_pull_requests_filterd_data(repo_url, days_back)
pr_analysis_data = analyze_pr_data(pr_filtered_data, strs_to_check)

with open('test_data.json', 'w') as f:
    f.write(dumps(pr_filtered_data, indent=4, default=str))
    
with open('test_analysis.json', 'w') as f:
    f.write(dumps(pr_analysis_data, indent=4, default=str))