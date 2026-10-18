# Research: Start With the Problem, Not the Tool (ចាប់ផ្តើមពីបញ្ហា មិនមែនពីឧបករណ៍)

As of 2026-10-14 · Source: topic line only, no article ("Implementing practical AI in a company requires starting with clear business problems rather than chasing technology. A step-by-step framework helps bridge strategy, data, and people") · Origin: no single source; a synthesis of RAND (2024), MIT NANDA (2025), BCG, Microsoft and Progress Software guidance, and the named cases below (see Origin trail)

## The heart

This is a story about the person nobody stood next to. An airline's chatbot told someone whose grandmother had just died one thing, and the airline's own web page said the opposite. A bank-sized software launch made headlines and then quietly went back to hiring people. A school asked for facial recognition and what it actually had was a paper sign-in sheet. Each time the technology was not the failure. Nobody had stood beside the person with the problem and asked what hurt. The viewer is a Cambodian owner, manager or employee who is told every week to "do AI". They should leave calm and capable: you do not need to chase anything. Look at what hurts in your own work, check that you have the real records, and bring the people who do the work with you.

Proposed title (untested, needs a native read):
- Main, search-friendly: «អេអាយក្នុងក្រុមហ៊ុន ចាប់ផ្តើមពីបញ្ហា មិនមែនពីឧបករណ៍» / "AI in a company starts with the problem, not the tool"
- Feeling-led alternative for the thumbnail or a second cut: «មុនពេលទិញអេអាយ សួរខ្លួនឯងសិនថា អ្វីដែលពិបាកបំផុតក្នុងការងាររបស់អ្នក?» / "Before you buy AI, ask what is hardest in your work"

Target length 7½–8½ minutes (my default; change it if you have another length in mind).

Four things the dossier keeps honest, so the film can stay warm without misleading anyone:
- **There is no single failure rate.** The famous "80%" reached RAND through a 2022 Fortune interview with an AI vendor's CEO, and RAND hedges it with "by some estimates". MIT's "95%" is a preliminary study of 52 organisations and mixes two denominators. Other surveys say 5%, 25%, 42% or nearly 75% succeed or fail, depending on what they ask. The script shows what each number measures and never states one rate as fact (see "The honest number line").
- **The framework is ours.** I found nothing that uses the "bridge strategy, data and people" wording. The three bands and eight steps below are a synthesis: every step cites a source, and the grouping and wording are marked as ours. It is a way of thinking, not a proven recipe. All the underlying evidence is interviews or self-reported surveys of mid-size and large organisations, and none studied very small businesses.
- **Cambodia: strong on the baseline, thin on stories.** One good survey (273 registered manufacturers) says the real bottleneck is paper records and untracked numbers, not AI. I found three Cambodian problem-first examples, but none has a published result and none gives a named owner's voice. I found no Cambodian or Southeast Asian project that failed by chasing technology, and I did not invent one. A real Cambodian owner or manager, interviewed or quoted, would beat any foreign case for this audience.
- **The hero story is a chatbot, not "AI".** The decision says nothing about what kind of chatbot it was, and the conversation happened on 11 Nov 2022, nineteen days before ChatGPT was released. The script says "ឆាតបូត" (chatbot), never "generative AI".

### Origin trail

- **No single article.** Searches for the topic's wording found only the nearest relatives:
  - Progress Software, Willy Muteba, "From Waste to ROI: A Problem-First AI Framework", 23 Mar 2026: the "Why Audit" (can you describe the problem without the words AI, machine learning or LLM?), then data realism, then a human-in-the-loop check [3][4].
  - Microsoft Cloud Adoption Framework, AI strategy (page dated 9 Oct 2026): step one is literally to start with business problems "before you consider AI at all" [20].
  - HBR, Israeli and Ascarza, "Most AI Initiatives Fail. This 5-Part Framework Can Help", 20 Nov 2025: closest phrase to the topic line ("bridge technical potential and business impact"), but only the teaser is readable [22].
  - Google Cloud AI Adoption Framework (30 Jun 2020: people, process, technology, data) [21] and BCG's 10-20-70 rule (first verifiable on BCG's Oct 2024 press release; no page shows how it was derived) [14].
- **The research anchors, and how the famous numbers travel.**
  - Jul 2022, Fortune, Jeremy Kahn, profiling Aible's CEO: leaders put AI failure at 83% to 92% in unnamed "recent surveys" [2].
  - 13 Aug 2024, RAND (Ryseff, De Bruhl, Newberry): borrows that "more than 80 percent" with "by some estimates", then interviews 65 data scientists and names five root causes [1].
  - Jul–Aug 2025, MIT NANDA "The GenAI Divide" (Challapally, Pease, Raskar, Chari): the contested 95% [5].
  - Andrew Ng's AI Transformation Playbook, Dec 2018, is the older ancestor of the "start with a small pilot" advice [18].
