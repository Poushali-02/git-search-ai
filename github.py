import requests
def get_issues_of_user(username:str, access_token):
    if not username or not access_token:
        return "GitHub credentials not found. Please log in with GitHub."
    url = f"https://api.github.com/search/issues?q=assignee:{username}+is:open"
    headers = {
        "Authorization" : f"token {access_token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "AISearchEngine/1.0"
    }
    try:
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            issues_data = response.json()
            issues = issues_data.get("items", [])
            if issues:
                issue_list = [f"- {issue['title']} (#{issue['number']})" for issue in issues]
                return "\n".join(issue_list)
            else:
                return "no issues are assigned to you currently! You're free!"
        else:
            print(f"Error response: {response.text}")
            return f"Error: Error fetcxhing issues: {response.text}"
    except Exception as e:
        return f"Error fetching issues: {str(e)}"