---
title: It burned through my usage limit
slug: it-burned-through-my-usage-limit
summary: Most of what eats a usage limit is text nobody typed. Measure what Claude is actually reading before you try to cut it.
order: 8
status: published
---
Most advice about usage limits is about you: write shorter messages, ask for less. That advice missed almost all of our problem. The biggest cost in our sessions was text nobody had typed in weeks.

The arithmetic is simple. Every time Claude answers, it rereads everything it's holding: the whole conversation so far, plus any instruction files that load on their own. So the real cost of a session is how much Claude is holding, multiplied by how many times it answers. A file that sits quietly in every session costs you on every single reply.

## Measure before you cut

We couldn't fix what we couldn't see, so Claude built a tool that reads our session logs and splits the total by where it came from: the conversation, files Claude opened, instruction files that loaded automatically, and so on. Seeing the split for the first time was the useful part. It turned "we're using too much" into a short list of specific things to fix.

Even that took care. The logs repeat each reply's usage once for every piece of the reply, so the obvious way of adding them up counts everything about twice. A measuring tool that's wrong by a factor of two will send you chasing the wrong things with total confidence.

## The file nobody typed

The first thing the tool found was the biggest. Our party game had an instruction file that loaded automatically into every session that touched the game. Over months it had grown into a huge rulebook, every lesson the project had ever learned, all in one place.

On its own it accounted for somewhere between a third and nearly half of everything Claude read across all our work. Nobody had noticed, because nobody ever typed it. It was just there, every time.

Nothing about it looked expensive from inside a session. Claude never mentioned the file, and it never showed up in the chat. The only symptom was that the limit arrived sooner than it should have, which is easy to blame on yourself and your long questions.

We cut it down to a short core, the rules that matter on every task, and moved the rest into separate files Claude opens only when a task needs them. Its share of what Claude read fell from 46.8% to 3.1%.

## Finished work still costs

The second find was quieter. Our to-do list keeps each piece of work as a written block, and a long-running block collects notes as items get done. Every session that opened the block read all of it, including the parts that were finished weeks earlier.

One block had grown to 152,100 bytes, most of it work that was already done. We started moving finished items out to an archive, leaving a one-line pointer behind, and the block dropped to 12,119.

There's a trap in that fix, and we wrote it into the rule. Moving finished work out of sight must never look like progress. The counts still include the archived items, so the tidy file can't pass itself off as a shorter to-do list.

## The notes that were too big to read

The same thing had happened to Claude's own notes. Every lesson learned had gone into one long file, and the instructions told Claude to read the whole thing at the start of every session, before doing any work at all. By the time we split it up, it was 11,615 lines long, and every session paid for every line before it wrote one of its own.

Now each lesson is its own small file, tagged by app and topic, and Claude searches for the handful that match the job instead of reading all of them. Nothing was thrown away. The cost of carrying it all is a sliver of what it was.

## Where it still goes wrong

Measuring tells you where to cut. It doesn't stop the limit arriving. Sessions still hit it in the middle of a job, and when they do, they leave work half-claimed for the next session to untangle. A smaller session dies less often. It still dies.

## If you build with Claude, try this

- **Keep always-loaded files short.** Anything that loads into every session is paid for on every reply. Put the detail in files Claude opens when it needs them.
- **Start fresh chats.** A long conversation is reread every time Claude answers.
- **Move finished work out of the way.** A file full of completed tasks still gets read.
- **Look before you cut.** If your tools can show what's filling Claude's memory, check that first. The biggest cost is rarely the one you'd guess.

Usage limits feel like a tax on asking for things. In our case, most of it was a tax on things we'd stopped looking at.
