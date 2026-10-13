---
title: Running several agents at once made a mess
slug: running-several-agents-made-a-mess
summary: Several Claude sessions working side by side can do a day's work in an hour, or wreck each other's work in a minute. Each one needs its own space and the warnings that come with it.
order: 7
status: published
---
Once one Claude session works, the obvious next step is to run several at once. One fixes a bug, another reviews yesterday's changes, a third tests a different app. On a good day it really is like having a small team.

On a bad day it's like having a small team in one tiny kitchen. They share one computer, one disk and one set of test devices, and none of them knows the others exist. Every mess we've had from running several sessions at once came from something they shared without knowing it.

## The copy that filled the disk

The worst one took a few minutes. Six sessions were reviewing work in parallel. One of them only needed to compare two versions of our party game's project, a read-only job. To do it, it copied the whole project folder into scratch space.

That folder holds a large archive of saved screenshots and test evidence, so the copy wrote 11GB and filled the disk. Every session in the batch died, along with a long web test run that had 255 checks passing at the time. Nothing from that round of work could be recovered.

The warning already existed. It was printed for the session handing out the work, which never copies anything. The session that did the copying never saw it. Now every helper's instructions carry the rule directly: never copy the project folder. Helpers get a sandbox instead, a lightweight stand-in made of links back to the real files, so they can read everything and change only their own small corner.

## Check while it runs, not before

Before that, we checked free disk space when starting a batch of helpers. The disk was fine at the start every time. It filled up in the middle, while helpers were busy making copies, and it happened twice before the rule changed. Now the free space gets checked again after the helpers are running.

The same thing happened with memory. Helpers and other sessions were all building and testing apps at the same time, with 11 app builds running together. Each one looked modest on its own. Nobody was adding them up.

The computer ran out of memory and started using the disk as overflow, and free disk space fell from 28GB to 306MB. No folder explained it, which made it maddening to find. Builds now take turns through a shared lock.

## Two sessions, one test phone

Our apps get tested on virtual phones running on the computer. When two sessions used the same virtual phone at once, the results went strange in ways that didn't look like a clash. In one run, a set of tests reported that it had passed while running nothing at all, and another set printed no result whatsoever.

Nothing about those results said "someone else is using this phone". They looked like ordinary bugs, so they cost real time to chase, and a passing result that ran nothing is the worst kind of wrong. Now each session borrows a private virtual phone of its own and gives it back when it's done, and there's a hard cap on how many can run on the machine at once.

## Same name, same mess

Even the sandboxes needed a rule. Two helpers were once given the same sandbox name, so they ended up working in the same space, and one destroyed the other's run partway through. The sandbox tool now refuses to create a sandbox whose name is already taken, and each helper's name includes a few random characters.

## Where it still goes wrong

More sessions isn't more speed past a point. The computer is shared, and every extra helper adds to the pile of things that can collide. Each of the rules above was written after a collision, which means the next collision is probably one we haven't had yet.

Our working rule now is one job per helper, with instructions generated from a shared list of known hazards rather than typed fresh each time. The coordinator writes only what's new about the job. The warnings come along automatically, so a helper can't miss one because somebody forgot to mention it.

## If you build with Claude, try this

- **Give each session its own space.** Its own folder or copy of the project, never a shared one, and never a full copy of something huge.
- **Put the warnings in each session's instructions.** A warning only the coordinator sees protects nobody.
- **Share devices one at a time.** If two sessions test on the same phone, expect nonsense results.
- **Watch the machine, not just the work.** Check disk and memory while the sessions run, not only before.
- **Start with fewer.** Two well-briefed sessions beat six that trip over each other.

Parallel sessions multiply what you can get done. They multiply the collisions too, unless each one knows where its edges are.
