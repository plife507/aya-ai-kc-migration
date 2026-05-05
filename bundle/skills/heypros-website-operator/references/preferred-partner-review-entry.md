# Preferred Partner Review Entry

Use this reference for KC Preferred Partner review entry in HeyPros.

This file is intentionally operational. Update it as the exact HeyPros UI sequence is discovered.

## Safety rules

- Treat review entry as a production write.
- Never submit a review unless Nathan explicitly approves the specific submission.
- Confirm the source review text/rating and the target job/customer before entering data.
- If using coordinate clicks, record viewport size and capture a screenshot first.
- Prefer stable refs from `snapshot`; use `click-coords` only when refs are absent or unreliable.
- Stop and ask if the screen does not match the expected sequence.

## Source checklist

Before opening or editing the HeyPros form, identify:

- source channel or source record
- customer/job name
- Jobber job number or PO if available
- HeyPros work order/job target if available
- review rating
- review text
- reviewer/customer name
- date of service or review date if relevant
- whether Nathan approved submit or only staging

## Browser setup checklist

1. Choose browser lane:
   - `user` for signed-in HeyPros work
   - `openclaw` only for non-auth checks or if Nathan has approved isolated login work
2. Confirm tab and URL.
3. Capture screenshot before the fragile sequence.
4. Record viewport size if coordinates will be used.
5. Keep the form state visible until verification is complete.

## Known command tools

```bash
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot
openclaw browser --browser-profile user screenshot
openclaw browser --browser-profile user click <ref>
openclaw browser --browser-profile user click-coords <x> <y>
openclaw browser --browser-profile user type <ref> "text"
openclaw browser --browser-profile user press Tab
openclaw browser --browser-profile user wait --text "Saved"
```

## Sequence log

The exact Preferred Partner review click sequence is not locked yet.

When discovered, document it here in this shape:

```text
Date verified:
Browser profile:
Viewport:
Starting URL/page:
Source data required:

Steps:
1. ...
2. ...
3. ...

Coordinate clicks:
- x,y -> purpose -> screenshot filename

Final submit gate:
- exact button/control:
- confirmation text:
- read-back verification:

Failure modes:
- ...
```

## Working draft sequence

Status: pending discovery.

Do not invent this sequence from memory. Capture it from a live HeyPros session with screenshots or snapshots, then update this section.
