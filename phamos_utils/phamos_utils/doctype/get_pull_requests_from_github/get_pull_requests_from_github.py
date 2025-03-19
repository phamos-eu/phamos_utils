# Copyright (c) 2025, Phamos GmbH and contributors
# For license information, please see license.txt

import frappe
import re
import requests
from frappe.model.document import Document


class GetPullRequestsfromGithub(Document):
	pass

@frappe.whitelist()
def fetch_pull_requests():
	print("Fetching PRs")
	doc = frappe.get_single("Get Pull Requests from Github")
	prs = search_github_prs(doc)
	frappe.db.set_value("Get Pull Requests from Github", doc.name, "resulting_list_of_pull_requests", prs)
            
def search_github_prs(doc):
	headers = {"Authorization": f"token {doc.get_password('github_token')}"}
	pr_list = []

	issues = doc.list_of_parent_and_child_issues.split("\n")
	
	for issue in issues:
		issue_number = extract_issue_numbers(issue)
		if not issue_number:
			continue
		query = f'repo:{doc.github_repository} "{issue_number}" in:body is:pr'
		url = f"{doc.github_base_url}/search/issues?q={query}"
		
		response = requests.get(url, headers=headers)
		if response.status_code != 200:
			print("Error fetching PRs:", response.text)
			continue
		
		for pr in response.json().get("items", []):
			if issue in pr["body"]:
				pr_list.append(pr["html_url"])

	pr_list = "\n".join(sorted(list(set(pr_list))))

	return pr_list

def extract_issue_numbers(issue):
    match = re.search(r"/(issues|work_items)/(\d+)", issue)
    if match:
        return match.group(2)