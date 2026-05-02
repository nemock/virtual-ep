# EP001 — Raw Transcript

Provider: whisper-local. Generated 2026-05-04 16:42 PT. Word count: ~1,400 (abbreviated for the example — a full episode would be ~6,000–8,000 words).

---

[00:00:00] HOST: All right, welcome back. I'm your host, and you're listening to the show. Big week. Like, really big week — two things happened that I don't think anyone is connecting yet, and I want to talk about both. Anthropic shipped Opus 5 on Tuesday, Spotify reported Thursday, and the stock popped. And, um, the story everyone's writing about both of these is wrong. Or, not wrong, just — surface level. So let's get into it. My co-host is here. How are you?

[00:00:34] COHOST: Doing well. Two big moves this week — Anthropic shipped Opus 5 and Spotify reported. Where do you want to start?

[00:00:42] HOST: Anthropic. Let's start there because everyone's going to expect us to. Opus 5 dropped Tuesday morning, you know, with a benchmark — LongBench-2 — and they cleared 90 percent. First model to do it. The benchmark just came out, like, a month ago, and nothing else was above 86. And so the headline is, you know, "Anthropic takes the lead." Fine. That's true this week. It's been true four other times in the last two years and it'll probably stop being true next month when OpenAI ships something. The actual story is what they shipped alongside it, which nobody is talking about.

[00:01:24] COHOST: You mean Sonnet 5?

[00:01:26] HOST: Sonnet 5. Yeah. They quietly released a new Sonnet variant the same day, priced 40 percent below the prior Sonnet. Forty percent. That's the move. Because, like, if you actually run an enterprise AI workload, you're not running it on Opus. You're running it on Sonnet. Sonnet's the volume play. And they just dropped the price 40 percent on it. And, um, what they're telling you when they do that is — they think inference cost is going to keep collapsing and they want to be the cheap-and-good API before OpenAI gets there. Opus 5 is the optics. Sonnet 5 is the actual move.

[00:02:08] COHOST: Right. If Sonnet is the volume play, though, why announce Opus 5 first? Why not just lead with the cheaper, better Sonnet?

[00:02:18] HOST: Because frontier models are how you stay in the conversation. You know, like — if you're not on the bench leaderboard, the AI Twitter discourse forgets about you. You can't ship just commodity products and stay relevant. So they need the flagship. But the flagship doesn't drive the revenue. The flagship drives the perception, and the perception drives the enterprise sales team's ability to walk into a room and say "we have the best model." Then in the room they sell you Sonnet because nobody can afford Opus at scale. It's, like — Intel did this for a decade with the high-end Xeons. Same playbook.

[00:02:58] COHOST: OK, and on pricing — they held the input price flat but raised output 12 percent. What's the read?

[00:03:06] HOST: That's interesting. Holding flat is a confidence signal. Like, they could have raised it. They have the only model on the new bench. Demand is there. Holding flat means they're, you know, betting that compute costs are coming in line and they don't need to extract every dollar today. The 12 percent output bump is small. But it's signaling. They think the next year is about agents, about long generation, about workloads that produce a lot of tokens, and that's where they want margin. Input is going to commoditize. Output, they think, has more pricing power because there's, like, value-add in what gets produced.

[00:03:48] COHOST: Got it. Let me push back on something. The contrarian read on Opus 5 — that it's noise and Sonnet's the signal. Like, isn't the real play just that they're hedging? They don't actually know which one wins?

[00:04:02] HOST: Maybe. But the way they're hedging tells you what they expect. If they thought Opus was the future they'd have priced Sonnet as a downstream product. Instead they're underbidding their own Sonnet. They're saying — we expect this layer to commoditize, we want to be the default cheap-and-good option, and we'll let the flagship sell itself on benchmarks. Dario said the line — "models are moving from products to commodities." He said it four times in one interview. Four. That's not a guy who's hedging. That's a guy who's signaling.

[00:04:38] COHOST: Yeah. Models are moving from products to commodities.

[00:04:42] HOST: Right. And so if you're an enterprise buyer right now, the read is — don't lock in. The Opus 5 is exciting but the real move is the Sonnet 5 price drop, and there's going to be another one in three months from one of these labs. The procurement decision today should be optionality, not loyalty.

[00:05:02] COHOST: All right, hold that thought. Different kind of commoditization story playing out in audio this week. Spotify reported Thursday. Stock popped. What did you see in the call?

[00:05:14] HOST: OK so this is actually my favorite story of the week, because the headline is — podcast ad revenue up 28 percent year over year, beat consensus by 6, stock up 11 percent the next morning. Great quarter. And every write-up I've read is saying, like, "podcast ads are back." That's wrong. This is not a podcast story. This is a programmatic-buying story. Spotify finally finished building the stack that makes audio inventory addressable, and the 28 percent is the result of that, not the cause.

[00:05:48] COHOST: What's the evidence?

[00:05:50] HOST: Their developer numbers. Spotify Audience Network — that's their programmatic ad API — hit 4.2 billion requests in March. Year ago it was 1.8 billion. So API request volume more than doubled in twelve months. That's where the growth is. Advertisers are buying audio inventory at scale, programmatically, the way they buy display. They're not picking shows anymore. They're buying audiences. And, um, you know, that's a totally different game than "we have Joe Rogan."

[00:06:24] COHOST: Right. And speaking of — I saw the $200M write-down on the exclusive deal embedded in operating expenses?

[00:06:32] HOST: Yes. Yes. So this is the part nobody's talking about. They wrote down 200 million dollars on a podcast exclusive deal this quarter. Buried it in the OpEx line, did not call it out separately. This is the third write-down on a single deal in eighteen months, by the way. And meanwhile, in the same call, Daniel Ek says — and I quote — "we're not in the content business, we're in the routing business." Said it three times. The exclusive deal era is dead. They're done with it. The strategy is programmatic audio. Routing.

[00:07:08] COHOST: And meanwhile MAU growth slowed to 9 percent.

[00:07:12] HOST: Yeah. Slowest in three years. The user growth story is over. The story is monetization. And the way you monetize is, you double the ad load on the free tier — which they did, twelve months — and you build the programmatic stack to absorb the inventory at scale. And, like, the fact that doubling ad load didn't crater free-to-paid conversion is the most underrated number in this earnings report. People are putting up with twice as many ads. That's the move.

[00:07:48] COHOST: Apple's audio ad business — are they about to copy this playbook?

[00:07:53] HOST: Two quarters away. Maybe one. They've been hiring programmatic ad people for six months. Quietly. They have the inventory — Apple Music, Apple Podcasts — and now they have a working playbook from Spotify. The "Spotify wins audio" story has, like, an 18-month shelf life max before Apple shows up. So if you're Spotify, you have a window. Use it.

[00:08:22] COHOST: OK. Last item. OpenAI cut Plus pricing 20 percent on Friday. Reaction or strategy?

[00:08:28] HOST: Strategy. Or — defensive strategy. Same thing. So $20 down to $16, three days after Anthropic ships Opus 5 and the Sonnet 5 price drop. This is not a price war. This is a churn defense. Plus subscriber count was, you know, leaked at 18 million last quarter. The math: 20 percent cut on $20 across 18 million subscribers, that's $80 million a month off the top line.

[Transcript continues for approximately 30 more minutes — abbreviated for example purposes.]
