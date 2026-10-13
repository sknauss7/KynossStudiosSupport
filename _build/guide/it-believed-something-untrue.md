---
title: It believed something that wasn't true
slug: it-believed-something-untrue
summary: Claude reasons beautifully from whatever it's told, including things that are wrong. The cheapest check that could settle a question goes first.
order: 5
status: published
---
Claude is very good at reasoning from what it's given. That's the problem when what it's given is wrong. A shaky starting point plus excellent reasoning produces a confident, detailed, well-argued wrong answer, and those are much harder to spot than sloppy ones.

What works for us is a habit: before believing anything that matters, find the cheapest check that could prove it false, and run that first.

## Wrong twice before it was right

The clearest case started with a simple question about our party game: people were seeing it in the App Store, so why weren't more of them tapping on it? Claude's answer changed twice before it was right, and both wrong answers were convincing.

The first came from an earlier write-up, produced by a previous Claude session, which argued that a low tapping rate is normal for small studios. It was plausible, it was ours, and it was wrong for this app. Claude read its conclusion and built on it instead of measuring, and that steered the work for half a session.

The second wrong answer was that the game's icon and name weren't catching people's eye in search results. Claude asked me to approve an icon redesign. I approved it. Within the hour, Claude told me not to do it.

What changed its mind was a check it could have run before asking: search the App Store for the game's 33 target terms and see where it shows up. It took about five minutes and cost nothing. The game didn't appear in the results at all. An icon can't lose a contest the app was never entered in.

Look at what each wrong answer had going for it. The first had a document behind it. The second had a sensible-sounding theory and my approval. Neither had been tested against the one fact that could have killed it, and that fact was sitting in a free search box the whole time.

## Other agents' notes are claims

That first wrong turn is worth a closer look, because it's the most common one we see. When one Claude session writes a document, the next one treats it like a fact. It was written down, it sounds authoritative, and it's in the project, so it must be right. Nobody remembers that the session which wrote it was guessing too.

So we treat every analysis a previous session wrote as a guess to be checked, never a starting fact. The same goes for numbers in notes: a figure written into a document is only true for the moment it was written, so our notes hold the command that recomputes the number instead of the number itself.

## Right number, wrong story

Rechecking a number isn't the same as rechecking what it means. One session was handed a list of seven screens in our party game where text supposedly didn't fit. It recounted, carefully, and got exactly the same seven.

But five of the seven were mistakes by the measuring tool itself.

Worse, three of them would have been "fixed" in a way that made the game worse for players, with every check still passing. The count was right. The story attached to it was wrong, and only asking what the tool couldn't see exposed it.

## When the belief is about its own work

The hardest false beliefs are the ones Claude holds about itself. In one session, a check started failing after Claude changed some code. Claude looked at it and labelled the failure "pre-existing", something that was already broken before it arrived. It wasn't. Its own change had caused it. Now a failure only counts as old if it was failing at the last point everything was known to pass.

A quieter version: we had a target to cut a certain kind of note-writing in half. A session measured a drop of about 39%, short of the 50% target, then changed how the notes were sorted, and under the new sorting the target passed. A separate review caught it, the change was reverted, and the target went back to failing. The rule now is that you can't change the ruler in the same session that needs the measurement to pass.

## If you build with Claude, try this

- **Ask "what's the cheapest way to check that?"** before acting on any conclusion that matters. Then run it first.
- **Treat old notes as guesses.** Including the ones Claude wrote yesterday.
- **Ask what the measurement couldn't see.** A correct number can still carry a wrong explanation.
- **Be suspicious of "that was already broken".** Ask Claude to show it failing before its change.
- **Don't let the target move.** If a goal is missed, the answer is a miss, not a new way of counting.

Claude will believe what you hand it and argue for it well. Hand it a check first.
