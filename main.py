import re, re, csv, pywikibot
from pathlib import Path
from datetime import datetime


SITE = pywikibot.Site()
rfr_base_page_name = "Commons:Requests_for_rights"
rfr_page = pywikibot.Page(SITE, rfr_base_page_name)


def commit(old_text, new_text, page, summary):
    """Show diff and submit text to page."""
    out("\nAbout to make changes at : '%s'" % page.title())
    pywikibot.showDiff(old_text, new_text)
    page.put(new_text, summary=summary, watchArticle=True, minorEdit=False)


def out(text, newline=True, date=False, color=None):
    """Just output some text to the console or log."""
    if color:
        text = "\03{%s}%s\03{default}" % (color, text)
    dstr = "%s: " % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if date else ""
    pywikibot.stdout("%s%s" % (dstr, text), newline=newline)


def reg_date(pwb_user):
    """Registration date (on commons) of the user."""
    return datetime.strptime(
        str(pwb_user.registration(force=True)), "%Y-%m-%dT%H:%M:%SZ"
    )


def dataset_maker(requested_right, status, username):
    """
    We are collecting some publicly available data that can be
    used to train bots to recommend users for rights or even
    granting user rights. The dataset generated by this function
    can be shared on request, contact User:Eatcha on commons.
    """
    Path(".logs").mkdir(parents=True, exist_ok=True)
    dataset = ".logs/rights_data.csv"
    if not os.path.isfile(dataset):
        open(dataset, "w").close()
        with open(dataset, mode="a") as f:
            f.write(
                "UserName,HasLocalUserPage,EntryDate,IsRightGranted,RequestedRight,EditCount,AccountAge,Gender,CanMail,AllRights,Scores\n"
            )

    percent = lambda num, total: int((num / total) * 100)
    pwb_user = pywikibot.User(source=SITE, title=username)

    try:  # see User:Yann, one of the first users on commmons. Raises exception
        account_age_days = (datetime.utcnow() - reg_date(pwb_user)).days
    except ValueError:
        account_age_days = 10000

    x = pwb_user.contributions(total=2000)
    no_file, no_commons, no_template, no_category, no_mediaWiki = 0, 0, 0, 0, 0
    for i, y in enumerate(x, start=1):
        ns = y[0].namespace()
        if "File" in ns:
            no_file += 1
        elif "Project" in ns:
            no_commons += 1
        elif "Template" in ns:
            no_template += 1
        elif "Category" in ns:
            no_category += 1
        elif "MediaWiki" in ns:
            no_mediaWiki += 1

    score = "file %d,commons %d,template %d,category %d,mediawiki %d" % (
        percent(no_file, i),
        percent(no_commons, i),
        percent(no_template, i),
        percent(no_category, i),
        percent(no_mediaWiki, i),
    )
    with open(dataset, mode="a") as ds:
        writer = csv.writer(ds, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                username,
                pwb_user.exists(),
                (datetime.utcnow()).strftime("%Y-%m-%d"),
                (True if status == "/Denied/" else False),
                requested_right,
                pwb_user.editCount(force=True),
                account_age_days,
                pwb_user.gender(force=True),
                pwb_user.isEmailable(force=True),
                ",".join([x for x in pwb_user.groups() if x != "*"]),
                score,
            ]
        )


def users_in_section(text):
    """Get all users in a particular rights's nomination area."""
    return re.findall(r"{{[Uu]ser5\|(.*?)}}", text)


def getCandText(username, right_section):
    """Get the candidate's nomination from COM:RFR, includes all commnent."""
    return re.search(
        (
            r"(.*?(?:[\n]{1,3}).*?{{[Uu]ser5\|%s}}(?:[\s\S]*?))(?:\n\n|==)"
            % (
                username.replace("(", "\(")
                .replace(")", "\)")
                .replace("*", "\*")
                .replace("?", "\?")
            )
        ),
        right_section,
    ).group(1)


def rights_section_finder_array(text):
    """
    Finds rights listed on COM:RFR, creates
    the regex to match the right's section
    """
    rights_start_array = []
    right_name_array = []
    for m in re.finditer(r"==([^|=]*?)==", text):
        right_name = m.group(1)
        if right_name and not right_name.isspace():
            right_name_array.append(right_name.strip())
            rights_start_array.append(m.group(0))
    array_regex = []
    for i, start in enumerate(rights_start_array):
        array_regex.append(
            (
                "%s(.*)%s"
                % (
                    start,
                    rights_start_array[1 + i]
                    if i < (len(rights_start_array) - 1)
                    else "<!-- User:UserRightsBot - ON -->",
                )
            )
        )
    return right_name_array, array_regex


