#!/usr/bin/env python3
"""Builds the unsigned "Pay It Forward Contacts" Apple Shortcut.

What it does on the iPhone:
  1. Opens Contacts with checkboxes (Select Contacts, multiple).
  2. For each friend picked, opens a ready-to-send 3-way text (the friend and Steven)
     with the message and the friend's first name filled in. The sender only taps Send.
  3. Returns to the Pay It Forward page, which says thank you.

The web page runs it with  shortcuts://run-shortcut?name=Pay%20It%20Forward%20Contacts&input=text&text=<message>
where <message> contains [First Name]. Run on its own, it uses the default message below.

Sign it on a Mac before sharing (iPhones only import signed shortcuts):
  shortcuts sign --mode anyone --input pay-it-forward-contacts.shortcut --output "Pay It Forward Contacts.shortcut"
"""
import plistlib
import sys
import uuid

STEVEN = "6193687141"
TOKEN = "[First Name]"
DONE_URL = "https://chitown034.github.io/pay-it-forward/#sent"
DEFAULT_MESSAGE = (
    "Hey [First Name], hope you're doing well. I went to a VA home buying seminar today and thought of you "
    "right away. I'm adding Steven here. He's a Navy vet who helps veterans use their VA home loan benefit, "
    "and he'll walk you through yours for free.\n\nSteven, this is [First Name]. Take good care of them."
)
OBJ = "￼"  # placeholder character where a variable sits inside text


def uid():
    return str(uuid.uuid4()).upper()


def output(name, ref):
    return {"OutputName": name, "OutputUUID": ref, "Type": "ActionOutput"}


def attachment(value):
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def text(string, refs=()):
    """Text with variables; each OBJ in `string` is replaced, in order, by the matching ref."""
    by_range, pos = {}, 0
    for ref in refs:
        pos = string.index(OBJ, pos)
        by_range["{%d, 1}" % pos] = ref
        pos += 1
    value = {"string": string}
    if by_range:
        value["attachmentsByRange"] = by_range
    return {"Value": value, "WFSerializationType": "WFTextTokenString"}


def action(identifier, **params):
    return {"WFWorkflowActionIdentifier": "is.workflow.actions." + identifier, "WFWorkflowActionParameters": params}


SHORTCUT_INPUT = {"Type": "ExtensionInput"}
REPEAT_ITEM = {"Type": "Variable", "VariableName": "Repeat Item"}

pick, loop, if_group, if_end = uid(), uid(), uid(), uid()
input_text, default_text = uid(), uid()
first, phones, phone, recipients_text, recipients, message, url_text = (uid() for _ in range(7))

actions = [
    # Message to use: the one passed in by the web page, or the default.
    action(
        "conditional",
        GroupingIdentifier=if_group,
        WFControlFlowMode=0,
        WFCondition=100,  # "has any value"
        WFInput={"Type": "Variable", "Variable": attachment(SHORTCUT_INPUT)},
    ),
    action("gettext", UUID=input_text, WFTextActionText=text(OBJ, [SHORTCUT_INPUT])),
    action("conditional", GroupingIdentifier=if_group, WFControlFlowMode=1),
    action("gettext", UUID=default_text, WFTextActionText=text(DEFAULT_MESSAGE)),
    action("conditional", GroupingIdentifier=if_group, WFControlFlowMode=2, UUID=if_end),
    # Contacts with checkboxes.
    action("selectcontacts", UUID=pick, WFSelectMultiple=True),
    # One 3-way text per friend.
    action(
        "repeat.each",
        GroupingIdentifier=loop,
        WFControlFlowMode=0,
        WFInput=attachment(output("Contacts", pick)),
    ),
    action(
        "properties.contacts",
        UUID=first,
        WFContentItemPropertyName="First Name",
        WFInput=attachment(REPEAT_ITEM),
    ),
    action(
        "properties.contacts",
        UUID=phones,
        WFContentItemPropertyName="Phone Numbers",
        WFInput=attachment(REPEAT_ITEM),
    ),
    action(
        "getitemfromlist",
        UUID=phone,
        WFItemSpecifier="First Item",
        WFInput=attachment(output("Phone Numbers", phones)),
    ),
    # Recipients: the friend's number and Steven's, one per line, split into a list.
    action(
        "gettext",
        UUID=recipients_text,
        WFTextActionText=text(OBJ + "\n" + STEVEN, [output("Item from List", phone)]),
    ),
    action(
        "text.split",
        UUID=recipients,
        **{"Show-text": True},
        text=text(OBJ, [output("Text", recipients_text)]),
        WFTextSeparator="New Lines",
    ),
    # Put the friend's first name into the message.
    action(
        "text.replace",
        UUID=message,
        WFInput=text(OBJ, [output("If Result", if_end)]),
        WFReplaceTextFind=TOKEN,
        WFReplaceTextReplace=text(OBJ, [output("First Name", first)]),
        WFReplaceTextCaseSensitive=True,
        WFReplaceTextRegularExpression=False,
    ),
    # The Messages sheet opens with everything filled in; the sender taps Send.
    action(
        "sendmessage",
        ShowWhenRun=True,
        WFSendMessageActionRecipients=attachment(output("Split Text", recipients)),
        WFSendMessageContent=text(OBJ, [output("Updated Text", message)]),
    ),
    action("repeat.each", GroupingIdentifier=loop, WFControlFlowMode=2, UUID=uid()),
    # Back to the page for a thank-you.
    action("gettext", UUID=url_text, WFTextActionText=text(DONE_URL)),
    action("openurl", WFInput=attachment(output("Text", url_text))),
]

shortcut = {
    "WFWorkflowActions": actions,
    "WFWorkflowClientVersion": "2302.0.4",
    "WFWorkflowMinimumClientVersion": 900,
    "WFWorkflowMinimumClientVersionString": "900",
    "WFWorkflowHasOutputFallback": False,
    "WFWorkflowHasShortcutInputVariables": True,
    "WFWorkflowIcon": {"WFWorkflowIconGlyphNumber": 59511, "WFWorkflowIconStartColor": 4274264319},
    "WFWorkflowImportQuestions": [],
    "WFWorkflowInputContentItemClasses": ["WFStringContentItem"],
    "WFWorkflowOutputContentItemClasses": [],
    "WFWorkflowTypes": [],
    "WFQuickActionSurfaces": [],
}

out = sys.argv[1] if len(sys.argv) > 1 else "pay-it-forward-contacts.shortcut"
with open(out, "wb") as f:
    plistlib.dump(shortcut, f, fmt=plistlib.FMT_BINARY)
print("wrote", out, len(actions), "actions")
