'''
	Utility scripts that scraps json dumps of game unit data from the latest communitydragon data file dump.
'''

from website import db, create_app
from website.models import Problem
from lxml import html
from pprint import pprint
import requests
import re

app = create_app()
app.app_context().push()

base_url = 'http://www.usaco.org/index.php?page=viewproblem2&cpid='
headers = {}
headers[
    'User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

first_index = 0
last_index = 1500

failed = []
for i in range(first_index, last_index + 1):
    url = base_url + str(i)
    print('Requesting: ' + url)

    try:
        page = requests.get(url, headers=headers)
        data = html.fromstring(page.content)
        contestInfo = data.xpath('string(//div[@class="panel"]/h2[1])').split()
        nameInfo = data.xpath('string(//div[@class="panel"]/h2[2])').split('.')

        if not contestInfo:
            continue

        print(contestInfo, nameInfo)

        pid = i
        for info in contestInfo:
            if re.match(r"20[0-9][0-9]", info):
                year = info
            elif info == "US":
                month = "US Open"
            elif info == "November" or info == "December" or info == "January" or info == "February" or info == "March":
                month = info
            elif info == "Bronze" or info == "Silver" or info == "Gold" or info == "Platinum":
                div = info

        name = nameInfo[1].strip()

        print(pid, year, month, div, name)

        problem = Problem(pid=pid, year=year, month=month, div=div, name=name)
        db.session.add(problem)
    except Exception as e:
        print(
            'Failed to retrieve data for {} {} {} {} {}. ({})'.format(i, year, month, div, name, str(e)))
        failed.append(name.strip())

print('Error retrieving the following problems:')
pprint(failed)

db.session.commit()
