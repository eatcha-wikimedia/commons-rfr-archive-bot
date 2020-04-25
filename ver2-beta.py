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

def rights_section_finder_array(text):
    matches = re.finditer(r"==([^=]*?)==", text)
    right_start_array = []
    right_name_array = []
    for m in matches:
        right_name = m.group(1)
        if right_name and not right_name.isspace():
            right_name_array.append(right_name.strip())
            right_start = m.group(0)
            right_start_array.append(right_start)
    array_regex = []
    for i,start in enumerate(right_start_array):
        regex = "%s(.*)%s" % (start, right_start_array[1+i] if i < (len(right_start_array)-1) else "<!-- User:UserRightsBot - ON -->")
        array_regex.append(regex)
    return right_name_array, array_regex

def handle_candidates(right):
    pass

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
