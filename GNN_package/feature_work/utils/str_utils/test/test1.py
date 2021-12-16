num = 0
str1="Thanks! Should I create issue for this PR?\n"
str2="Up to you -- we've fixed it internally and will push it out to the git repo soon :).  Thanks for the typo fix!\n"
str3="Hey webmaven: as mentioned in our [Contribution doc](https://github.com/tensorflow/tensorflow/blob/master/CONTRIBUTING.md), we don't accept pull requests through github yet.  However, if you don't mind, " \
     "I will make these edits internally and update the repository on our next upstream push with credit given to you.\n"
str4="How is this, then?:\nhttps://tensorflow-review.googlesource.com/#/c/1050/\n"
def wordCount(str) -> int:
    num = 0
    if str == '' or str == ' ':
        num = 0
    else:
        num = len(str.strip().split(' '))
    return num
print(wordCount(str1))
print(wordCount(str2))
print(wordCount(str3))
print(wordCount(str4))