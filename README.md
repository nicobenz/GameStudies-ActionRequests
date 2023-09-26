# GameStudies-TopicCurves
## What to expect in this repo
Here I investigate if there is a possibility to draw keyword development curves of action request speech acts in video games using game transcripts from [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/). 
Action requests aim to make the player do something, like 'go', 'help', 'talk' or 'find'. 
These speech acts are imperative in a sense but not in a forced way. 
They are like instructions given to the player rather than the players avatar, so they are somewhat meta-narrative while being part of the narration. 

Early assumptions are that verbs like 'talk' might see a falling curve because talking is a big part of character introduction that might be strongest in early and mid parts, while 'help' or 'kill' might have a rising curve because player characters usually rise in power as the game progresses and is more able to perform these tasks. 
I also suspect these verbs differ not only in video games as a whole but also within genres. 
Survival games might have a slower rising curve for 'kill' than shooter games because of the lower power levels of the player character in these type of games. 
So maybe there can be some general and also genre-specific findings.

## TODO:
### Data collection and preparation:
- [x] crawl and clean transcripts from [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/)
- [x] scrape audio files from YouTube channels of non-commented playthroughs like: 
  - [ ] [Gamers Little Playground](https://www.youtube.com/@glp), 
  - [x] [FullPlaythroughs](https://www.youtube.com/@FullPlaythroughs), 
  - [ ] [MKIceAndFire](https://www.youtube.com/@MKIceAndFire) and/or 
  - [ ] [Shirrako](https://www.youtube.com/@Shirrako)
- [ ] transcribe files using OpenAI's Whisper (takes about 10% of file length in base model)
- [ ] genre-tag transcripts
- [ ] merge into transcripts of [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/)

### Processing and analysis:
- [x] use word-level n-grams of variable sizes
- [x] calculate keyword importance for every n-gram using term frequency
- [x] plot relative importance for every keyword for all games and by genre
- [ ] expand analysis to all verbs instead of chosen verbs to avoid bias
- [ ] change preprocessing to only include verbs used in imperative fashion in tf value calculation
- [ ] cluster verbs into synonyms (using cosine similarity on spaCy vectors?)
- [ ] calculate ANOVA or other tests to check for significant differences between genres

## Current challenges
- How to deal with compound verbs in cases like 'I need help!'? This should be considered a synoym to 'Help me!', but a POS tagging approach would exclude this.
- How to account for uneven class distribution? Action adventure is the dominant class with much higher distribution than other genres. Maybe prune this class and raise other genres using SMOTE?
- Should I use the mean curves as a baseline? If the curve for 'kill' is rising in all genres, this way I could see if the curve is rising even stronger in shooter games. Maybe create a residual matrix to see the curves corrected for baseline and perform Monte Carlo Tests for significance testing.
- How to deal with Whisper's hallucinations? Segments keep randomly repeating. Can usually be fixed in postprocessing in cases of full repetition but how to deal with cases like this?
  - [01:40:11.380 --> 01:40:13.380]  Oh, that's a good one!
  - [01:40:13.380 --> 01:40:15.380]  Oh, that was a good one.
- Also, sometimes random characters from other scripts appear in English words:
  - [02:00:54.620 --> 02:00:56.620]  I'm inешema.
  - [01:57:40.340 --> 01:57:42.340]  The flank already美元!
