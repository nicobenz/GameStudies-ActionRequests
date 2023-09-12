# GameStudies-TopicCurves
Here I investigate if there is a possibility to draw topic curves for video games using game transcripts from [Game Scripts Wiki].(https://game-scripts-wiki.blogspot.com/).

## TODO:
- [x] crawl and clean transcripts
- [ ] use word-level n-grams with n = transcript.length / 100 (?)
- [ ] calculate topics and relative topic importance for every n-gram
- [ ] track topic movements between n-grams using cosine similarity
- [ ] plot relative importance for every topic
- [ ] use cosine similarity again to map topics between games based on genre
