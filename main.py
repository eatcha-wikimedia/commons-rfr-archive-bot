import re
import pywikibot
import datetime
from datetime import datetime
from pathlib import Path
import csv
import os

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
    dstr = (
        "%s: " % datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if date
        else ""
    )
    pywikibot.stdout("%s%s" % (dstr, text), newline=newline)


def reg_date(pwb_user):
    """Recent most editor for file."""
    ts = pwb_user.registration(force=True)
    return datetime.strptime(str(ts), "%Y-%m-%dT%H:%M:%SZ")


def dataset_maker(right, status, username):
    Path(".logs").mkdir(parents=True, exist_ok=True)
    dataset = ".logs/rights_data.csv"
    if not os.path.isfile(dataset):
        open(dataset, "w").close()
        with open(dataset, mode="a") as f:
            f.write(
                "UserName,HasLocalUserPage,EntryDate,IsRightGranted,RequestedRight,EditCount,AccountAge,Gender,CanMail,AllRights,Scores\n"
            )

    percent = lambda num, total: int((num / total) * 100)
    date_yyyy_mm_dd = (datetime.utcnow()).strftime("%Y-%m-%d")
    right_granted_or_not = True
    if status == "/Denied/":
        right_granted_or_not = False

    pwb_user = pywikibot.User(source=SITE, title=username)
    has_local_user_page = pwb_user.exists()
    requested_right = right
    edit_count = pwb_user.editCount(force=True)
    all_rights = ",".join([x for x in pwb_user.groups() if x != "*"])
    try:  # see User:Yann, one of the first person on commmons
        account_age_days = (datetime.utcnow() - reg_date(pwb_user)).days
    except ValueError:
        account_age_days = 10000
    gender = pwb_user.gender(force=True)
    is_mailable = pwb_user.isEmailable(force=True)
    x = pwb_user.contributions(total=2000)
    no_file = 0
    no_commons = 0
    no_template = 0
    no_category = 0
    no_mediaWiki = 0
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
    file_score = percent(no_file, i)
    commons_score = percent(no_commons, i)
    template_score = percent(no_template, i)
    category_score = percent(no_category, i)
    mediaWiki_score = percent(no_mediaWiki, i)
    score = "file %d,commons %d,template %d,category %d,mediawiki %d" % (
        file_score,
        commons_score,
        template_score,
        category_score,
        mediaWiki_score,
    )
    with open(dataset, mode="a") as ds:
        writer = csv.writer(ds, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                username,
                has_local_user_page,
                date_yyyy_mm_dd,
                right_granted_or_not,
                requested_right,
                edit_count,
                account_age_days,
                gender,
                is_mailable,
                all_rights,
                score,
            ]
        )


def users_in_section(text):
    """Get all users in a particular rights's nomination area."""
    users = re.findall(r"{{[Uu]ser5\|(.*?)}}", text)
    return users


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
    matches = re.finditer(r"==([^|=]*?)==", text)
    rights_start_array = []
    right_name_array = []
    for m in matches:
        right_name = m.group(1)
        if right_name and not right_name.isspace():
            right_name_array.append(right_name.strip())
            right_start = m.group(0)
            rights_start_array.append(right_start)
    array_regex = []
    for i, start in enumerate(rights_start_array):
        regex = "%s(.*)%s" % (
            start,
            rights_start_array[1 + i]
            if i < (len(rights_start_array) - 1)
            else "<!-- User:UserRightsBot - ON -->",
        )
        array_regex.append(regex)
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
        (
            rfr_base_page_name
            + status
            + right
            + "/"
            + str((datetime.utcnow()).year)
        ),
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


def hours_since_granted(text):
    time_stamps = re.findall(
        r"[0-9]{1,2}:[0-9]{1,2},\s[0-9]{1,2}\s[a-zA-Z]{1,9}\s[0-9]{4}\s\(UTC\)", text
    )
    for time_stamp in time_stamps:
        last_edit_time = time_stamp
    try:
        dt = (datetime.utcnow()) - datetime.strptime(
            last_edit_time, "%H:%M, %d %B %Y (UTC)"
        )
    except UnboundLocalError:
        return 0
    return int(dt.days * 24 + dt.seconds // 3600)


def handle_candidates():
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
        right_regex = rights_regex_array[rights_name_array.index(right_name)]
        right_section = re.search(right_regex, text, re.DOTALL).group(1)
        users = users_in_section(right_section)
        for user in users:
            candidate_text = getCandText(user, right_section)
            dt = hours_since_granted(candidate_text)
            if dt < 12:
                out(
                    "candidate %s is %d hours only, will wait for 12 hours atleast"
                    % (user, dt),
                    color="yellow",
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
                    "User:%s is still not granted %s right." % (user, right_name),
                    color="white",
                    date=True,
                )
                continue


def main():
    if not SITE.logged_in():
        SITE.login()
    handle_candidates()


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
