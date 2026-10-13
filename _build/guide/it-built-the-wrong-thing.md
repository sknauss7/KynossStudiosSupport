---
title: It built the wrong thing really well
slug: it-built-the-wrong-thing
summary: Claude will build whatever you describe, beautifully, including the thing that can't work. Test the risky idea with a real experiment before any app gets built.
order: 4
status: published
---
Claude never pushes back on an idea because it's hard. Describe an app and it will start building, and it will build well: clean screens, careful code, every feature you asked for. That's exactly the risk. If the idea at the heart of the app can't work, you get a polished version of something that can't work, and you find out after the polish.

So before any of our apps gets built, the riskiest claim it depends on gets tested with a real experiment. Before that experiment runs, we write down the number it has to hit. If it misses, the app doesn't get built.

## The scam checker

One idea was an app that reads a conversation with a stranger on a selling site and warns you if it looks like a scam. The pitch was that the AI built into the phone would judge each conversation. It sounded right, and it sounded like exactly the kind of thing AI is for.

Before any app code, Claude ran the experiment. It wrote a set of example conversations, half of them scams and half of them innocent, and set the bar in advance: at least 85% of conversations judged correctly, with false alarms under 10%.

The important half was the innocent one. Those conversations were written to look suspicious on purpose, with payment app talk, requests to hold an item, urgency about shipping. That's what real, harmless buyers sound like, and an app that cries wolf at them is useless.

The result flipped the plan. A plain list of known scam patterns caught every scam with no false alarms at all. Letting the phone's AI make the call raised false alarms on half the innocent conversations.

Simply asking the AI "is this a scam?" was worse still. It flagged 75% of the innocent ones. The AI idea at the centre of the pitch was the wrong design, and that was clear the same day instead of after an app was built around it.

The report was honest about its limits, too. Claude had written the example conversations itself, so the exact numbers weren't a promise about the real world. The shape of the result was what mattered. In the end, what was left after the experiment was thin, and I killed the app before it was built.

## The idea that looked great on paper

Another idea was a sleep app that listens overnight and tracks teeth grinding. On paper it scored 26 out of 30 on our idea checklist. It had never been tested against reality.

The check asked a simple question: what would it learn to recognise grinding from? There was no usable collection of labelled overnight recordings at a scale we could get. And clenching, one of the things the app promised to track, makes no sound at all, so a phone on the nightstand can't hear it.

That check was mostly research rather than a running experiment, and it was enough. The honest version of the app would have tracked about half of what it promised. It was killed before anything was built.

## What skipping the check costs

The check only helps if it's actually run. Two of our apps show what happens otherwise.

One app read itemised medical bills and pointed out likely errors. It was built and reached beta testing, and the one claim everything depended on, that it actually finds errors on real bills, was never tested. Another app had both of its checks waived instead of passed, and its launch steps then sat untouched for months. Both were well built. Both were killed later, when someone finally asked the questions the checks would have asked at the start.

Neither was a failure of Claude's work. The screens were fine and the code was careful. Claude did exactly what it was asked, and nobody had asked whether the thing was worth doing. That question is yours. Claude will answer it if you ask, but it won't raise it on its own.

## If you build with Claude, try this

- **Name the riskiest claim.** What has to be true for this app to be worth anything? Ask Claude to say it in one sentence.
- **Test that claim first, without building the app.** A rough experiment in a day beats a beautiful app built on a guess.
- **Write the pass mark before you run it.** Decide what "good enough" means before you see the result, so you can't talk yourself into it afterwards.
- **Test the innocent cases.** Anything that judges or detects needs examples designed to fool it, not just easy ones.
- **Treat "we skipped the check" as "we don't know".** A waived test is not a passed one.

Claude can build almost anything you ask for. Make sure the thing you're asking for can work before it does.
