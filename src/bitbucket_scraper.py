from base64 import b64encode
from requests import get
from collections import namedtuple
from urllib.parse import urlparse
from os import environ
from datetime import datetime, timedelta


def _encode_username_and_password(user_name, password):
    """
    Encodes the username and password to base64
    """
    username_and_password = f"{user_name}:{password}"
    username_and_password_bytes = username_and_password.encode("ascii")
    base64_bytes = b64encode(username_and_password_bytes)
    base64_auth = base64_bytes.decode("ascii")
    return base64_auth


def export_bitbucket_username_and_app_password_to_env_var(
    user_name: str, password: str
):
    base64_auth = _encode_username_and_password(user_name, password)
    url = "https://api.bitbucket.org/2.0/user"
    headers = {
        "Authorization": f"Basic {base64_auth}",
    }
    response = get(url=url, headers=headers)
    if response.status_code == 200:
        environ["BITBUCKET_BASE64_TOKEN"] = base64_auth
        print("successfully added bitbucket authentication")
    else:
        print("incorrect bitbucket username or app password")


def _get_workspace_and_repo_from_url(repo_url: str) -> namedtuple:
    parsed_url = urlparse(repo_url)
    params = parsed_url.path.split("/")
    workspace = params[1]
    repo = params[2]
    repo_data_tuple = namedtuple("Repo", ["workspace", "repo"])(workspace, repo)
    return repo_data_tuple


def _transform_days_ago_int_to_iso_date(days_ago: int) -> str:
    days_ago_date = datetime.now() - timedelta(days=days_ago)
    days_ago_date = days_ago_date.replace(hour=0, minute=0, second=0, microsecond=0)
    days_ago_iso_date = days_ago_date.isoformat()
    return days_ago_iso_date


def _get_bitbucket_pr_raw_data_page(
    repo_data_tuple: namedtuple, days_ago: int, page_num: int = 1
) -> dict:
    url = f"https://api.bitbucket.org/2.0/repositories/{repo_data_tuple.workspace}/{repo_data_tuple.repo}/pullrequests"

    query_params = {
        # "state": "MERGED",
        "pagelen": 50,
        "page": page_num,
        "q": f'updated_on >= {_transform_days_ago_int_to_iso_date(days_ago)} AND state = "MERGED"',
    }

    headers = {"Authorization": f"Basic {environ['BITBUCKET_BASE64_TOKEN']}"}

    response = get(url=url, headers=headers, params=query_params)
    if response.status_code == 200:
        if response.json()['size'] == 0:
            print('no pull requests found in the selected timeframe')
            return None
        bitbucket_raw_pr_data = response.json()
        next_page_exists = ('next') in bitbucket_raw_pr_data.keys()
        while next_page_exists:
            query_params['page'] += 1
            next_response = get(url=url,headers=headers,params=query_params)
            next_response_dict = next_response.json()
            next_response_values = next_response_dict['values']
            next_page_exists = ('next' in next_response_dict)
            bitbucket_raw_pr_data['values'].extend(next_response_values)
        return bitbucket_raw_pr_data
    else:
        print('no')
        raise Exception("failed to get bitbucket pull requests data")


def _format_bitbucket_pr_raw_data(bitbucket_raw_pr_data):
    prs = bitbucket_raw_pr_data["values"]
    prs_filtered = []
    for pr in prs:
        pr_id = pr["id"]
        pr_title = pr["title"]
        pr_description = pr["description"]
        pr_merge_datetime = datetime.fromisoformat(pr["updated_on"])
        pr_filtered = {
            "number": pr_id,
            "title": pr_title,
            "body" : pr_description,
            "merged_at" : pr_merge_datetime
        }
        prs_filtered.append(pr_filtered)
    return prs_filtered

