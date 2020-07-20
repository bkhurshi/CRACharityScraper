#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests
import argparse

#Parse arguments
parser = argparse.ArgumentParser(description='Scrape data about charities from the CRA website')
parser.add_argument('queries', nargs='+', help='The terms used in the CRA charity search')
args=parser.parse_args()
baseUrl = 'https://apps.cra-arc.gc.ca'

def parseResultPage(url):
    response = requests.get(url)
    page = BeautifulSoup(response.content, "html.parser")

    # Charity Name
    # <div class="row">
    #	<div class="col-md-12">
    #		<h1 class="mrgn-tp-md" id="wb-cont">Acad&eacute;mie Islamique du Manitoba Inc./Islamic Academy of Manitoba Inc. — Quick View</h1>
    #	</div>
    # </div>
    charityName = page.find('h1').text.strip('— Quick View').replace(',','')

    # Charity Number
    # Looks like:
    #<div class="row">
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">Registration no.:</div>
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-9">
    #		<strong>
    #			886188507
    #			RR
    #			0001
    #		</strong>
    #	</div>
    #</div>
    charityNumber = [div for div in page.findAll('div') if 'Registration no.:' in div.contents][0].findNext('div').contents[1].contents[0].replace("\r\n","").replace("\t","").replace(',','')

    # Effective Date
    #<div class="row">
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">Effective date of status:</div>
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-9">
    #		<strong>
    #			2007-05-25
    #		</strong>
    #	</div>
    #</div>
    effectiveDate = [div for div in page.findAll('div') if 'Effective date of status:' in div.contents][0].findNext('div').contents[1].contents[0].replace("\r\n","").replace("\t","").replace(',','')

    # Designation
    # <div class="row">
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-3">Designation:</div>
    #	<div class="col-xs-12 col-sm-6 col-md-6 col-lg-9"><strong>
    #
    #			Private foundation
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #		</strong>
    #		<a href="https://www.canada.ca/en/revenue-agency/services/charities-giving/charities/charities-giving-glossary.html#private" target="_blank"><span class="glyphicon glyphicon-question-sign"></span></a>
    #	</div>
    #</div>
    designation = [div for div in page.findAll('div') if 'Designation:' in div.contents][0].findNext('div').contents[0].contents[0].replace('\r\n','').replace('\t','').replace(',','')

    # Total Revenue
    # 		<p class="h5 mrgn-lft-md mrgn-tp-md"> Total revenue: $250,012.00</p>
    totalRevenue = [x for x in [p.contents for p in page.findAll('p')] if 'Total revenue:' in str(x)][0][0].strip('Total revenue: ').replace(',', '')

    # Government Funding
    #<th>Government funding $195,137.00 (78.05%)</th>
    governmentFunding = [x for x in [p.contents for p in page.findAll('th')] if 'Government funding' in str(x)][0][0].strip('Government funding').strip(')').split('(')[0].replace(',', '')

    # Total Expenses
    # 		<p class="h5 mrgn-lft-md mrgn-tp-md">Total expenses: $260,531.00</p>
    totalExpenses = [x for x in [p.contents for p in page.findAll('p')] if 'Total expenses:' in str(x)][0][0].strip('Total expenses: ').replace(',', '')

    # Management and administration
    #<th>Government funding $195,137.00 (78.05%)</th>
    management = [x for x in [p.contents for p in page.findAll('th')] if 'Management and administration' in str(x)][0][0].strip('Management and administration').strip(')').replace('\t','').split('(')[0].replace(',', '')

    print(charityName + ',' + charityNumber + ',' + effectiveDate + ',' + designation + ',' + totalRevenue + ',' + governmentFunding + ',' + totalExpenses + ',' + management)


print('Name, Registration Number, Date of Status, Designation, Revenue, Government Funding, Expenses, Management')

for query in args.queries:
    for pageNum in range(1,6):
        url = 'https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/bscSrch?dsrdPg=' + str(pageNum) + '&q.srchNm=' + query + '&q.stts=0007&q.ordrClmn=NAME&q.ordrRnk=ASC'
        response = requests.get(url)
        page = BeautifulSoup(response.content, "html.parser")

        urls = [link['href'] for link in page.findAll('a', href=True) if "selectedCharityBn=" in link['href']]
        if len(urls) == 0:
            break

        for link in page.findAll('a', href=True):
            if "&selectedCharityBn=" in link['href']:
                url = baseUrl + link['href']
                try:
                    parseResultPage(url)
                except:
                    print("ERROR: " + url)
