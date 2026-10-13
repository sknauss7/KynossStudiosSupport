---
title: It said it was done, and it wasn't
slug: it-said-it-was-done
summary: Claude will tell you the work is finished when it isn't. Here is how we make every "done" pass through something that could have said no.
order: 1
status: published
---
The most expensive word Claude says is "done." It isn't lying. It read the code it wrote, the code looked right, and it believed the code. Most of the time it's even correct, and that's the trap: you stop checking.

I've built fifteen apps with Claude doing the building. Many of the rules we work by now exist because a "done" turned out to be wrong in a way nobody saw at the time. What fixed it each time was the same thing: a check that could have said no, and actually ran.

## Look at the screen, not the code

Claude builds an app by reading and writing text. It never sees the app unless you make it look. So when it says a new screen is finished, what it means is that the code for the screen looks finished.

Screenshots help, with a catch. One of our test runs crashed on launch and still produced a perfectly good screenshot of the phone's home screen. The check only asked whether the image existed, so it passed. Two rounds of automated colour checks then ran against the wallpaper and came back with confident, meaningless numbers.

A picture can also look right and still be wrong. In our party game, the text that tells a blind player what just happened looked fine in every screenshot. A screen reader heard nothing, because that text was hidden from it. Only a check that listens the way a screen reader does could catch that, so now one does.

So the proof that a screen works has to be something only the real, running app could produce: a specific button, a colour in the right place, the words a screen reader actually reads out. A screenshot existing proves nothing.

## Make the new test fail first

The second kind of false "done" is a test that passes no matter what. Claude writes a fix, writes a test for the fix, runs it, and it passes. Nobody asks whether the test would have failed before the fix.

By late August, the notes Claude keeps for itself listed four separate cases of the same mistake: a check that was written, passed, and "would pass just as happily against the defect it names."

One check printed "OK" every time, with the fix in place or ripped out entirely. A version number sent it down a path where it could never report a problem. Its own notes even said it skipped that case. The printout still said everything matched.

So every new test now runs against the broken code first, and it has to fail there. If it passes on the bug, it isn't a test yet. Then the fix goes in and the same test has to pass. If I could keep only one habit from this page, it would be this one.

## Check that the check ran

This is the one that surprised me. A check can be correct, able to fail, and still never run.

In one session Claude added sixteen new checks to an existing tool, proved every one of them could fail, and closed nine pieces of work on the strength of them. Then its own review asked what actually runs those checks. Nothing did. No script and no automated job ever called them.

Test runs mislead the same way. Our party game has a set of slow tests that only run when a switch is turned on. Without the switch they're skipped, and the summary still reports thousands of tests passed. When Claude went looking, seven of the ten passing full runs on the machine had skipped those tests entirely. One session had offered such a run as proof about the very tests that never ran.

It gets simpler than that. Ask for a single test in a form the runner doesn't understand, and it finds nothing, runs zero tests, and reports success.

So a result has to say how many things it checked, and that count gets compared with how many it should have checked. A skip prints "SKIPPED", never "OK". Anything a check can't read counts as a failure.

## The checker was wrong too

The tool Claude built to catch runs that didn't really run was itself wrong on its first real use. Pointed at old logs whose answer was already known, it would have flagged every full run of the game as broken, forever. Its own practice tests had all passed, because Claude wrote them with the same wrong idea of the log format that was in the tool.

That's the honest limit of all this. Claude writes the checks too, and they can share its blind spots. The defence is to point every new check at something whose answer you already know, before you trust it with anything you don't.

## If you build with Claude, try this

- **Ask to see it.** Have Claude open the real app and show you the screen, then look at it yourself.
- **Ask it to break the code first.** A new test should fail on the old code before it passes on the new.
- **Ask how many ran.** "All tests passed" means little until you know the number it should have been.
- **Treat "done" as a claim.** Ask what would have told you if it wasn't.

None of this needs a smarter AI. It needs the habit of asking for evidence, the same one you'd use with a new hire who is eager, fast and a little too sure of themselves.
