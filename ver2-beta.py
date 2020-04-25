import re
import pywikibot
import datetime

def TellLastRun():
    page = pywikibot.Page(SITE, "User:UserRightsBot/last-run")
    try:
        old_text = page.get(get_redirect=False)
    except pywikibot.exceptions.NoPage:
        old_text = ""
    out("Updating last run time", newline=True, date=True, color="yellow")
    commit(old_text, str(datetime.datetime.utcnow()), page, "Updating last complete run time")

def commit(old_text, new_text, page, summary):
    """Show diff and submit text to page."""
    out("\nAbout to make changes at : '%s'" % page.title())
    pywikibot.showDiff(old_text, new_text)
    page.put(new_text, summary=summary, watchArticle=True, minorEdit=False)

def out(text, newline=True, date=False, color=None):
    """Just output some text to the consoloe or log."""
    if color:
        text = "\03{%s}%s\03{default}" % (color, text)
    dstr = (
        "%s: " % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if date
        else ""
    )
    pywikibot.stdout("%s%s" % (dstr, text), newline=newline)

def users_in_section(text):
    """Get all users in a particular rights's nomination area."""
    users = re.findall(r"{{User5\|(.*?)}}", text)
    return users

def getCandText(username, right_section):
    """Get the candidate's nomination from COM:RFR, includes all commnent."""
    return re.search((r"(.*?\n.*?{{User5\|%s}}(?:[\s\S]*?))(?:[=]{2,4})" % (username.replace("(","\(").replace(")","\)").replace("*","\*").replace("?","\?"))), right_section).group(1).strip()

def rights_section_finder_array(text):
    matches = re.finditer(r"==([^=]*?)==", text)
    rights_start_array = []
    right_name_array = []
    for m in matches:
        right_name = m.group(1)
        if right_name and not right_name.isspace():
            right_name_array.append(right_name.strip())
            right_start = m.group(0)
            rights_start_array.append(right_start)
    array_regex = []
    for i,start in enumerate(rights_start_array):
        regex = "%s(.*)%s" % (start, rights_start_array[1+i] if i < (len(rights_start_array)-1) else "<!-- User:UserRightsBot - ON -->")
        array_regex.append(regex)
    return right_name_array, array_regex

def handle_candidates():
    rights_name_array, rights_regex_array = rights_section_finder_array(text)
    for right_name in rights_name_array:
        right_regex = rights_regex_array[rights_name_array.index(right_name)]
        right_section = re.search(right_regex, text, re.DOTALL).group(1)
        users = users_in_section(text)
        for user in users:
            candidate_text = getCandText(username, right_section)
            if re.search((r"{{(?:[Nn]ot[\s|][Dd]one|[Nn][dD]).*?}}"), candidate_text):
                out("User:%s is denied %s rights" % (user,right), color='red', date=True)
            elif re.search((r"{{(?:[Dd]one|[dD]|[Gg]ranted).*?}}"), candidate_text) is not None:
                out("User:%s is granted  %s rights" % (user,right), color="green", date=True)
            else:
                out("User:%s is still waiting for %s rights to be granted" % (user,right), color='white', date=True)
                continue

    

def main():
    if not SITE.logged_in():
        SITE.login()
    handle_candidates()
    TellLastRun()

#print(rights_section_finder_array(text))

if __name__ == "__main__":
  try:
    main()
  finally:
    pywikibot.stopme()
