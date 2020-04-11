import pywikibot
import re, datetime

SITE = pywikibot.Site()
rfr_base_page_name = "Commons:Requests_for_rights"
rfr_page = pywikibot.Page(SITE, rfr_base_page_name)

def getCandText(username, rights_section):
    """Get the candidate's nomination from COM:RFR, includes all commnent."""
    return re.search((r"((?:.*?)\n(?:\s*?)(?:\*|#|)(?:\s*?){{[Uu]ser5\|%s}}(?:[\s\S]*?))(<!--|====)" % (username.replace("(","\(").replace(")","\)").replace("*","\*").replace("?","\?"))), rights_section).group(1)

def users_in_section(right):
    """Get all users in a particular rights's nomination area."""
    section = re.search(("<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)start(?:[\s|]*?)-->([\s\S]*?)<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)end(?:[\s|]*?)-->" % (right,right)), (rfr_page.get(get_redirect=False))).group()
    users = re.findall(r"{{User5\|(.*?)}}", section)
    return section, users

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

def human_help(message):
    """Ask humans for help, if can't self fix missing helper comments."""
    full_message = ("\n==Need human help : Self-Diagnosis failed - UserRightsBot ==\n" + message)

    try:
        dev = pywikibot.User(SITE, "Eatcha")
        dev.send_email("Need human help : UserRightsBot - Self-Diagnosis failed", full_message, ccme=False)
    except:
        pass

def checks(right):
    """Perform some checks to ensure we are handling nominations correctly, also try to self add comments if not found."""
    if re.search((r"<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)end(?:[\s|]*?)-->" % right), (rfr_page.get(get_redirect=True))) is None:
        if rights.index(right) < (len(rights)-1):
            regex = r"<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)start(?:[\s|]*?)-->" % rights[(rights.index(right)+1)]
        else:
            regex = r"==(?:\s*)Translation(?:\s*)administrators(?:\s*)&(?:\s*)GW(?:\s*)Toolset(?:\s*)users(?:\s*)=="
        try:
            next_start = re.search(regex, rfr_page.get(get_redirect=True)).group()
            new_text = rfr_page.get().replace(next_start, (("<!-- %s candidates end -->" % right) + "\n" + next_start))
            edit_summary = ("Self-Diagnosis  : adding %s end comment" % right)
            commit(rfr_page.get(), new_text, rfr_page, summary=edit_summary)
        except:
            human_help("Missing end tag for %s , but unable to self fix. You can fix this error by adding the following text at appropriate loction on [[COM:RFR]]\n<code><nowiki><!-- %s candidates end --></nowiki></code>" % (right, right))
    elif re.search((r"<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)start(?:[\s|]*?)-->" % right), (rfr_page.get(get_redirect=True))) is None:
        if rights.index(right) > 0:
            regex = r"<!--(?:[\s|]*?)%s(?:[\s|]*?)candidates(?:[\s|]*?)end(?:[\s|]*?)-->" % rights[(rights.index(right)-1)]
        else:
            regex = r"==(\s*)%s(\s*)==" % (rights[0])
        try:
            prior_end = re.search(regex, rfr_page.get(get_redirect=True)).group()
            new_text = rfr_page.get().replace(prior_end, (prior_end + "\n" + ("<!-- %s candidates start -->" % right)))
            edit_summary = ("Self-Diagnosis  : adding %s start comment" % right)
            commit(rfr_page.get(), new_text, rfr_page, summary=edit_summary)
        except:
            human_help("Missing start tag for %s , but unable to self fix. You can fix this error by adding the following text at appropriate loction on [[COM:RFR]]\n<code><nowiki><!-- %s candidates start --></nowiki></code>" % (right, right))

def archive(text_to_add,right,status,username):
    """If a nomination is approved/declined add to archive and remove from COM:RFR page."""
    archive_page = pywikibot.Page(SITE, (rfr_base_page_name + status + right + "/" + str((datetime.datetime.utcnow()).year)))
    try:
        old_text = archive_page.get(get_redirect=False)
    except pywikibot.exceptions.NoPage:
        old_text = ""
    try:
        commit(old_text, (old_text + "\n" + text_to_add), archive_page, summary=("Adding " + ("[[User:%s|%s]]'s " % (username,username)) + right + " request"))
    except pywikibot.LockedPage as error:
        human_help("%s is locked, unable to archive closed candidates. Update my userrights or downgrade protection.\nError Log :\n %s" % (archive_page, error))
        return
    try:
        commit(rfr_page.get(), (rfr_page.get(get_redirect=False)).replace(text_to_add, ""), rfr_page, summary=("Removing " + ("[[User:%s|%s]]'s " % (username,username)) + right + " request" + (" (Status: %s) " % (status.replace("/","",2)))))
    except pywikibot.LockedPage as error:
        human_help("%s is locked, unable to remove closed candidates. Update my userrights or downgrade protection.\nError Log :\n %s" % ("COM:RFR", error))
        return

def TellLastRun():
    page = pywikibot.Page(SITE, "User:UserRightsBot/last-run")
    try:
        old_text = page.get(get_redirect=False)
    except pywikibot.exceptions.NoPage:
        old_text = ""
    out("Updating last run time", newline=True, date=True, color="yellow")
    commit(old_text, str(datetime.datetime.utcnow()), page, "Updating last complete run time")

def handle_candidates(right):
    """Sort the candidates and handle them."""
    section, users = users_in_section(right)
    for user in users:
        try:
            candidate_text = getCandText(user, section)
        except AttributeError:
            continue
        if re.search((r"{{(?:[Dd]one|[dD]|[Gg]ranted).*?}}"), candidate_text) is not None:
            out("User:%s is granted  %s rights" % (user,right), color="green", date=True)
            archive(candidate_text, right, "/Approved/", user)
        elif re.search((r"{{(?:[Nn]ot[\s|][Dd]one|[Nn][dD]).*?}}"), candidate_text) is not None:
            out("User:%s is denied %s rights" % (user,right), color='red', date=True)
            archive(candidate_text, right, "/Denied/", user)
        else:
            out("User:%s is still waiting for %s rights to be granted" % (user,right), color='white', date=True)
            continue

def main():
    """Triggers checks and candidate handling for all rights. """
    global rights
    if not SITE.logged_in():
        SITE.login()
    rights = [
        'Confirmed',                     # 0
        'Autopatrolled',                 # 1
        'AutoWikiBrowser access',        # 2
        'Patroller',                     # 3
        'Rollback',                      # 4
        'Filemover',                     # 5
        'Template editor',               # 6
        'Upload Wizard campaign editors' # 7
        ]
    for right in rights:
        checks(right)
        handle_candidates(right)
    TellLastRun()

if __name__ == "__main__":
  try:
    main()
  finally:
    pywikibot.stopme()
