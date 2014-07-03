import requests, bs4, base64, sys, traceback, json

from bs4 import BeautifulSoup

github_user = '*****'
github_pw = '*****'

base_codeplex_url = 'https://REPO.codeplex.com/workitem'
codeplex_issue_count = 100
base_github_url = 'https://api.github.com/repos/USER/REPO/issues'


def TransferCodeplexIssue(issue_num):

  soup = SoupifyCodeplexIssue(issue_num)

  title = GetTitle(soup)
  descr = GetDescription(soup)

  data = """
 {
  "title": "%s",
  "body": "%s",
  "assignee": null,
  "milestone": null,
  "labels": []
} """ % ( title, descr )

  print data

  resp = CallGithubApi(base_github_url, data, requests.post)
  text = resp.text
  dict = json.loads( text )
  url = dict['url'].encode('UTF8')
  TransferCodeplexComments(soup, url)
  MaybeCloseGithubIssue(soup, url)

def TransferCodeplexComments(soup, github_url):

  comments = soup.find_all('div', class_='comment_divider')

  for comment in comments:
      text = Strip(comment.text)
      data = '{  "body": "%s" }' % text
      resp = CallGithubApi(github_url + '/comments', data, requests.post)
      print resp

  MaybeCloseGithubIssue(soup, github_url)

def MaybeCloseGithubIssue(soup, github_url):
 status = GetCodeplexStatus(soup)
 if ( status == 'Closed' ):
   CloseGithubIssue(github_url)

def CloseGithubIssue(github_url):
    data = """ {  "state" : "closed" } """
    resp = CallGithubApi(github_url, data, requests.patch)
    print resp

def CallGithubApi(url, data, method):
    headers = { 'Content-Type': 'application/json', 'Authorization': 'Basic ' + base64.encodestring(github_user + ':' + github_pw) }
    r = method(url, data=data, headers=headers)
    return r

def Soupify(url):
    r = requests.get(url)
    html = r.text
    html = Strip(html)
    soup = BeautifulSoup(html)
    return soup

def SoupifyCodeplexIssue(issue_num):
    url = base_codeplex_url + '/' + str(issue_num)
    soup = Soupify(url)
    return soup

def GetCodeplexStatus(soup):
    status = soup.find(id='StatusLink').contents
    status = status[0].encode('UTF8')
    return status

def GetTitle(soup):
    title = soup.find(id='workItemTitle').contents
    title = title[0].encode('UTF8')
    return title

def GetDescription(soup):
    descr = soup.find(id='descriptionContent').contents
    descr = descr[0].encode('UTF8')
    return descr

def Strip(s):
    return s.replace('\r','').replace('\n','').strip()

for i in range(codeplex_issue_count):
  print 'issue ' + str(i+1)
  try:
    TransferCodeplexIssue(i+1)
  except:
    print "error transferring issue " + str(i+1)
    traceback.print_exc()




