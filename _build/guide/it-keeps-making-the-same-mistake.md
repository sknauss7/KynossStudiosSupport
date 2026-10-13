---
title: It keeps making the same mistake
slug: it-keeps-making-the-same-mistake
summary: Claude starts every session knowing nothing about your last one. A lesson only sticks if it's written where the next session will actually read it.
order: 3
status: published
---
You fix something with Claude, explain what went wrong, and it says it understands. A week later it makes the same mistake, in the same way, with the same confidence.

It isn't being stubborn. Each new session starts with no memory of the last one. Whatever Claude learned yesterday is gone unless it was written down somewhere, and even then it only helps if the new session reads it at the right moment. Most of our work on this problem has been about that second part.

## Make the retro impossible to skip

The first rule was simple. Every finished piece of work ends with a short note: what went wrong, what was harder than expected, and what the next session should know. The notes were supposed to feed a growing file of lessons.

Claude kept skipping it. The work was done, the notes felt optional, and it archived the work without writing them. Asking more firmly didn't help.

So the archiving tool now refuses to run until the notes exist. "None" is allowed, but it has to come with a reason. That one change did more than any amount of asking, because it moved the rule out of the instructions, where it can be forgotten, and into the tool, where it can't.

## A lesson nobody reads is no lesson

The notes piled up. For months they lived in one long file that Claude was told to read at the start of every session, and by the time we changed it, it ran to 11,615 lines. Reading all of it was expensive, and worse, it didn't work. A rule buried thousands of lines deep doesn't come to mind at the moment it matters.

Now every lesson is its own small file, tagged with the app, the kind of work and the topic. At the start of a job, Claude searches for the handful that match and reads only those. There are 1007 of them, and a typical search returns a short list worth reading closely.

## Write it where the next worker looks

Even a well-filed lesson can miss. Here's the one that taught us that.

When Claude starts a long job in the background, it often leaves a small helper running that waits for the job to finish. One common way to write that helper has a flaw: it searches for the job by name, and it finds its own name, so it waits forever. One session found three of these helpers that had been waiting on nothing for 8.5 hours.

We wrote it down. It came back anyway. In a later session, the Claude handing out work to other Claude sessions wrote the broken pattern into two of their instructions itself, even claiming a small change made it safe. It didn't. One of those sessions stacked up three more stuck helpers, and I flagged the same problem for the third time.

The note existed. It just wasn't in the place the next worker read. So the instructions each helper session gets are now generated from a shared file of known hazards, instead of written fresh each time, and that file carries the safe way to wait.

## Some repeats are beliefs, not bugs

Not every repeated mistake is code. Sometimes it's a sentence. Three open questions about how our party game balances its scoring were put off for eighteen days, three separate times, with the same explanation: these can only be settled by watching real people play.

When a session finally checked that sentence against the game's actual code, it was false for two of the three. The answers were sitting in numbers the game already had. Each deferral had copied the excuse forward instead of testing it, so now an excuse like that is treated as a claim with an expiry date, and it gets checked again before it can be used to put something off.

## Where it still goes wrong

Writing lessons down creates a new place for mistakes to hide: the write-up itself. In one review, the closing summary of a piece of work turned out to contain nine claims that the code contradicted, each one describing more than the work had actually checked. The summary is the part people read, and it was the part nobody had checked.

## If you build with Claude, try this

- **End every task with a short note.** What went wrong, and what the next session should know. Keep it in a file in your project.
- **Make the note hard to skip.** A checklist item Claude must tick before it calls the work done beats a polite request.
- **Keep lessons small and findable.** One topic per note, so you can point Claude at the three that matter.
- **Put the warning where the work starts.** If you hand Claude instructions for a task, the relevant warning belongs in those instructions.
- **Recheck old excuses.** "We can't know that yet" deserves a second look before it buys another delay.

Claude doesn't learn between sessions. Your project can, if what you learn lives in it.
