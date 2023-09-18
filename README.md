# GameStudies-TopicCurves
Here I investigate if there is a possibility to draw keyword development curves of imperative action verbs in video games using game transcripts from [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/).

## TODO:
- [x] crawl and clean transcripts
- [x] use word-level n-grams of variable sizes
- [x] calculate keyword importance for every n-gram using term frequency
- [x] plot relative importance for every keyword for all games and by genre
- [ ] improve preprocessing
## Current challenge
Change preprocessing to only include tokens used as actions verbs in an imperative way, calling the player to do a certain action like "go and talk to the innkeeper", "slay the dragon" or "bring me a shrubbery".