def archive(text_to_add, right, status, username):
    """If a nomination is approved/declined add to archive and remove from COM:RFR page."""
    if not right:
        out(
            " New rights found, please declare in dict_for_archive for conversion",
            color="red",
        )
        return
    archive_page = pywikibot.Page(
        SITE,
        (rfr_base_page_name + status + right + "/" + str((datetime.utcnow()).year)),
    )
    try:
        old_text = archive_page.get(get_redirect=False)
    except pywikibot.exceptions.NoPage:
        old_text = ""
    try:
        commit(
            old_text,
            (old_text + "\n\n" + text_to_add),
            archive_page,
            summary=(
                "Adding "
                + ("[[User:%s|%s]]'s " % (username, username))
                + right
                + " request"
            ),
        )
    except pywikibot.LockedPage as error:
        out(error, color="red")
        return
    try:
        commit(
            rfr_page.get(),
            (rfr_page.get(get_redirect=False)).replace("\n" + text_to_add, ""),
            rfr_page,
            summary=(
                "Archiving "
                + ("[[User:%s|%s]]'s " % (username, username))
                + right
                + " request"
                + (" (Status: %s) " % (status.replace("/", "", 2)))
            ),
        )
    except pywikibot.LockedPage as error:
        out(error, color="red")
        return

    dataset_maker(right, status, username.replace("_", " "))


def hours_since_last_signed(text):
    """Hours elapsed since the time at which nomination was last signed."""
    for time_stamp in re.findall(
        r"[0-9]{1,2}:[0-9]{1,2},\s[0-9]{1,2}\s[a-zA-Z]{1,9}\s[0-9]{4}\s\(UTC\)", text
    ):
        last_edit_time = time_stamp
    try:
        dt = (datetime.utcnow()) - datetime.strptime(
            last_edit_time, "%H:%M, %d %B %Y (UTC)"
        )
    except UnboundLocalError:
        return 0
    return int(dt.days * 24 + dt.seconds // 3600)


def handle_candidates(wait_hour):
    dict_for_archive = {
        "Confirmed": "Confirmed",
        "Autopatrol": "Autopatrolled",
        "AutoWikiBrowser access": "AutoWikiBrowser access",
        "Patroller": "Patroller",
        "Rollback": "Rollback",
        "Template editor": "Template editor",
        "Filemover": "Filemover",
        "Upload Wizard campaign editors": "Upload Wizard campaign editors",
        "Translation administrators & GW Toolset users": None,
    }
    text = rfr_page.get()
    rights_name_array, rights_regex_array = rights_section_finder_array(text)
    for right_name in rights_name_array:
        right_section = re.search(
            rights_regex_array[rights_name_array.index(right_name)], text, re.DOTALL
        ).group(1)
        for user in users_in_section(right_section):
            candidate_text = getCandText(user, right_section)
            dt = hours_since_last_signed(candidate_text)
            if dt < wait_hour:
                out(
                    "[[User:%s]] was granted '%s' right %d hours ago, %d more hours to archiving."
                    % (user, right_name, dt, int(wait_hour - dt)),
                    color="white",
                    date=True,
                )
                continue

            if (
                re.search((r"{{(?:[Nn]ot[\s|][Dd]one|[Nn][dD]).*?}}"), candidate_text)
                is not None
            ):
                out(
                    "User:%s is denied %s rights" % (user, right_name),
                    color="red",
                    date=True,
                )
                archive(
                    candidate_text,
                    dict_for_archive.get(right_name, None),
                    "/Denied/",
                    user,
                )
            elif (
                re.search((r"{{(?:[Dd]one|[dD]|[Gg]ranted).*?}}"), candidate_text)
                is not None
            ):
                out(
                    "User:%s is granted  %s right." % (user, right_name),
                    color="green",
                    date=True,
                )
                archive(
                    candidate_text,
                    dict_for_archive.get(right_name, None),
                    "/Approved/",
                    user,
                )
            else:
                out(
                    "[[User:%s]] is not yet granted/denied the '%s' right."
                    % (user, right_name),
                    color="white",
                    date=True,
                )
                continue


def main():
    if not SITE.logged_in():
        SITE.login()
    wait_hour = 12
    handle_candidates(wait_hour)


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
