# GameStudies-TopicCurves
Here I investigate if there is a possibility to draw keyword development curves of something that I consider 'call to action verbs' in video games using game transcripts from [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/). 
Call to action verbs aim to make the player do something, like 'go', 'help', 'talk' or 'find'. 
These verbs are imperative in a sense but not in a forced way. 
They are like instructions given to the player rather than the players avatar, so they are somewhat meta-narrative while being part of the narration. 

Early assumptions are that verbs like 'talk' might see a falling curve because talking is a big part of character introduction that might be strongest in early and mid parts, while 'help' or 'kill' might have a rising curve because player characters usually rise in power as the game progresses and is more able to perform these tasks. 
I also suspect these verbs differ not only in video games as a whole but also within genres. 
Survival games might have a slower rising curve for 'kill' than shooter because of the lower power levels for the player character in these type of games. 

## TODO:
- [x] crawl and clean transcripts
- [x] use word-level n-grams of variable sizes
- [x] calculate keyword importance for every n-gram using term frequency
- [x] plot relative importance for every keyword for all games and by genre
- [ ] expant analysis to all verbs instead of chosen verbs to avoid bias
- [ ] change preprocessing to only include verbs used in imperative fashion in tf value calculation
- [ ] cluster verbs to treat synonyms as the same verb (using cosine similarity on spaCy vectors?)
- [ ] calculate ANOVA or other tests to check for significant differences between genres
## Current challenge
- How to deal with compound verbs in cases like 'I need help!'? This should be considered a synoym to 'Help me!', but a POS tagging approach would exclude this.
- How to account for uneven class distribution? Action adventure is the dominant class with much higher distribution than other genres. Maybe prune this class and raise other genres using SMOTE?
- Should I use the mean curves as a baseline? If the curve for 'kill' is rising in all genres, this way I could see if the curve is rising even stronger in shooter games. Maybe create a residual matrix to see the curves corrected for baseline and perform Monte Carlo Tests for significance testing.
