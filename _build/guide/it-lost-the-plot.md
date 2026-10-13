---
title: It lost the plot in a long chat
slug: it-lost-the-plot
summary: The longer a chat with Claude runs, the less of the start it really remembers. We stopped keeping anything important in the chat.
order: 2
status: published
---
A long chat with Claude feels like progress. You've explained the app, agreed on a plan, fixed a dozen things together. It feels like Claude knows the project as well as you do.

It doesn't, and it knows less the longer you go. Claude works from a fixed amount of working memory. When a conversation outgrows it, the older parts get squeezed into a summary to make room. The decision you made two hours ago survives as a sentence. The reason behind it is gone, and so is the thing you tried first that didn't work. So Claude cheerfully tries it again.

## What a long chat did to us

We learned this the expensive way. For a while, I ran our whole to-do list for the apps in one long conversation per batch of work. Again and again it ended the same way: the chat filled up, Claude summarized itself to make room, then had to do it again, and again, until the session fell over.

From the outside it didn't look like a crash coming. It looked like Claude getting a little forgetful, then a little repetitive. It would re-check something it had already checked, or ask a question I'd answered an hour earlier. Each slip was small enough to shrug off, and by the time they added up, the session was already gone.

One died in the middle of a big batch of changes with 34 files edited and not yet safely put away. Nothing was lost for good, but someone had to work out what those changes were, who made them and whether they were finished. That someone was a fresh Claude, reading the files cold.

## Small blocks, written down

So the work moved out of the chat and into a file. Each piece of work is a written block: what it's for, the list of things to do, and what "finished" means. Claude takes one block, works it, and stops. Then I clear the chat, and the next session starts from the file instead of a fading conversation.

Writing down what "finished" means turned out to be the important part. Without it, Claude decides for itself when a job is done, and a tired session at the end of a long chat is generous about that. With it, there's a list to check against, and anyone, including the next Claude, can tell whether the block really is done.

The stop is a numbered rule in the instructions, with no exceptions written into it: tell me the block is finished, then wait for a fresh start before touching the next one. Giving the stop a name matters more than it sounds. Skipping it stops being a judgment call and becomes breaking a rule, and Claude is much better at following rules than at judging when to stop.

## Write the state down, not the story

The first version of this still went wrong, in a quieter way. Each session left a note at the top of the file for the next one, a "start here" message in plain prose. The notes read well. They also went stale fast, because a note describes the moment it was written, and the next session would change things without updating it.

Now each session writes a record instead: what it finished, what it changed, and the checks it ran, with their results captured by the tool rather than typed by hand. And a note is never allowed to hold a number. If the next session needs to know how many things are left, the note holds the command that counts them, so the count is always fresh.

The idea underneath both rules is one line in our instructions: a number, a list or a banner is a claim about the code, and it goes stale the moment someone changes the code.

## When the session dies anyway

This doesn't make sessions immortal. They still run out of room, or hit the usage limit halfway through a block. When that happened, a dead session left its work marked as "in progress", and the next session politely skipped it, because someone else was clearly on it. Nobody was.

The fix was boring: a check at the start of each session for claims whose owner no longer exists, and any unsaved work from the dead session gets saved as a file before anyone touches it. The written blocks made that possible. A conversation that dies takes its plan with it. A file doesn't.

## If you build with Claude, try this

- **Keep the plan in a file.** Ask Claude to update it as it works, and to read it first when a new chat starts.
- **One job per chat.** When the job is done, start a new conversation and point it at the file.
- **Ask for a handoff note.** What's done, what's next, and what still hasn't been checked.
- **Don't trust a number in an old note.** Ask Claude to count again.

The chat is a great place to think out loud. It's a terrible place to keep anything you'll need tomorrow.
