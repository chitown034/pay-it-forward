# Pay It Forward Contacts (Apple Shortcut)

Lets iPhone visitors tick several contacts at once. iPhones don't let a web page open Contacts
with checkboxes, so the page's **Choose several contacts** button runs this Shortcut:

1. Contacts opens with checkboxes; the visitor ticks friends and taps Done.
2. For each friend, Messages opens a 3-way text (the friend and Steven, 619-368-7141) with the
   message and the friend's first name filled in. The visitor only taps Send.
3. The Shortcut returns to the Pay It Forward page, which says thank you.

The page passes the message the visitor chose (with `[First Name]` in it) as the Shortcut's input.
Run from the Shortcuts app on its own, it uses the Default message.

## Sign and share it (on a Mac, once)

iPhones only import signed Shortcuts, and signing needs a Mac.

1. On your iPhone, delete the old **Pay It Forward Contacts** Shortcut (it shows "an action could not be found").
2. Download `pay-it-forward-contacts.shortcut` from this folder to your Mac's Downloads folder.
3. In Terminal on the Mac:

   ```bash
   cd ~/Downloads
   ```

   ```bash
   shortcuts sign --mode anyone --input pay-it-forward-contacts.shortcut --output "Pay It Forward Contacts.shortcut"
   ```

4. Double-click **Pay It Forward Contacts.shortcut** and choose **Add Shortcut**. Keep the name exactly
   **Pay It Forward Contacts**; the page runs it by that name. It syncs to your iPhone through iCloud.
5. In the Shortcuts app, right-click it, choose **Share**, then **Copy iCloud Link**. Put that link in
   `SHORTCUT_INSTALL` in `index.html` so visitors see the one-time **Add the contact picker** button.

Current signed version: https://www.icloud.com/shortcuts/4538593acfc94eeb99efc9437f36112e
(set as `SHORTCUT_INSTALL`). If you re-sign it, share again and replace that link.

## Rebuild

`make_shortcut.py` writes the unsigned file:

```bash
python3 make_shortcut.py pay-it-forward-contacts.shortcut
```