def _get_bitbucket_pr_activity_log(pr_number:int,repo_data_tuple:namedtuple) -> dict:
    url = f"https://api.bitbucket.org/2.0/repositories/{repo_data_tuple.workspace}/{repo_data_tuple.repo}/pullrequests/{pr_number}/activity"
    headers = {"Authorization": f"Basic {environ['BITBUCKET_BASE64_TOKEN']}"}

    query_params = {
        # "state": "MERGED",
        "pagelen": 50,
    }
    
    response = get(url=url,headers=headers,params=query_params)
    
    if response.status_code == 200:
        bitbucket_raw_pr_activity_data = response.json()
        next_page_exists = ('next' in bitbucket_raw_pr_activity_data)
        if next_page_exists:
            next_page_url = bitbucket_raw_pr_activity_data['next']
        while next_page_exists:
            next_response = get(url=next_page_url)
            next_response_dict = next_response.json()
            next_page_exists = ('next' in next_response_dict.keys())
            if next_page_exists:
                next_page_url = next_response_dict['next']
                pass
            next_response_values = next_response_dict['values']
            bitbucket_raw_pr_activity_data['values'].extend(next_response_values)
            
            
        return bitbucket_raw_pr_activity_data
    else:
        print(response.request.url)
        print(response.status_code)
        print(response.reason)
        raise Exception("failed to get bitbucket pull requests activity data")

def _get_approvals_from_bitbucket_pr_activity_log(pr_activity_log:dict) -> dict:
    approvals_list = []
    values_dicts_list : list = pr_activity_log['values']
    for subdict in values_dicts_list:
        subdict :dict
        approval_dict = subdict.get('approval')
        if approval_dict:
            username = approval_dict['user']['display_name']
            state = 'APPROVED'
            submitted_at = datetime.fromisoformat(approval_dict['date'])
            approval_event = {
                'username': username,
                'state': state,
                'submitted_at': submitted_at
            }
            approvals_list.append(approval_event)
    return approvals_list

def _iterate_prs_and_append_approvals_list(prs_filtered:list, repo_data_tuple:namedtuple) -> list:
    for pr in prs_filtered:
        pr_number = pr['number']
        pr_activity_log = _get_bitbucket_pr_activity_log(pr_number=pr_number,repo_data_tuple=repo_data_tuple)
        pr_approvals_list = _get_approvals_from_bitbucket_pr_activity_log(pr_activity_log=pr_activity_log)
        pr['reviews'] = pr_approvals_list
    return prs_filtered

def get_bitbucket_repo_pull_requests_filterd_data(repo_url:str, days_ago:int) -> list:
    repo_data_tuple = _get_workspace_and_repo_from_url(repo_url=repo_url)
    bitbucket_raw_pr_data = _get_bitbucket_pr_raw_data_page(repo_data_tuple=repo_data_tuple, days_ago=days_ago)
    if bitbucket_raw_pr_data is None:
        return None
    prs_filtered = _format_bitbucket_pr_raw_data(bitbucket_raw_pr_data=bitbucket_raw_pr_data)
    prs_final = _iterate_prs_and_append_approvals_list(prs_filtered=prs_filtered,repo_data_tuple=repo_data_tuple)
    return prs_final


if __name__ == "__main__":
    # username = 'Manno_123'
    # app_password = 'ATBByvpEYBkxy9uLdGLfNSQ5rMAd9E502B3A'
    from json import dumps

    repo_url = "https://bitbucket.org/fargo3d/public/src/bb3829f0c860c774e09f9c7299a0c36863fe19d5/?at=release%2Fpublic"
    days_ago = 121
    repo_data_tuple = _get_workspace_and_repo_from_url(repo_url=repo_url)
    eshta = _get_bitbucket_pr_raw_data_page(
        repo_data_tuple=repo_data_tuple, days_ago=days_ago
    )
    with open("test.json", "w") as f:
        f.write(dumps(eshta, indent=4, default=str))
        
    prs_filtered = _format_bitbucket_pr_raw_data(eshta)
    
    with open('test_bitbucket_filtered.json', 'w') as f:
        f.write(dumps(prs_filtered,indent=4, default=str))

    prs_final = _iterate_prs_and_append_approvals_list(prs_filtered,repo_data_tuple)
    
    with open('test_bitbucket_final.json', 'w') as f:
        f.write(dumps(prs_final,indent=4, default=str))