- **The people stories** come from primary documents where I could read them: the tribunal decision, Klarna's own press release, the UT System audit through Medscape and Network World, STAT, the Kaiser and AMA pages, and the Google/Thailand papers. Bloomberg's Klarna interview was blocked, so its quotes were checked across three secondary copies.
- **Into Khmer.** I found no Khmer article that explains problem-first AI adoption for business. Khmer business media (Sabay, Fresh News, DAP News) write "AI" in Latin letters far more than the Khmer word (89 uses against 16 in eight pages). Facebook and YouTube were not searched.
- **Method note.** `scout.py search` often returned nothing and many hosts refused connections (gartner.com, bcg.com, mckinsey.com, bloomberg.com, canlii, kas.de, NEJM). Agents used WebSearch and WebFetch as fallbacks, and those return small-model summaries, so the numbers that carry weight were re-checked against saved primary pages (the Moffatt decision, Klarna's release, RAND, MIT, Progress, the KAS survey text). Anything still resting on a summary is marked "verify".

## Story spine

1. **Hook (first 60–75 seconds): a message on the day a grandmother died.** 11 Nov 2022. Jake Moffatt opens an airline's website to book a flight and asks the chat window about a discount for people who have just lost a relative. Our own chat window types the answer: buy now, apply for the reduced fare within 90 days. Then the airline's own policy page slides in underneath and says the opposite. The airline refuses the refund, admits in writing that the chatbot used "misleading words", and still makes a person with no lawyer take it to a tribunal. The airline sends an employee. The airline's defence is that the chatbot is a separate legal entity. The tribunal calls that a remarkable submission and orders the airline to pay CAD 812.02. *Feeling: tender, quiet outrage; small amounts, big grief.* [6][7]
2. **The pressure: everyone says you must.** Managers feel pressure to "do something, anything, with AI" (RAND). 64% of 2,000 CEOs say fear of falling behind makes them invest before they understand the value (IBM). Then Cambodia: of 273 registered manufacturers phoned in December 2025, more than half track no business number at all, about two in three run on phone, email, social media and paper, and only about one in three feel pressure from competitors. If you have not started, you are not alone. *Feeling: relief.* [1][12][8]
3. **What goes wrong when you chase the tool.** Klarna's 2024 boast (2.3 million chats, "equivalent work of 700 agents") and its 2025 U-turn: the CEO says cost was too predominant and quality fell, humans are hired back, and it begins recruiting its own most passionate customers to work part-time in service. The RAND price example: leaders ask for the price that sells the most, but they need the price that earns the most. The Kinshasa school that asked for facial recognition and had a paper problem. Then the honest number line: different studies, different questions, no single failure rate. *Feeling: a wry smile, then care.* [9][1][3][5]
4. **The turn: three questions.** A napkin version of the eight-step framework, with one real person in each band: *what hurts* (the Kinshasa fix; Kaiser's doctors writing notes at night), *what do we truly know* (RAND's "weekly sales reports are not the data a model needs"; Calmette Hospital being honest that it only had lab results), *will people use it and trust it* (the Thai eye-screening nurses; Kaiser's doctors review every note; the lawyer who chose a $20 chatbot over a $50,000 tool). Then: test small, watch one number, keep, fix or stop. *Feeling: clear, calm, constructive.* [16–19]
5. **Home: Cambodia.** The survey authors' own conclusion that pushing AI ahead of basic systems is "premature", and what they recommend instead (free accounting, stock and order tools first; AI taught in Khmer, tied to tasks firms already do). Three Cambodian starts, labelled for what they are: a hospital tool with no published result, a cashew-farmer chatbot on Telegram at an early stage, a bank's own usage numbers. *Feeling: warm, local, honest about the thin evidence.* [10][11]
6. **Ending: the line the viewer remembers.** AI does not know what hurts. Only people do. Close on a calm screen with one question left on it (what is hardest in your work?), then back to Jake, with the last line: may someone always stand next to the person with the problem. *Feeling: a quiet lump in the throat that turns into resolve.*

## Moments

Best first. "Words only" means we paraphrase and credit; we do not use their audio, footage or logos.

1. **The chatbot against its own page, and the employee sent to the tribunal.** The decision (2024 BCCRT 149, paras 2, 13–22, 27–28, 44): the grandmother died 11 Nov 2022; the chatbot said to request the reduced fare within 90 days; the page it linked said that refunds do not apply after travel; the first application went in on 17 Nov, six days after the death; on 8 Feb 2023 an airline rep admitted the chatbot gave "misleading words"; Moffatt was self-represented and the airline was represented by an employee; the tribunal member (Christopher Rivers) called the separate-legal-entity defence "a remarkable submission" and wrote that the airline gave no reason why customers should double-check one part of its site against another. The order, from the decision itself: CAD 650.88 damages + 36.14 interest + 125 fees = 812.02. Why it works: the amounts are tiny and the subject is grief; nothing needs embellishing. Words only; show our own retyped chat, no screenshots. [6][7]
2. **Kinshasa: paper, not cameras.** A technical school asked for facial recognition to track student attendance "like in the news". The writer visited. Teachers passed a paper sheet each morning and students signed for absent friends. The fix took an afternoon: a shared link, a few ticked boxes, one spreadsheet. A second anecdote from the same post: a planned recommendation engine replaced by a well-built database query that worked in two days. Why it works: it is funny, small and instantly relatable to any owner. Single-author blog on a vendor site, school unnamed; say "he wrote" and do not name the school. [3]
3. **A CEO walks back his own press release.** Klarna, 27 Feb 2024: the AI assistant had 2.3 million conversations in its first month, "equivalent work of 700 full-time agents", resolution in under 2 minutes versus 11. Siemiatkowski, 8 May 2025 (Bloomberg, quote checked in PYMNTS): cost "unfortunately seems to have been a too predominant evaluation factor", so "you end up with lower quality"; the promise now is that a customer can always reach a human. Feb 2026 (podcast, via CX Foundation): the company is onboarding its most passionate customers to work part-time in service from home, and says no one lost a job. Why it works: a public reversal and a human fix. Do not say "fired 700": the release says "equivalent work", and Klarna did not abandon AI. [9]
4. **Thailand's eye-screening nurses.** Thailand aims to screen 60% of people with diabetes for an eye disease that can cause blindness, with about 4.5 million patients and roughly 200 retinal specialists. Google built an AI that read photos in minutes at specialist accuracy in the lab. In 11 clinics over about 8 months, researchers watched what happened: more than a fifth of images were rejected, only 2 of 11 clinics had a room that could be darkened, uploads took 60–90 seconds on slow internet, and nurses were frustrated when a scan they thought was fine was rejected, because the patient then had to travel. One researcher said patients cared about their experience, not that it was an AI. A later 7,940-patient study found the AI more sensitive than specialist over-readers for vision-threatening disease, with a specialist reviewing every image as a safety check. Why it works: the honest lesson is that accuracy was never the problem, the clinic was; and it is Southeast Asian. Google-authored and Google-funded; the nurse quotes and the one-fifth figure come from MIT Technology Review and TechCrunch quoting the CHI paper, so confirm them in the paper before they reach the screen. [15]
5. **Kaiser's doctors and the notes they wrote at night.** The Permanente Medical Group: some physicians spend close to a quarter of a work week on records and finish at night or on days off. It offered an ambient note-taking tool as an option, not a requirement; doctors review every note; heavy users told colleagues (grassroots). A doctor-leader's small scene: the tool filtered out chat about children, pets and Christmas greetings from decades-long patient relationships while writing the note she would have typed. Honest cost: it sometimes got facts wrong (a planned prostate exam written as done). Kaiser's own estimate: about 15,800 hours saved over 63 weeks across 7,260 physicians. An independent randomised trial at UCLA found a much smaller effect. Why it works: the pain is simple to say and the tool never touches diagnosis. The hours are Kaiser's own estimate, observational. [16]
6. **"The price that sells the most" is not "the price that earns the most".** From RAND's interviews: leaders asked a team for a model to set a price, and what they actually needed was the price with the best profit margin. Another interviewee's team was told to apply AI where a few if-then rules would have done. Why it works: an owner gets it at once; it shows what a wrong question costs. [1]
7. **The lawyer who kept her $20 chatbot.** MIT's report quotes an unnamed mid-sized-firm lawyer: her firm paid $50,000 for a contract-analysis tool, but she kept using a $20-a-month chatbot because she could steer it and iterate; she drew the line at high-stakes contracts. The same report says workers at over 90% of surveyed companies used personal AI tools while only 40% of companies had bought an official subscription. Why it works: the people with the pain found the painkiller first. Anonymous and interview-based: "a lawyer told researchers". [5]
8. **Some owners counted their CCTV cameras as "AI".** In the Cambodian survey, the authors treat the image-and-video AI figure as an upper bound because some respondents seem to have counted ordinary CCTV. Alongside: 58.61% of firms track no key business number; 68.50% run on phone, email, social media and paper; only 33.70% feel competitor pressure. Why it works: it is a Cambodian number that makes an owner feel seen, not scolded. [10]
9. **"We only have the lab results."** Calmette Hospital's team told a French-language outlet in July 2024 that not all medical data is on computer, so their antibiotic-resistance predictor would use only bacteriology results and could not include diagnoses or treatments; they named adoption (friendly design, training, resistance to change) as the hard part. Why it works: a data limit stated plainly by the people building the tool. No published accuracy found; the award release is promotional. [11]
10. **Grief, timed.** The decision says Moffatt's grandmother died on the same day the chatbot answered. Any funeral, journey or feeling is ours to imagine and must be framed as imagination ("imagine that day…"). [6]

Also found, not in the spine (use if a beat needs it): Zillow Offers shut down 2 Nov 2021 after a ~$304M inventory write-down and a ~25% staff cut; founder Rich Barton's letter ends by recalling he bought Zillow.com for $8.95 and says it weighs on him to let 25% of colleagues go (price-forecasting bet, not generative AI) [13]. McDonald's ended its drive-thru voice test with IBM in July 2024 and Taco Bell's technology chief said in Aug 2025 he is rethinking where voice AI belongs, with trained staff stepping in at busy times [9]. Samsung's May 2023 memo banning generative AI at work after engineers pasted source code in [9]. Morgan Stanley's advisor assistant, which answers only from the firm's own documents and links to the source (company-reported figures) [17]. MD Anderson and IBM Watson: see "Handle with care" before using.

## The case for starting with the problem

The strongest evidence, best first. None of it proves that starting with the problem *causes* success: it is all interviews or self-reported surveys.

- **RAND (13 Aug 2024)** [1]: 65 interviews (50 industry, 15 academic), at least five years' experience each. Five root causes: stakeholders misunderstand or miscommunicate the problem; the organisation lacks the data; the team chases technology instead of users' problems; weak infrastructure; the problem is too hard for AI. First principle in the report's own words: "Focus on the problem, not the technology." 84% of the industry interviewees named a leadership-driven cause. RAND's own caveats: most interviewees were engineers, so results may skew toward blaming leadership; it covered machine learning, not prompt-only chatbot projects.
- **MIT NANDA (Aug 2025)** [5]: preliminary; 300+ public initiatives, 52 organisation interviews, 153 leaders surveyed at four conferences. The "95%" is two different things in one report: "95% of organisations getting zero return", and about 5% of enterprise-grade, task-specific tools reaching production with remarked impact. The report says its figures are "directionally accurate". Its explanation is a "learning gap" in tools that do not adapt. Buying from a partner reached deployment about twice as often as building in-house, but the report warns that this may not be causal.
- **BCG, "The Widening AI Value Gap" (Sep 2025)** [14]: 1,250 senior executives, 68 countries, self-reported. 5% get value at scale, 35% scale with some return, 60% see hardly any material value. Laggards hand AI to middle managers who are unsure or fearful. The 10-20-70 rule (10% algorithms, 20% technology, 70% people and process) is a rule of thumb about where effort goes, not a measured result.
- **McKinsey, State of AI (Nov 2025)** [verify, summaries only]: 1,993 respondents; "high performers" (about 6%) were far more likely to have fundamentally redesigned workflows (55% against 20%). Correlation with a label, not proof of cause.
- **Gartner** [predictions, verify on gartner.com]: at least 30% of generative AI projects abandoned after proof of concept by end of 2025 (a July 2024 prediction); 60% of AI projects without AI-ready data abandoned through 2026 (Feb 2025); over 40% of agentic AI projects cancelled by end of 2027 (June 2025). Predictions, not measurements.
- **IBM CEO study (May 2025)** [12]: 2,000 CEOs; 64% say fear of falling behind drives investment before they understand the value; 25% of AI initiatives delivered expected ROI; 16% scaled enterprise-wide.
- **Deloitte (Jan 2026)** [verify]: 3,235 leaders; only 25% have moved 40% or more of pilots into production.

### The honest number line (for the script)

These measure different things; do not average them or quote one as "the" rate.

| Study | Figure | What it actually measures |
|---|---|---|
| MIT NANDA 2025 | about 5% | enterprise-grade or task-specific tools reaching production with remarked impact; 52 organisations |
| BCG 2025 | 5% | firms getting AI value at scale; 1,250 executives, self-reported |
| McKinsey 2025 | about 6% | "high performers" by profit impact; 1,993 respondents |
| IBM 2025 | 25% | initiatives delivering expected ROI; 2,000 CEOs |
| Deloitte 2026 | 25% | leaders with 40%+ of pilots in production |
| S&P Global 2025 (via CIO Dive) | 42% | companies that scrapped most initiatives; secondary only |
| Wharton and GBK 2025 | nearly 75% | report positive ROI; about 800 US senior decision makers at large firms; self-reported |

Never merge BCG's 5% and MIT's 5%: they are different questions. The same headline swings from "nearly all fail" to "nearly all succeed" depending on the question.

### Counter-views (one line each, and the script's answer)

- **"Let staff experiment first; you cannot know the problem in advance."** Ethan Mollick (Wharton, May 2025) argues nobody has a playbook for your company and the time to begin is not when everything is clear [verify wording]; many workers hide their AI use out of fear. Answer: the people who feel the pain are the ones who find the problems, so problem-first does not mean committee-first. MIT's best deployments began with power users and frontline managers.
- **"The failure numbers are weak."** Agreed: the 80% is borrowed, the 95% mixes denominators, Gartner's are predictions, and Wharton finds nearly three-quarters report positive ROI. The film says so on screen.
- **"The 70% is an effort rule."** Agreed. BCG states it as where focus should go; no derivation found.
- **"Sources disagree on where value is."** BCG says 70% of potential value sits in core business functions, MIT says back-office pays best, RAND and Gartner stress data, MIT says data is not the barrier. The film does not turn any of these into a rule.

## The framework (our synthesis)

Eight steps in three bands, plus a napkin version. SYNTHESIS = wording, order and grouping are ours; QUOTED = the idea is taken from a named source. Each step has one test a manager can ask, the sources behind it, and the failure it prevents.

**Napkin version (the three questions the film teaches):**
1. What hurts, in plain words, and what number will show it is fixed?
2. Do we have the real records, and who owns and checks them?
3. Will the people who do the work use it, and have we been honest with them?

### Band 1: Strategy (what hurts?)

- **S1. Say the pain in plain words, with no "AI" in the sentence.** (test QUOTED from Progress, wording ours.) *Test:* can I describe this in one sentence without saying AI, and say whose day gets easier? *Sources:* Progress Why Audit [3]; Microsoft step 1 [20]; RAND "focus on the problem" [1]. *Prevents:* tech-first projects. Kinshasa wanted cameras and had a paper problem.
- **S2. Pick the one number that proves it is fixed, and check it tracks money, not just activity.** (SYNTHESIS) *Test:* which number on my monthly report should change? *Sources:* RAND price example [1]; Ng, measurable objective [18]; Progress, report business numbers [3]. *Prevents:* a model tuned to the wrong metric (RAND cause 1); "unclear business value" (a named Gartner cause of abandonment).
- **S3. Try the simplest fix first, use AI only for what is left, and borrow a ready tool before building your own.** (SYNTHESIS) *Test:* would a form, a checklist, a spreadsheet or a few rules solve most of it? *Sources:* RAND if-then rules [1]; Progress's attendance spreadsheet and database-query stories [3]; Microsoft's warning against reaching for generative AI where a repeatable flow will do [20]; MIT's buy-versus-build finding (with its not-causal caveat) [5]. *Prevents:* paying for AI where a form would do.

### Band 2: Data (what do we truly know?)

- **D1. Look at the real records for this one problem: do they exist, are they correct, can you reach them today?** (SYNTHESIS) *Test:* show me ten real past cases of this problem with the right answer written next to them (the "ten cases" wording is ours). *Sources:* RAND, weekly sales reports are not the right data [1]; Progress, data realism [3]; Gartner, data readiness judged per use case [verify]. *Prevents:* discovering late that the data was never recorded, or was recorded for another purpose. Cambodian anchor: 58.61% of surveyed firms track no key number [10].
- **D2. Give the data and the answers one owner who checks them by hand.** (SYNTHESIS) *Test:* who owns this data, and who checks the high-stakes answers before they go out? *Sources:* RAND, data work is "the plumbers'" job and knowledge leaves with the person [1]; MIT, humans preferred for complex work [5]; Kaiser's doctors reviewing every note [16]; Moffatt, where nobody checked [6]. *Prevents:* silent errors and a project that dies when one person leaves.

### Band 3: People (will they use it and trust it?)

- **P1. Start with the people who feel the pain, and fit the fix into steps they already do.** (SYNTHESIS) *Test:* did the people who do this job say what would help, and does it add steps to their day? *Sources:* MIT, projects sourced from frontline managers [5]; Gartner, build into existing workflows and involve staff in the pilot [verify]; Progress, "adoption" [3]; McKinsey, workflow redesign [verify]; Thai nurses [15]. *Prevents:* tools that workers bypass.
- **P2. Tell the team honestly what it means for their jobs, and teach the basics.** (SYNTHESIS) *Test:* can I say plainly what happens to my staff's work if this succeeds? *Sources:* Mollick, hidden AI use out of fear [verify]; RAND, subject-matter experts quietly resisting [1]; BCG, fearful middle managers [14]; Klarna, a human always available [9]. *Prevents:* secret use and passive resistance.
- **P3. Test small for a set time, watch the one number, then keep, fix or stop.** (SYNTHESIS) *Test:* after the trial did the number move, and are people still using it a month after the novelty? *Sources:* Ng, a first pilot with traction in 6–12 months [18]; Progress, retention [3]; RAND, stay with a problem rather than switching [1]; Gartner and S&P on abandonment after proof of concept. *Prevents:* the demo that never reaches real use, and abandoning a good project too early. Do not give "6–12 months" or "a year" to a small shop as advice: they come from large-firm and machine-learning projects.

### How it relates to named frameworks

Microsoft orders its decisions problem first, which matches ours [20]. Google [21] and BCG [14] organise around people, process, technology and data. Ng puts strategy fourth, after a pilot, because most firms cannot write a good one before they have experience [18]; our framework asks only for a clear problem, not a grand AI strategy, which is consistent with his reasoning, but MIT and BCG show top-level commitment matters in large firms, so this is not a universal order.

## Script lines (Khmer)

Natural, warm Khmer keyed to the beats, ready for `script_km.py`. **These are my drafts and nobody has read them aloud: they need a native read, and every † word in "Names and terms" needs an ear check once narrated.** Numbers and years are written as Khmer words on purpose because digits are untested with the narrator clone. Short sentences end with «។» because the clone pauses at full stops, not at spaces. No Latin letters reach the voice. Names and terms use the spellings in the table below. The decision uses "they/their" for Moffatt, so the lines use the name ជេក and never a gendered honorific. A few lines are marked (optional) and are the first to cut.

- Hook (date): «ថ្ងៃទីដប់មួយ ខែវិច្ឆិកា ឆ្នាំពីរពាន់ម្ភៃពីរ។ យាយរបស់ជេក បានស្លាប់។»
- Hook (the question): «ថ្ងៃតែមួយនោះ ជេកបើកគេហទំព័ររបស់ក្រុមហ៊ុនអ៊ែរកាណាដា ដើម្បីទិញសំបុត្រយន្តហោះ។ ហើយសួរឆាតបូតថា មានតម្លៃពិសេសឬអត់ សម្រាប់មនុស្សដែលបាត់បង់សាច់ញាតិ។»
- Hook (the answer): «ឆាតបូតឆ្លើយថា អាចទិញសំបុត្រតម្លៃធម្មតាសិន ហើយដាក់ពាក្យសុំតម្លៃពិសេសក្រោយ ក្នុងរយៈពេលកៅសិបថ្ងៃ។»
- Hook (the page): «ប៉ុន្តែទំព័រដែលឆាតបូតបង្ហាញតំណ សរសេរផ្ទុយពីនេះ។»
- Hook (the refusal): «ជេកដាក់ពាក្យសុំ មិនទាន់ដល់មួយសប្តាហ៍ក្រោយមក។ ក្រុមហ៊ុនបដិសេធ។ ក្រោយមក បុគ្គលិកម្នាក់ទទួលស្គាល់ថា ឆាតបូតបានប្រើពាក្យ ដែលនាំឱ្យយល់ច្រឡំ។ តែក៏នៅតែមិនសងប្រាក់។»
- Hook (the tribunal): «ជេកនាំរឿងនេះ ទៅតុលាការតូចមួយ ដែលដោះស្រាយវិវាទតាមអ៊ីនធឺណិត។ ជេកគ្មានមេធាវីទេ។ ក្រុមហ៊ុនបញ្ជូនបុគ្គលិកម្នាក់ មកតំណាង។»
- Hook (the defence): «ក្រុមហ៊ុនអះអាងថា ឆាតបូតជាអង្គភាពដាច់ដោយឡែក ដែលទទួលខុសត្រូវចំពោះសកម្មភាពរបស់ខ្លួនឯង។ សមាជិកតុលាការហៅពាក្យនេះថា ការអះអាងដ៏ចម្លែក។»
- Hook (the ruling): «ថ្ងៃទីដប់បួន ខែកុម្ភៈ ឆ្នាំពីរពាន់ម្ភៃបួន តុលាការសម្រេចថា ឆាតបូតគឺជាផ្នែកមួយនៃគេហទំព័រ ហើយក្រុមហ៊ុនត្រូវទទួលខុសត្រូវ។ ក្រុមហ៊ុនត្រូវសងសរុបប្រាំបីរយដប់ពីរដុល្លារកាណាដា។»
- Hook (the turn): «តុលាការនិយាយថា ក្រុមហ៊ុនមិនបានយកចិត្តទុកដាក់គ្រប់គ្រាន់ ដើម្បីប្រាកដថា ឆាតបូតនិយាយត្រូវ។ រឿងនេះមិនមែនអំពីថា ឆាតបូតឆ្លាតឬអត់ទេ។ គឺអំពីការដែលគ្មាននរណាម្នាក់ ឈរក្បែរមនុស្សដែលមានបញ្ហា ហើយសួរថា យើងកំពុងប្រាប់គាត់អ្វី។»
- Pressure (everyone says): «ឥឡូវនេះ ក្រុមហ៊ុននីមួយៗ ត្រូវបានគេនិយាយថា ត្រូវប្រើអេអាយ។ បើមិនប្រើ នឹងយឺតជាងគេ។»
- Pressure (RAND): «ស្ថាប័នស្រាវជ្រាវអាមេរិកមួយឈ្មោះ រ៉ែន បានសម្ភាសអ្នកជំនាញអេអាយ ហុកសិបប្រាំនាក់។ ពួកគេប្រាប់ថា អ្នកគ្រប់គ្រងស្ថិតក្រោមសម្ពាធ ឱ្យធ្វើអ្វីមួយ ណាក៏បាន ជាមួយអេអាយ។»
- Pressure (the first cause): «មូលហេតុទីមួយដែលពួកគេរកឃើញ គឺមនុស្សមិនយល់ច្បាស់ ថាបញ្ហាដែលត្រូវដោះស្រាយ គឺអ្វី។»
- Pressure (Cambodia): «នៅកម្ពុជា អ្នកស្រាវជ្រាវបានទូរសព្ទសួរម្ចាស់ និងអ្នកគ្រប់គ្រងរោងចក្រ ដែលបានចុះបញ្ជី ពីររយចិតសិបបីរោងចក្រ។ ជាងពាក់កណ្តាល មិនបានតាមដានលេខសំខាន់ណាមួយ នៃអាជីវកម្មខ្លួនសោះ។»
- Pressure (not alone): «ហើយមានតែមួយភាគបីប៉ុណ្ណោះ ដែលមានអារម្មណ៍ថា ក្រុមហ៊ុនប្រកួតប្រជែង កំពុងប្រើអេអាយ ដាក់សម្ពាធលើខ្លួន។ បើអ្នកមិនទាន់ចាប់ផ្តើម អ្នកមិនមែនតែម្នាក់ឯងទេ។»
- Chasing (Klarna boast): «ក្រុមហ៊ុនក្លាណា នៅប្រទេសស៊ុយអែត ប្រកាសនៅខែកុម្ភៈ ឆ្នាំពីរពាន់ម្ភៃបួន ថាអ្នកជំនួយការអេអាយរបស់ខ្លួន បានជជែកជាមួយអតិថិជន ពីរលានបីសែនដង។ ស្មើនឹងការងាររបស់បុគ្គលិកប្រាំពីររយនាក់។»
- Chasing (Klarna turn): «ដល់ខែឧសភា ឆ្នាំពីរពាន់ម្ភៃប្រាំ នាយកប្រតិបត្តិរបស់ក្រុមហ៊ុន បាននិយាយថា គេយកតម្លៃថោក ជាកត្តាធំពេក ហើយលទ្ធផលគឺគុណភាពទាប។»
- Chasing (Klarna human): «ក្រុមហ៊ុនមិនបានបោះបង់អេអាយទេ។ តែបានចាប់ផ្តើមជួលមនុស្សមកឆ្លើយអតិថិជនឡើងវិញ ដើម្បីឱ្យអតិថិជនអាចជួបមនុស្សបានជានិច្ច បើគេចង់។»
- Chasing (Klarna customers, optional): «គាត់ថែមទាំងចង់ឱ្យអតិថិជន ដែលស្រឡាញ់ក្រុមហ៊ុនបំផុត មកធ្វើការជាផ្នែក ពីផ្ទះ។»
- Chasing (RAND price): «នៅក្នុងរបាយការណ៍ដដែល អ្នកជំនាញម្នាក់និយាយថា ថ្នាក់ដឹកនាំបានសុំម៉ូដែលមួយ ដើម្បីរកតម្លៃដែលលក់បានច្រើនបំផុត។ ប៉ុន្តែតម្លៃដែលលក់បានច្រើនបំផុត មិនមែនជាតម្លៃដែលរកប្រាក់ចំណេញបានច្រើនបំផុតទេ។»
- Chasing (Kinshasa 1): «អ្នកសរសេរម្នាក់ នៅទ្វីបអាហ្វ្រិក បានរៀបរាប់ពីសាលាបច្ចេកទេសមួយ ដែលសុំប្រព័ន្ធស្គាល់មុខ ដើម្បីរាប់វត្តមាននិស្សិត។ ដូចដែលគេឃើញក្នុងព័ត៌មាន។»
- Chasing (Kinshasa 2): «គាត់ទៅមើលដោយផ្ទាល់។ រាល់ព្រឹក គ្រូបញ្ជូនក្រដាសចុះឈ្មោះ ហើយនិស្សិតខ្លះ ចុះឈ្មោះជួសមិត្តដែលអវត្តមាន។ បញ្ហាគឺក្រដាស មិនមែនការស្គាល់មុខទេ។»
- Chasing (Kinshasa 3): «ដំណោះស្រាយ ចំណាយពេលតែមួយរសៀល។ តំណមួយ ប្រអប់ពីរបីដែលត្រូវតិក និងតារាងមួយ។ គ្មានកាមេរ៉ា។ គ្មានអេអាយ។»
- Numbers (honest): «តើអេអាយក្នុងក្រុមហ៊ុន បរាជ័យញឹកញាប់ប៉ុណ្ណា? គ្មានចម្លើយតែមួយទេ។ ការសិក្សានីមួយៗ សួរសំណួរផ្សេងគ្នា។»
- Numbers (the four): «សាកលវិទ្យាល័យអិមអាយធី រកឃើញថា ប្រហែលប្រាំភាគរយ នៃឧបករណ៍ពិសេសសម្រាប់ក្រុមហ៊ុន ទៅដល់ការប្រើប្រាស់ពិត។ ការស្ទង់មតិមួយរបស់អាយប៊ីអិម ថាម្ភៃប្រាំភាគរយ ទទួលបានផលដូចរំពឹង។ ការស្ទង់មតិមួយទៀត ថាក្រុមហ៊ុនសែសិបពីរភាគរយ បានបោះបង់គម្រោងភាគច្រើន។ ហើយការស្ទង់មតិមួយទៀត ពីក្រុមហ៊ុនធំនៅអាមេរិក ថាជិតបីភាគបួន ទទួលបានផលល្អ។»
- Numbers (so what): «លេខទាំងនេះ មិនអាចយកមកបូកបញ្ចូលគ្នាបានទេ។ ដូច្នេះ កុំជឿលេខណាមួយ ដូចជាច្បាប់ធម្មជាតិ។ សូមសួរថា តើវាវាស់អ្វី។»
- Framework (intro): «ដូច្នេះ តើត្រូវចាប់ផ្តើមពីណា? យើងបានប្រមូលគំនិតពីការសិក្សាទាំងនេះ ជាបីសំណួរ។ នេះជាវិធីគិតមួយ មិនមែនជាមន្តអាគមទេ។»
- Framework (strategy): «សំណួរទីមួយ៖ តើអ្វីដែលពិបាក? និយាយវាឱ្យបានចំ ដោយមិនប្រើពាក្យអេអាយ។ បើអ្នកមិនអាចនិយាយបានទេ អ្នកនៅមិនទាន់មានបញ្ហា។ អ្នកមានតែចំណង់ចង់ប្រើបច្ចេកវិទ្យា។»
- Framework (the one number): «បន្ទាប់មក ជ្រើសលេខមួយ ដែលនឹងបញ្ជាក់ថាបញ្ហាបានជា។ ហើយសួរថា តើទម្រង់ ឬបញ្ជីត្រួតពិនិត្យ អាចដោះស្រាយបានភាគច្រើនឬទេ។»
- Framework (data): «សំណួរទីពីរ៖ តើយើងមានកំណត់ត្រាពិតឬទេ? សូមយកករណីពិតដប់ ដែលមានចម្លើយត្រឹមត្រូវសរសេរនៅក្បែរ។ បើរកមិនបាន នោះគឺជាចម្លើយរួចហើយ។»
- Framework (RAND data): «អ្នកជំនាញម្នាក់ប្រាប់ថា ថ្នាក់ដឹកនាំគិតថាមានទិន្នន័យល្អ ព្រោះទទួលរបាយការណ៍លក់រាល់សប្តាហ៍។ តែទិន្នន័យដែលកត់ទុកសម្រាប់ការងារមួយ មិនមែនជាទិន្នន័យដែលការងារមួយទៀតត្រូវការទេ។»
- Framework (Calmette): «នៅមន្ទីរពេទ្យកាល់ម៉ែត ក្នុងភ្នំពេញ ក្រុមស្រាវជ្រាវបង្កើតឧបករណ៍មួយ ទាយថាមេរោគណា ទប់ទល់នឹងថ្នាំអង់ទីប៊ីយ៉ូទិកណា។ ពួកគេបានប្រាប់ដោយត្រង់ថា ទិន្នន័យពេទ្យ មិនទាន់ត្រូវបានដាក់ចូលកុំព្យូទ័រទាំងអស់ ដូច្នេះគេប្រើបានតែលទ្ធផលពីមន្ទីរពិសោធន៍។ យើងមិនទាន់រកឃើញលទ្ធផល ដែលបានចេញផ្សាយទេ។»
- Framework (people): «សំណួរទីបី៖ តើអ្នកដែលធ្វើការនេះរាល់ថ្ងៃ នឹងប្រើវាឬទេ? ហើយតើយើងបាននិយាយត្រង់ជាមួយគេឬនៅ?»
- Framework (Thailand 1): «នៅប្រទេសថៃ គេបង្កើតអេអាយមួយ អានរូបថតភ្នែករបស់អ្នកជំងឺទឹកនោមផ្អែម។ នៅក្នុងមន្ទីរពិសោធន៍ វាត្រឹមត្រូវដូចអ្នកឯកទេស។ ប៉ុន្តែនៅគ្លីនិកពិត ជាងមួយភាគប្រាំនៃរូបថត ត្រូវបានបដិសេធ។ មានតែពីរក្នុងចំណោមដប់មួយគ្លីនិក ដែលមានបន្ទប់ងងឹតគ្រប់គ្រាន់។ ហើយអ៊ីនធឺណិតយឺត។»
- Framework (Thailand 2): «គិលានុបដ្ឋាយិកាខកចិត្ត ព្រោះរូបថតដែលពួកគាត់ឃើញថាល្អ ត្រូវបានបដិសេធ ហើយអ្នកជំងឺត្រូវធ្វើដំណើរទៅរកអ្នកឯកទេស។ បញ្ហាមិនមែនភាពត្រឹមត្រូវទេ។ គឺគ្លីនិក និងមនុស្ស។»
- Framework (Kaiser): «នៅរដ្ឋកាលីហ្វ័រញ៉ា ក្រុមសុខាភិបាលធំមួយ ដឹងថាគ្រូពេទ្យខ្លះ ចំណាយពេលជិតមួយភាគបួន នៃសប្តាហ៍ធ្វើការ ទៅលើកំណត់ត្រា ហើយច្រើនតែធ្វើវាពេលយប់។ ពួកគេផ្តល់ឧបករណ៍មួយ ដែលស្តាប់ការពិគ្រោះ ហើយសរសេរកំណត់ត្រាជំនួស។ វាជាជម្រើស មិនបង្ខំ។ ហើយគ្រូពេទ្យត្រួតពិនិត្យរាល់កំណត់ត្រា។»
- Framework (Kaiser honesty): «ក្រុមនេះប៉ាន់ស្មានថា ចំណេញពេលបានប្រហែលដប់ប្រាំមួយពាន់ម៉ោង។ តែនេះជាលេខរបស់ពួកគេផ្ទាល់។ ការសាកល្បងឯករាជ្យមួយ រកឃើញលទ្ធផលតូចជាងនេះ។»
- Framework (lawyer, optional): «មេធាវីម្នាក់ប្រាប់អ្នកស្រាវជ្រាវអិមអាយធី ថាក្រុមហ៊ុនគាត់ចំណាយប្រាំម៉ឺនដុល្លារ ទិញឧបករណ៍មួយ។ ប៉ុន្តែគាត់នៅតែប្រើឆាតជីភីធី ដែលតម្លៃម្ភៃដុល្លារក្នុងមួយខែ ព្រោះគាត់អាចជជែកតាមដានបាន។»
- Framework (trust): «ឧបករណ៍ដែលមនុស្សជឿទុកចិត្ត គឺឧបករណ៍ដែលគេអាចឃើញថា ចម្លើយមកពីណា ហើយអាចនិយាយថាទេ។»
- Framework (small test): «ចុងក្រោយ សាកល្បងតូចមួយ។ មើលលេខដែលអ្នកបានជ្រើស។ ក្រោយមួយខែ មើលថា មនុស្សនៅតែប្រើវាឬអត់។ រួចសម្រេចចិត្ត៖ បន្ត កែ ឬឈប់។»
- Cambodia (survey advice): «ក្រុមស្រាវជ្រាវកម្ពុជាដែលស្ទង់មតិរោងចក្រទាំងនោះ សរសេរថា ការប្រើអេអាយមុនមានប្រព័ន្ធមូលដ្ឋាន ជារឿងមិនទាន់ដល់ពេល។ ពួកគេណែនាំឱ្យចាប់ផ្តើមពីឧបករណ៍ឥតគិតថ្លៃ សម្រាប់កត់គណនេយ្យ ស្តុក និងការបញ្ជាទិញ។»
- Cambodia (cashew): «មានក្រុមមួយ បង្កើតឆាតបូតនៅលើតេឡេក្រាម ឱ្យកសិករចិញ្ចឹមស្វាយចន្ទី សួរអំពីដើមឈើ ជាភាសាខ្មែរ ដោយផ្ញើរូបថត សំឡេង ឬអក្សរ។ ពួកគេកំពុងសាកល្បងនៅខេត្តកំពង់ធំ។ នេះនៅដើមដំបូង ហើយមិនទាន់មានលទ្ធផលចេញផ្សាយ។»
- Cambodia (bank, optional): «ធនាគារមួយក្នុងភ្នំពេញ ក៏មានជំនួយការជជែក ជាភាសាខ្មែរ។ ធនាគារនិយាយថា មានអ្នកប្រើជាងម្ភៃប្រាំពាន់នាក់ ក្នុងមួយខែ។ នេះជាលេខរបស់ធនាគារខ្លួនឯង។»
- Ending (heart): «អេអាយមិនដឹងថា អ្វីពិបាកទេ។ មានតែមនុស្សប៉ុណ្ណោះ ដែលដឹង។»
- Ending (the question): «ដូច្នេះ មុនពេលអ្នកសួរថា តើត្រូវប្រើអេអាយអ្វី សូមសួរខ្លួនឯងថា ក្នុងការងាររបស់អ្នក មានអ្វីមួយ ដែលពិបាក ឬចំណាយពេលច្រើនជាងគេ។ ចាប់ផ្តើមពីទីនោះ។»
- Ending (last line): «ហើយសូមឱ្យមានមនុស្សម្នាក់ ឈរនៅក្បែរអ្នកដែលមានបញ្ហា។»

## Timeline

| Date | Event | Sources |
|---|---|---|
| Jun 2012 – about Sep 2016 | MD Anderson's Oncology Expert Advisor project with IBM: contract extended 12 times; about $62.1M total spend per the UT System audit | [verify, via Medscape and Network World] |
| Dec 2018 | Andrew Ng, Landing AI, "AI Transformation Playbook" (five steps; first pilot with traction in 6–12 months) | [18] |
| 11 Nov 2022 | Jake Moffatt's grandmother dies; same day the chatbot answers the bereavement-fare question | [6] |
| 17 Nov 2022 | First refund application | [6] |
| 30 Nov 2022 | OpenAI releases ChatGPT (nineteen days after the chatbot conversation) | OpenAI release page |
| 8 Feb 2023 | An airline rep admits the chatbot used "misleading words"; refund still refused | [6] |
| 14 Feb 2024 | Tribunal decision, 2024 BCCRT 149; order CAD 812.02 | [6][7] |
| 27 Feb 2024 | Klarna press release: 2.3M conversations, "equivalent work of 700 full-time agents" | [9] |
| 29 Jul 2024 | Gartner predicts at least 30% of generative AI projects abandoned after proof of concept by end of 2025 | [verify] |
| 13 Aug 2024 | RAND report (65 interviews, five root causes) | [1] |
| 6 May 2025 | IBM CEO study: 64% invest from fear of falling behind | [12] |
| 8 May 2025 | Klarna CEO, Bloomberg interview: cost "too predominant", lower quality, humans back | [9] |
| Jun 2025 | Draft National AI Strategy 2025–2030 (Ministry of Post and Telecommunications), still a draft | [10] |
| Jul–Aug 2025 | MIT NANDA "The GenAI Divide" (preliminary) | [5] |
| Sep 2025 | BCG "The Widening AI Value Gap" (5% / 35% / 60%) | [14] |
| 15–26 Dec 2025 | Fieldwork for the KAS/CADT survey of 273 Cambodian manufacturers | [10] |
| Feb 2026 | KAS/CADT "Digital Insights" published; Klarna CEO on a podcast about recruiting customers | [10][9] |
| 23 Mar 2026 | Progress Software problem-first post (Kinshasa attendance story) | [3] |

## Names and terms

Spellings built from letter-name rules rather than Khmer media precedent are marked †; run them through the documentary's ASR check once narrated, and treat that as a floor, not proof: the clone can misread what the ASR accepts. **Key finding: Khmer business media print company names and "AI" in Latin letters (89 uses of Latin "AI" against 16 of បញ្ញាសិប្បនិម្មិត in eight pages), so almost every name has no Khmer-script print precedent and the `SAY` table must carry these spellings.** The official term for AI is បញ្ញាសិប្បនិម្មិត (Ministry lexicon, 2025); the channel keeps អេអាយ for narration. Names marked "screen only" are not voiced in the draft script.

| Name or term | Who or what | Khmer spelling (as spoken) | Sources | Voice risk and respelling |
|---|---|---|---|---|
| Jake Moffatt | applicant in the tribunal case | ជេក (first name only after the first mention); ម៉ូហ្វេត † if the surname is voiced | decision [6] | M. The decision calls them "Mr. Moffatt" with "they". No gendered honorific; ជេក or គាត់. The decision spells the surname "Moffat" in paras 14, 15, 19. |
| Air Canada | airline | អ៊ែរកាណាដា | Monoroom (Montreal Khmer magazine, 2015) | L–M. If អ៊ែរ is mangled try អេរកាណាដា. |
| Christopher Rivers | "Tribunal Member" | សមាជិកតុលាការ in the script; គ្រីស្តូហ្វឺ រីវឺស † if voiced | decision | M. Never call him ចៅក្រម (judge). Write final ស, not ស៍. |
| Civil Resolution Tribunal | small online tribunal | "តុលាការតូចមួយ ដែលដោះស្រាយវិវាទតាមអ៊ីនធឺណិត" † | descriptive | It is not a full court. Say it once, then "តុលាការ". |
| Klarna | Swedish payments firm | ក្លាណា † | none | L–M. Use ក, not គ (គ្លា would read "klea"). |
| Sebastian Siemiatkowski | Klarna's CEO | "នាយកប្រតិបត្តិរបស់ក្រុមហ៊ុន" in the script; surname screen only | none | H. Pronunciation unverified; no usable audio found. |
| IBM | company | អាយប៊ីអិម † | letter rule | M. The channel has MIT = អិមអាយធី and AMD = អេអឹមឌី: keep one letter-name for M (អិម). |
| Watson | IBM's AI | វ៉ាតសុន † | none | L–M. |
| MD Anderson Cancer Center | Texas cancer hospital | "មន្ទីរពេទ្យព្យាបាលជំងឺមហារីកដ៏ល្បីមួយ នៅរដ្ឋតិចសាស់" | DAP News, Fresh News (តិចសាស់) | L for the description; H if named (អិមឌី អាន់ឌឺសិន †). |
| Kaiser Permanente / Permanente Medical Group | US health system | "ក្រុមសុខាភិបាលធំមួយ នៅរដ្ឋកាលីហ្វ័រញ៉ា" | កាលីហ្វ័រញ៉ា is the plan-06 spelling | H if named (កៃហ្ស៊ឺ ភើមែនតេ †). Describe it. |
| Morgan Stanley | US financial firm | "ក្រុមហ៊ុនហិរញ្ញវត្ថុធំមួយនៅអាមេរិក" | none | M. Describe it. |
| OpenAI | maker of ChatGPT | អូផិនអេអាយ † | one Facebook tech page | M. Write as one word. |
| ChatGPT | chatbot | ឆាតជីភីធី | Khmer Wikipedia title ឆាតជីភីធី (ChatGPT) | M. G = ជី, consistent with ជីភីអេស and ជីភីយូ. Test ឆាត. |
| RAND | US research organisation | រ៉ែន † | none | M. Drop the final d. Say "ស្ថាប័នស្រាវជ្រាវអាមេរិកមួយឈ្មោះ រ៉ែន". |
| MIT | university | អិមអាយធី | existing channel spelling | unchanged. Say "សាកលវិទ្យាល័យអិមអាយធី". |
| NANDA | MIT's AI initiative | screen only | | ណាន់ដា also sounds like the Khmer given name នន្ទា; keep on screen. |
| Google; Gemini | | ហ្គូហ្គល; ជែមីណាយ | existing channel spellings | unchanged |
| McKinsey, BCG, Gartner, Harvard Business Review | consultancies, research firm, magazine | screen only | none | H. Describe: "ក្រុមហ៊ុនប្រឹក្សាធំមួយ". |
| Andrew Ng | AI educator | screen only | none | H. How "Ng" is said is unverified. |
| Vancouver; Canada; Sweden; Singapore | places | វ៉ាន់ខូវឺ; កាណាដា; ស៊ុយអែត; សិង្ហបុរី | Khmer Wikipedia, DAP News | L. Vancouver is spelled two ways in print: pick one. |
| Kinshasa, Africa | city in the DRC | the script says "ទ្វីបអាហ្វ្រិក" | | Avoid voicing Kinshasa. |
| Calmette Hospital | Phnom Penh hospital | មន្ទីរពេទ្យកាល់ម៉ែត † | not checked in this research | M. Confirm the usual Khmer spelling. |
| Thailand | | ប្រទេសថៃ | everyday | L. |
| Telegram | messaging app | តេឡេក្រាម † | none found | M. |
| Phnom Penh; Kampong Thom | | ភ្នំពេញ; ខេត្តកំពង់ធំ | | L. |
| chatbot | | ឆាតបូត | Khmer Wikipedia (ChatGPT article) | Avoid ចាតបូត (machine-translated sites; ចាត់ means "assign"). |
| data | | ទិន្នន័យ | Ministry lexicon; every Khmer outlet | The ន្ន conjunct with ័ may stumble; test. Never use ព័ត៌មាន (news). |
| model | | ម៉ូដែល | AMS, Sabay, DAP | L. |
| algorithm | | ក្បួនដោះស្រាយ (replaces plan-06's ក្បួនគណនា †) | Khmer Wikipedia title via khmerpulse.com | Not used in the script; if it is later, test ក្ប. |
| workflow / process | | ដំណើរការ; plain "របៀបធ្វើការងារ" | | |
| pilot | | "សាកល្បងតូចមួយ" † | | L. |
| ROI | | never voice the letters; say "ចំណាយប៉ុន្មាន ហើយបានមកវិញប៉ុន្មាន" † | | The formal ផលចំណេញពីការវិនិយោគ is H (វិនិយោគ is rare). |
| hallucination | | not used; if needed, "អេអាយប្រឌិតចម្លើយ ហើយនិយាយដូចជាប្រាកដ" † | none | Never say the English. |
| shadow AI | | "បុគ្គលិកប្រើអេអាយដោយលួចលាក់" † | none | |
| trust; customer service; staff | | ទំនុកចិត្ត / ទុកចិត្ត; សេវាអតិថិជន; បុគ្គលិក | DAP News; business sites | L–M. |
| the three bands | Strategy, Data, People | first mention as sentences: «ដឹងថាត្រូវដោះស្រាយបញ្ហាអ្វី» · «ទិន្នន័យដែលអាចទុកចិត្តបាន» · «មនុស្សដែលជឿទុកចិត្តលទ្ធផល»; then short tags «បញ្ហា · ទិន្នន័យ · មនុស្ស» | | Least ambiguous option. Avoid ព័ត៌មាន for data. យុទ្ធសាស្ត្រ is printed but formal and risky for the voice. |

Why these spellings: ហ្គ for hard g, ជ for soft g and the letter G (ជីភីធី, ជែមីណាយ); ក before ា for a clean "a" (ក្លាណា), never គ; avoid a final ស៍ because the clone may drop the s (earlier ស៍ endings, e.g. in plan-04, may be affected); write one brand as one word because the clone pauses at spaces; keep a space only between a given name and a family name.

**Needs a native Khmer ear:** ម៉ូហ្វេត, ក្លាណា, អ៊ែរកាណាដា, ឆាតជីភីធី, អូផិនអេអាយ, ទិន្នន័យ, ឆាតបូត, and the numbers in words (កៅសិប, ប្រាំបីរយដប់ពីរ, ពីររយចិតសិបបី); also these whole lines: "ចំណាយប៉ុន្មាន ហើយបានមកវិញប៉ុន្មាន", the three-band sentences, and the last line «ហើយសូមឱ្យមានមនុស្សម្នាក់ ឈរនៅក្បែរអ្នកដែលមានបញ្ហា។».

## Visuals

The channel rule (docs/channel/README.md): CC0, public domain, CC BY, or the Pixabay/Unsplash licence; no AI-generated clips, no readable logos, no faces unless licensed for it; credit everything on the end card; redraw charts. BY-SA files are outside the list, so none are used.

- **Real material:**
  - Empty Vancouver terminal, March 2020 (CC BY 2.0, GoToVan, Wikimedia Commons) [V11]: opening image, graded cool. Do not imply the 2020 context.
  - Phnom Penh Central Market, night market, Sisowath Quay, a 360° Central Market panorama (all CC0, Wikimedia Commons: Mx. Granger, Dtfman, Kiensvay) and motorbike traffic (CC BY 2.0, ND Strupler): ambience only; shoppers' faces show, so never label a face as a "worried owner".
  - VOA Khmer street-coffee seller video (public domain, 1920×1080, credit "VOA Khmer"): the only Khmer-language public-domain footage found; check it has no wire footage inside.
  - IBM Watson at the 2011 exhibition (CC BY 3.0, Raysonho; carries a trademark tag; crop out IBM marks) and MD Anderson main building (CC BY 4.0, Kenneth C. Zirkel): only if the Watson story is used.
  - Two Pixabay Phnom Penh clips (ferry on the river, motorbike traffic): Pixabay licence; no recognisable faces, no logos.
  - Talks (CC BY on YouTube; use the speaker's voice only, since slides and music may not be covered; captions are auto-generated, check by ear): Cassie Kozyrkov, "Staying Safe in the AI Future" (Big Things Conference, Madrid, 3 Dec 2019), where she says decision-makers set an AI system's purpose and that leaders are often absent; a 15–25 second clip at about 20:37 and the "pet rock" image at 3:37–4:02 (AI is just a tool). Brian T. O'Neill (2020) and Ted Shelton (2025) are candidates but were not transcribed.
- **Not available under a safe licence:** call-centre photos, Cambodian garment-factory or office photos, any Kaiser, Klarna or Morgan Stanley press imagery, Cambodian government imagery.
- **Reports (RAND, MIT, BCG, McKinsey, Gartner):** all rights reserved. Cite a figure in words with a credit and redraw it as our own diagram; show no page, chart image or logo. The tribunal decision is © the Civil Resolution Tribunal: short credited quotes only, retype the chat in our own style, no screenshot of the decision page, and no tribunal or CanLII logos. A full-page view needs the tribunal's written permission.
- **Stock to illustrate (Pixabay/Unsplash queries that return something real):** worried owner, Unsplash "small business owner worried" (stills); office with spreadsheet, Unsplash "spreadsheet on laptop"; hand on a whiteboard, Pixabay "whiteboard" (Coverr footage) or Unsplash "hand drawing on whiteboard" (the best-performing scene); clinic, Unsplash "doctor typing on computer in clinic" (32 hits, on point); customer service desk, Pixabay ids 141672, 337397, 262475 (not 286687 or 287269, which are tagged AI-generated); small team, Unsplash "team around a table meeting laptops"; Phnom Penh, Unsplash "Phnom Penh" (497 hits) or "Cambodia market stall"; rural, Pixabay "khmer" (rice fields). Pixabay now carries AI-generated clips: always read the tags. Pixabay "chatbot" returns only robot clichés; use our own chat window. Cambodian garment-line stock probably does not exist: use hands-and-machines close-ups with no faces, or an illustration.
- **Our own animated diagrams:**
  - The chat re-enactment (opening): a dark navy chat window typing a short excerpt of the chatbot's answer, then the airline's own policy line sliding in underneath contradicting it. Our own UI, the airline named only in words.
  - A Moffatt timeline from Nov 2022 to Feb 2024 with the five nodes above, ending only on the ordered totals (CAD 650.88 damages, CAD 812.02 awarded with its three parts). No fare bars: the decision's itemised fares ($794.98 + $845.38 = $1,640.36) differ by $10 from its own stated total ($1,630.36), so never add them on screen.
  - The framework: three stacked bands (Strategy, Data, People), a yellow dot ("somebody's pain") entering at the top and shrinking as it passes through each band; the 10-20-70 bar as an option, with the 70 lit for People and a caption "a rule of thumb".
  - The honest number line: 20 dots, one dot = 5%, each study in its own labelled row with its source and what it measures. Never merge BCG's 5% with MIT's 5%.
  - Klarna before and after: a seesaw labelled "cost" and "quality", no Klarna logo or colour.
  - The Kinshasa fix: a paper sign-in sheet turning into a checkbox list and one spreadsheet.
- **Mood:** the Moffatt scene is tender and still (low piano or strings, no beat, long holds of 5–6 seconds, muted dawn light); Klarna is brisk and proud, then a stumble (a rising pulse that drops out); the research headlines are neutral and steady (a clock-tick, clean diagram light); the success stories are warm and unhurried (golden desk-lamp light, eye contact); the framework is clear and constructive (one instrument added per band); Cambodia is warm and local (morning light over markets and river, no vocals); the close brings light back to a calm screen with one open question. Opening image: the empty terminal, cool and slow-pushed, then the phone glow and our own chat window.

## Handle with care

- **Jake Moffatt is a private individual** named in a public decision. No photo; a stock actor is never captioned as them; no invented words or feelings stated as fact (the decision quotes only the chatbot's reply and their reliance on it); no age, gender, ethnicity or family beyond the grandmother; avoid gendered honorifics (the decision uses "they"). The funeral, the flight and the mood are imagination and must be framed as such.
- **The chatbot's nature is not established** (decision para 14: no information on its nature) and the conversation predates ChatGPT's release by nineteen days. Say "a chatbot", never "generative AI" or "ChatGPT-style". The claim that Air Canada later removed it has no primary source: leave it out.
- **Fares:** show only the decision's stated totals (CAD 650.88, 812.02). The decision has two $10 arithmetic slips in its itemised figures.
- **Two Watson projects.** MD Anderson's Oncology Expert Advisor (with IBM, 2012 to about 2016, about $62.1M, ended unused on patients outside Houston per the audit coverage) is not IBM's Watson for Oncology product. The UT System audit is about procurement, not the science, and IBM's spokesperson said the project "was a success", so say "the audit found", never "Watson failed". Lynda Chin led the project: report only what the audit says, skip the personal side-notes. The STAT 2018 article on internal IBM slides is paywalled beyond its lede. I would cut this beat unless it is needed.
- **Klarna.** The 700, 853 and $60M figures are Klarna's own estimates, not audited; do not say "fired 700" (the release says "equivalent work", the CEO says no one lost a job); do not say Klarna reversed everything (it moved to a hybrid); do not repeat "now-deleted" (the release was live on klarna.com on 2026-10-14); do not use the 75% some outlets quote (the release says two-thirds). Siemiatkowski is a public figure speaking publicly: fine to paraphrase with a date; do not infer anything from his surname.
- **The statistics.** No single failure rate (see the table). RAND covered machine learning, excluding prompt-only chatbot projects, and its 84% is from interviewees who were mostly engineers. MIT's anonymous interviewees (the COO, the lawyer, the procurement VP) are narrated as "told researchers", never named. Fortune's description of MIT's sample (150 and 350) does not match the report: use the report's 52, 153 and 300+.
- **Kaiser.** The hours saved are Kaiser's own estimate from observational data; an independent randomised trial found a modest effect (one tool about 9.5% less note time, the other no significant change; press and release only, the paper was not opened). Do not use the "an hour a day" summary as a fact. Patients gave consent; do not name the patient quoted by KFF Health News.
- **Thailand.** Both studies are Google-authored and Google-funded. The nurse quotes and "more than a fifth rejected" come from MIT Technology Review and TechCrunch quoting the paper: confirm in the CHI 2020 paper before they reach the screen. The weeks-of-wait figure conflicts between sources, so leave it out.
- **Kinshasa and Progress Software.** A single-author, first-person account on a vendor's blog: say "he wrote", do not name the school, and do not repeat the "20% code, 80% adoption" line (no data behind it).
- **The Cambodian survey.** Registered manufacturers only, phone interviews with owners and managers, 273 analysed against 381 planned, fieldwork 15–26 Dec 2025, a donor-foundation publication that is not peer-reviewed. The book's abstract has errors ("75.76% use no AI" is a share of tool selections, not firms): say "roughly one in six firms use AI", never a false-precision decimal. Its recommendations are written for policymakers and funders: the script says "they wrote", not "you should".
- **Cambodian examples are company or donor claims, not results.** Calmette (no published accuracy; award release is promotional), ChivCheat (early stage; the "60% of farmers use Telegram" figure has no cited origin, so do not use it), ABA's assistant (ABA's own unaudited numbers; trade-press pieces read as bank-supplied), Wing, ACLEDA and the Khmer document-AI project (vendor claims). Never pair a named bank with an AI failure without a source. Do not name the five ChivCheat founders or the Calmette researchers on screen unless the team agrees. Do not infer anyone's age or background.
- **Jobs-at-risk numbers.** Do not use CFOtech Asia's "57% of Cambodian employment" or "88% of garment jobs": the only matching ILO figures are older measures of technical automatability, not AI.
- **Advice a viewer might act on.** The framework is our synthesis of mixed evidence from large and mid-size organisations; say so in the film. Do not give "6–12 months" or Gartner's $5–20M costs to a small shop. The film says "a way of thinking, tested by the people who tried it", not "a method that works".
- **The Cambodia draft strategy is still a draft** and the data-protection law has not been enacted (as of the sources, Feb 2026): say "draft", not "Cambodia's AI strategy".
- **Footage.** Stock only; a stock actor may play "an owner" or "a doctor", never a named real person. Trademarks (airline livery, IBM, Klarna, Kaiser, Morgan Stanley, BCG, McKinsey, Gartner, RAND) are not decoration.

## Sources

1. RAND — Ryseff, De Bruhl, Newberry, "The Root Causes of Failure for Artificial Intelligence Projects and How They Can Succeed", 13 Aug 2024. https://www.rand.org/pubs/research_reports/RRA2680-1.html `[ceb48f]`
2. Fortune — Jeremy Kahn, profile of Aible's CEO, 26 Jul 2022. https://fortune.com/2022/07/26/a-i-success-business-sense-aible-sengupta/ `[2ccb6c]`
3. Progress Software — Willy Muteba, "From Waste to ROI: A Problem-First AI Framework", 23 Mar 2026. https://www.progress.com/blogs/from-waste-to-roi-a-practical-framework-for-problem-first-ai-success `[0c8341]`
4. Teamland — "How to Implement AI Successfully", 8 Jul 2026 (closest generic phrasing). `[0f9caa]`
5. MIT NANDA — Challapally, Pease, Raskar, Chari, "The GenAI Divide: State of AI in Business 2025" (third-party mirror). `[fdf211]`, `[350682]`; Fortune, Jeremy Kahn, 21 Aug 2025 `[76e5cf]`
6. Civil Resolution Tribunal of British Columbia — "Moffatt v. Air Canada, 2024 BCCRT 149", 14 Feb 2024 (CanLII-formatted PDF copy; the CRT and CanLII pages returned 403). `[cb7f19]`
7. CBC News — report on the decision, 15 Feb 2024. `[089c1f]`
8. Chanty Pisal and Sean Mouy Ing — "Profiling the AI Readiness Baseline in Cambodia's Manufacturing SMEs", Konrad-Adenauer-Stiftung Cambodia with CADT, Digital Insights 01/2026. Summary https://cadt.edu.kh/profiling-the-ai-readiness-baseline-in-cambodias-manufacturing-smes/ `[32cde4]`; text extracted from the public PDF (session scratchpad).
9. Klarna — press release, 27 Feb 2024 `[17a705]`; PYMNTS, 8 May 2025 `[a4ad93]`; Retail Systems `[dc5392]`; People Matters `[1961bd]`; CX Foundation, 17 Feb 2026 `[501a9d]`; Restaurant Business, 14 Jun 2024 `[4ed181]`; BBC, 29 Aug 2025 `[4fcb7d]`; Straits Times (Bloomberg), 2 May 2023 `[2489c4]`.
10. KAS/CADT survey (as 8); ESCAP and MISTI, "Artificial Intelligence: Empowering Innovation, Ethics and Inclusion in Cambodia", 2026 `[dabfe1]`; Draft National AI Strategy 2025–2030, Ministry of Post and Telecommunications, Jun 2025 `[1aab8b]`.
11. Le Petit Journal Cambodge, 1 Jul 2024, on the Calmette antibiotic-resistance predictor `[cee9bd]`; CADT release, 6 Dec 2025 `[009135]`; CGIAR, 28 Aug 2024, on ChivCheat `[105697]`; Cambodia Investment Review, 10 Mar 2025 `[2ce8db]` and 11 Feb 2026 `[590468]`, on ABA's assistant.
12. IBM Institute for Business Value — CEO study, 6 May 2025. https://newsroom.ibm.com/2025-05-06-ibm-study-ceos-double-down-on-ai-while-navigating-enterprise-hurdles `[236153]`
13. Zillow Group Q3 2021 release, 2 Nov 2021 `[391b35]`; Rich Barton's letter, LinkedIn, 2 Nov 2021 `[3e6c0b]`.
14. BCG — "The Widening AI Value Gap", Sep 2025 (PDF) `[7e7dd6]`; BCG press release, 24 Oct 2024.
15. MIT Technology Review, 27 Apr 2020 `[e0619e]`; TechCrunch, 27 Apr 2020 `[db38a0]`; Beede et al., CHI 2020 abstract, research.google `[1fd217]`; Ruamviboonsuk et al., Lancet Digital Health 2022 abstract `[c9edad]`.
16. AMA, 12 Jun 2025 `[1f2945]`; Kaiser Permanente Division of Research, 1 Apr 2025 `[e96f81]`; AMA, 18 Mar 2024 `[0b3137]`; KFF Health News, 27 Jan 2026 `[4fd16d]`; UCLA trial release `[d6212e]`.
17. InvestmentNews, 15 Mar 2023 `[145d70]`; OpenAI case study, Morgan Stanley `[6f75e9]`; Microsoft Work Trend Index, 8 May 2024 `[f1779f]`.
18. Landing AI — Andrew Ng, "AI Transformation Playbook", Dec 2018 `[41bf58]`.
19. Gartner press releases (29 Jul 2024; 26 Feb 2025; Jun 2025), via secondary copies `[89e933]`, `[9c59d7]`, `[b99ebe]`: verify on gartner.com.
20. Microsoft — Cloud Adoption Framework, AI strategy, 9 Oct 2026 `[382100]`.
21. Google Cloud — AI Adoption Framework, 30 Jun 2020 `[12e9f7]`, `[05f377]`.
22. HBR — Israeli and Ascarza, 20 Nov 2025 (teaser only) `[53dcac]`; Mollick, "Making AI Work: Leadership, Lab, and Crowd", 22 May 2025 `[38d83c]`; Wharton and GBK, Oct 2025 `[c1bfd1]`.
23. Medscape, 22 Feb 2017 `[41cc7c]`; Network World, 9 Mar 2017 `[65131c]`; STAT, 5 Sep 2017 `[f92bd7]`.
24. Khmer terms: Ministry of Post and Telecommunications lexicon 2025 `[3f8526]`; AMS `[bd0139]`, `[2edd2e]`; Sabay `[d2843e]`, `[403df5]`; Fresh News `[ad45a1]`, `[3136c6]`; DAP News `[8255ba]`; Khmer Wikipedia (ChatGPT) `[10b40a]`.

Scout ids are in `docs/video-plan-07/sources/` (git-ignored).

## For the YouTube description

1. RAND, "The Root Causes of Failure for Artificial Intelligence Projects and How They Can Succeed" (Aug 2024).
2. Civil Resolution Tribunal of British Columbia, "Moffatt v. Air Canada, 2024 BCCRT 149" (14 Feb 2024).
3. Konrad-Adenauer-Stiftung Cambodia and CADT, "Profiling the AI Readiness Baseline in Cambodia's Manufacturing SMEs" (2026).
4. Microsoft Cloud Adoption Framework, "AI strategy" (start with business problems).
5. Google Research, the Thailand diabetic eye-screening studies (CHI 2020; Lancet Digital Health 2022).
6. Klarna, press release "Klarna AI assistant handles two-thirds of customer service chats in its first month" (27 Feb 2024).

## Before production

The film pipeline that used to live in `storage/` (shared tools `khmer-film/`, the template `love-19-vs-29-doc/`, and `maps-traffic-edu/`) is gone from disk as of 2026-10-14 with no backup, so production started by rebuilding a lean pipeline from my notes in `storage/ai-problem-first-edu/` (script, narration, timeline, Chrome frame renderer, build) with the shared voice rules recreated in `storage/khmer-film/` (`khmer_speech.py` with joined repeats and a `PRON` table, `khmer_phrasing.py` with calm breath stops). The narrator is the user's choice, `flower-wilted-speaker-b`. The working script is `storage/ai-problem-first-edu/script_km.py`: it differs from the lines above only in small ways (a colon after "សំណួរទីមួយ" became a full stop, the two ៗ lines were reworded). The Khmer listen check by the user stays mandatory before the final render. Production builds from the **Story spine**, **Moments**, **Framework** and **Script lines**. Keep a `NOT` table only for the "Handle with care" items: "fired 700", "generative AI" for the chatbot, any single failure rate, "Watson failed", the 60% Telegram figure, adding the decision's fares on screen.
