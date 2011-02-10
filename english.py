import string

class English:
    def __init__(self, thresh=0.7, dic="/usr/share/dict/words"):
        self.dict = {} 
        self.thresh = thresh
        f = open(dic)
        for line in f.readlines():
            line = line.strip()
            if len(line) > 0:
                line = line.lower()
                self.dict[line] = True
   
    def skip_word(self, word):
        if len(word) == 0:
            return True
        if word[0] == '#' or word[0] == '@':
            return True
        if word == 'RT':
            return True
        if word.startswith("http"):
            return True
        return False

    def is_english(self, sentence):
        words = sentence.split(" ")
        words = [word.lower() for word in words if not self.skip_word(word)] 
        exclude = set(string.punctuation)
        words = [''.join(ch for ch in s if ch not in exclude) for s in words]
        
        if len(words) == 0:
            return False

        english = 0
        for word in words:
            if word.lower() in self.dict:
                english += 1
         
        if (float(english) / float(len(words))) > self.thresh:
            return True
        else:
            return False
