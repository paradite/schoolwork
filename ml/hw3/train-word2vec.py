import word2vec

word2vec.word2phrase('text8', 'text8-phrases', verbose=True)
word2vec.word2vec('text8-phrases', 'text8.bin', size=100, verbose=True)

# word2vec.word2clusters('text8', 'text8-clusters.txt', 10, verbose=True)

# word2vec.word2phrase('enwik9', 'enwik9-phrases', verbose=True)
# word2vec.word2vec('enwik9-phrases', 'enwik9.bin', size=100, verbose=True)