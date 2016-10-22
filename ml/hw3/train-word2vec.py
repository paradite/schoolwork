import word2vec

word2vec.word2phrase('train-cleaned.txt', 'train-phrases', verbose=True)

word2vec.word2vec('train-phrases', 'train-100.bin', size=100, verbose=True)

# word2vec.word2clusters('text8', 'text8-clusters.txt', 10, verbose=True)
