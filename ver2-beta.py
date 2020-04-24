text = """
{{Editnotices/Page/Commons:Requests for rights}}
{{Archive box|
{{Search box|root=Commons:Requests for rights|search-width=20|search-button-label=Search archived requests}}
* [[Commons:Requests for rights/Approved|Approved requests]]
* [[Commons:Requests for rights/Denied|Declined requests]]
}}
<noinclude>[[Category:Commons user rights request pages]]</noinclude>
[[Category:User permissions]]
== Confirmed ==
{{See also|COM:Autoconfirmed users#Confirmed users|Confirmed users}}
{{tmbox|text=Autoconfirmed users don't have to request this flag. To see if you are autoconfirmed, please see [[Special:Preferences|your preferences]].
}}
<!-- Place your request below here. -->

== Autopatrol ==
{{See also|Commons:Patrol#Autopatrol|Autopatrolled users}}
{{tmbox|text=As a rough guideline, [[COM:Administrators|administrators]] usually require editors to have made more than 500 useful non-botlike edits, and to have been active in the last thirty days. Patrollers and License reviewers don't have to request this flag.<br/>
<span style="display:none;" class="small adminonly">[[Commons:Requests for rights/possible autopatrolled candidates|Find possible candidates.]]</span>
}}
<!-- Place your request below here. -->



== AutoWikiBrowser access ==
{{See also|Commons:AutoWikiBrowser/CheckPage}}
<!-- Place your request below here. -->


====[[User:InkoBot|InkoBot]]====
*{{User5|InkoBot}}
:needs bot mode enabled for run, approved task: [[Commons:Bots/Requests/InkoBot II]] Thank you.  [[User:Hgzh|hgzh]] 11:48, 23 April 2020 (UTC)

== Patroller ==
{{See also|Commons:Patrol|Patrol guideline}}
{{tmbox|text=License reviewers don't have to request this flag.}}
<!-- Place your request below here. -->



== Rollback ==
{{See also|Commons:Rollback|Rollback guideline}}
<!-- Place your request below here. -->


====[[User:Charlesjsharp|Charlesjsharp]]====
*{{User5|Charlesjsharp}}
:removed a couple of years ago. I was unaware how rollback should be used. I got no warning. [[https://commons.wikimedia.org/w/index.php?title=User_talk:Srittau&action=edit&section=34|See response from admin]] Thank you. [[User:Charlesjsharp|Charlesjsharp]] ([[User talk:Charlesjsharp|<span class="signature-talk">{{int:Talkpagelinktext}}</span>]]) 16:34, 23 April 2020 (UTC)

====[[User:Acagastya|Acagastya]]====
*{{User5|Acagastya}}
:Hi.  I would like to request the file mover rights.  I haven't requested a lot of file renames, yes.  But I can surely help with other's requests. Thank you. [[user talk:acagastya|<span style="color:#ba0000;">acagastya</span>]] 12:48, 23 April 2020 (UTC)
*{{d|Granted}}. '''- [[User:Fitindia|<span style="font-variant:small-caps;color:#FF7F00;text-shadow:2px 2px 3px #FFA500;">FitIndia</span>]] <sup><small>[[User talk:Fitindia|Talk]] [[Special:EmailUser/Fitindia|✉]]</small></sup>''' 13:58, 23 April 2020 (UTC)

== Template editor ==
{{see also|Commons:Template editor|Template editor}}
<!-- Place your request below here. -->

== Filemover ==
{{See also|Commons:File renaming|Renaming guideline}}
{{tmbox|text=As a rough guideline, [[COM:Administrators|administrators]] usually require editors to have made between 1,000 and 1,500 useful, non-botlike edits or a large amount of justified renaming requests at the Commons before they will consider granting the filemover right.}}
<!-- Place your request below here. -->

====[[User:Walser123|Walser123]]====
*{{User5|Walser123}}
:To handle my own renaming requests and help others rename files. Thank you. - [[User:Walser123|Walser123]] ([[User talk:Walser123|<span class="signature-talk">{{int:Talkpagelinktext}}</span>]]) 10:55, 19 April 2020 (UTC)
::The same words as I wrote them ... Just out of interest, why was your [https://commons.wikimedia.org/w/index.php?title=User_talk:Walser123&diff=410919993&oldid=410030655&diffmode=source last request] declined? --[[User:Killarnee|Killarnee]] (<small>[[User talk:Killarnee|T]]•[[meta:User:Killarnee/1|1]]•[[meta:User:Killarnee/2|2]]</small>) 12:02, 19 April 2020 (UTC)
Hello Killarnee. I wanted to replace a duplicate and rename the file, but instead a new file was made for the replacement picture and now the duplicate still exists. And sorry for using your words, but you wrote exactly what I planned to write so I just copied it ː) Best regards, [[User:Walser123|Walser123]] ([[User talk:Walser123|<span class="signature-talk">{{int:Talkpagelinktext}}</span>]]) 13:23, 19 April 2020 (UTC)


== Upload Wizard campaign editors ==
{{See also|Commons:Upload Wizard campaign editors|Upload Wizard campaign editors}}
<!-- Place your request below here. -->


== Translation administrators & GW Toolset users ==
{{See also|Commons:GWToolset users|GWToolset users|Commons:Translation administrators|Translation administrators}}
{{tmbox|text=Only [[Commons:Bureaucrats|bureaucrats]] can grant these rights, so please request them on the [[Commons:Bureaucrats' noticeboard|bureaucrats' noticeboard]].}}

<!-- User:UserRightsBot - ON -->
"""

import re

def rights_section_finder_array(text):
    matches = re.finditer(r"==([^=]*?)==", text)
    right_start_array = []
    for m in matches:
        right_name = m.group(1)
        if right_name and not right_name.isspace():
            right_start = m.group(0)
            right_start_array.append(right_start)
    array_regex = []
    for i,start in enumerate(right_start_array):
        regex = "%s(.*)%s" % (start, right_start_array[1+i] if i < (len(right_start_array)-1) else "<!-- User:UserRightsBot - ON -->")
        array_regex.append(regex)
    
    return array_regex

print(rights_section_finder_array(text))
