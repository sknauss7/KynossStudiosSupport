---
title: It did something I didn't want
slug: it-did-something-i-didnt-want
summary: The real risk is rarely a dramatic rogue AI. It's a quiet step you can't take back, or a tool that did the wrong thing and reported success. Keep the one-way steps for yourself.
order: 9
status: published
---
When people worry about an AI doing something they didn't want, they picture something dramatic. What actually happens is quieter. A script edits the wrong thing, every check passes, and it reports success. Or a step that can't be undone gets taken because nothing said to stop.

You can't make Claude perfect. You can decide which mistakes are allowed to happen without you.

## Decide which steps are one-way

Most of what Claude does can be undone. A bad edit can be reverted, and a wrong screen can be redesigned. A few things can't: sending an app to Apple for release, posting something in public, deleting data, spending money. Those are written into our instructions as the steps where Claude stops and asks.

In practice that means Claude does all the work right up to the button. For a release, it builds the app, uploads it, fills in the store listing, attaches everything, and then stops short of pressing "Submit" and tells me it's ready. Occasionally I hand over the button for one named release, in writing. The default stays the same.

The list is short on purpose. If Claude had to ask about everything, I'd start approving without reading, and the asking would protect nothing. Keeping the list to the steps that genuinely can't be taken back keeps each question worth reading.

## Put the limit in the tool, not the request

Asking Claude to be careful works most of the time. For the things that matter, "most of the time" isn't good enough, so the limit lives in the tool instead.

Our posts on X are a good example. The tool that posts them won't post anything unless I've tapped approve on that exact text, and a changed word means a new approval. It posts at most once a day, it has a hard monthly spending cap, and a single stop file halts all of it. None of those depend on Claude remembering a rule. They're how the tool works.

## Success, reported by the thing that failed

The scarier mistakes are the ones that look like success. Our to-do file holds many separate blocks of work, and each block numbers its items starting from one. A script Claude wrote to mark finished items searched the whole file for the first match.

So four of the seven items it was meant to close landed in an earlier block instead. Someone else's unfinished work was marked done, the real targets were left open, every safety check in the script passed, and it reported success.

It was caught only because the session recounted the block straight after the edit and the numbers didn't match. The fix was structural: edits to the to-do file now go through one tool that finds the right block by name first and refuses an edit that would lose or duplicate an item.

## Failing quietly is its own kind of unwanted

A similar thing nearly happened with a report that checks all our apps in one run. One app's file had a problem, which crashed the whole run partway through. Every app after it was skipped, and every problem the report had already found was thrown away without being printed.

From the outside, that crash looked almost the same as a normal "some checks didn't finish" result. A separate review found it before it did any harm, and now one bad file gets logged as a failure instead of taking the whole report down with it.

## Where it still goes wrong

Keeping the button doesn't mean everything behind the button is right. In one release, Claude built a screen explaining why the app wanted your location, with a "Not now" option that let people skip Apple's own permission request. Apple's rules don't allow that, and the release was rejected.

Nothing irreversible happened. The fix was a single "Continue" button that always leads to Apple's request. The rule about one-way steps did its job, in the sense that nothing was lost and the fixed version went back to Apple the same day. It didn't make the screen right. Keeping those steps for yourself is the floor. You still have to look at what you're approving.

## If you build with Claude, try this

- **Write down your one-way steps.** Releasing, posting, deleting, paying. Tell Claude to stop and ask before each one.
- **Keep the list short.** Ask about too much and you'll stop reading the questions.
- **Build limits into tools.** An approval step or a spending cap beats a request to be careful.
- **Recount after automated edits.** "It said it succeeded" is not the same as "it changed the right thing".
- **Read what you approve.** The button is yours, and so is what it sends.

Claude will do what you ask, and quickly. The steps you can't take back should be the ones it can't take at all.
