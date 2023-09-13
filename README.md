# GameStudies-TopicCurves
Here I investigate if there is a possibility to draw topic curves for video games using game transcripts from [Game Scripts Wiki](https://game-scripts-wiki.blogspot.com/).

## TODO:
- [x] crawl and clean transcripts
- [x] use word-level n-grams with n=1000 (or n = transcript.length / 20?)
- [x] calculate topics and relative topic importance for every n-gram
- [x] track topic movements between n-grams using cosine similarity
- [ ] plot relative importance for every topic
- [ ] use cosine similarity again to map topics between games based on genre
## Current challenge
Tracking topic movement between n-grams through cosine similarity difficult because most topics of an n-gram have a very high similarity with all topics of the following n-gram. No clear tracking of topics over n-grams possible. Maybe there is another way?
