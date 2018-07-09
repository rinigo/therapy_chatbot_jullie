import pandas as pd
import nltk
from nltk.util import ngrams
import random
# from util import config, log
import slackweb
from common.util.error_msg import error_msg
from nltk.tag.stanford import StanfordPOSTagger
from textblob import Word
# exec(open("./test.py").read())
import string


slack_master = slackweb.Slack(url="https://hooks.slack.com/services/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")
pos_path_jar = "./stanford-postagger-full-2017-06-09/stanford-postagger.jar"
pos_path_model = "./stanford-postagger-full-2017-06-09/models/english-left3words-distsim.tagger"
pos_tagger = StanfordPOSTagger(pos_path_model,pos_path_jar)


nouns = ["NN","NNS","NNP","NNPS"]
prps = ["PRP","PRP$"]
adverbs = ["RB","RBR","RBS"]
adjectives = ["JJ","JJR","JJS"]
verbs = ["VB","VBD","VBG","VBN","VBP","VBZ"]
do_type = ["do","dont","did","didnt","does","doesnt"]
be_type = ["are","arent","were","werent","is","isnt","was","wasnt","am"]
should_type = ["should","better","have to","has to","had to"]
can_type = ["can","could","cant","couldnt"]
think_type = ["think","feel","consider"]
idea_type = ["idea", "opinion","suggestion"]
sp_type1 = ["good","better","best","next","step"]
sp_type2 = ["remember","like","love"]

subj = ""
vbs = ""

# listの要素を複数消すメソッド
def dellist(items, indexes):
     for index in sorted(indexes, reverse=True):
         del items[index]

def tag_sents(text):
    token = nltk.word_tokenize(text)
    #havetoを一まとまりにする処理
    bigram = ngrams(token,2)
    words = [('have', 'to'),('has', 'to'),('had', 'to')]
    idx_haveto = [index for index, value in enumerate(bigram) if value in words]
    num = 0
    for idx in idx_haveto:
        insert_word = token[idx-num] + " " +token[idx+1-num] 
        dellist(token,[idx-num,idx+1-num])
        token.insert(idx-num,insert_word)
        num = num+1
    
    tag_token = pos_tagger.tag(token)
    return tag_token
    
def tag_df(text):
    s_tokenized = nltk.sent_tokenize(str(text))
    matched = []
    for sidx, sent in enumerate(s_tokenized):
        tag_token = tag_sents(sent)
        for widx,word_tag in enumerate(tag_token):
            matched.append([sidx, widx, word_tag[0],word_tag[1]])
    matched = pd.DataFrame(matched)
    matched.columns = ['sidx', 'widx', 'word','tag']
    return matched
    
def fix_tag(matched):
    dic = {'u': 'PRP','i': 'PRP','have to': 'MD','has to': 'MD','had to': 'MD','like': 'VB','know': 'VB','move': 'VB','ask': 'VB','dont': 'RB','don`t': 'RB','didnt': 'RB','did`t': 'RB',"am": 'VB',"get": 'VB'}
    if any(matched["word"].isin(dic.keys())):
        matched.loc[matched["word"].isin(dic.keys()),"tag"] = matched[matched["word"].isin(dic.keys())].apply(lambda row: dic[row["word"]], axis=1)
        return matched
    return matched
#Python3 では * をはさむことで以降の変数はキーワードでしか呼べなくなる。
def change_subj(row,*,q_type=""):
    change = {
        "you":"i",
        "i":"you",
        "we":"you guys",
        "this":"that",
        "these":"those",
        "our":"your",
        "my":"your",
        "me":"you",
        "your":"my",
        "yours":"mine",
    }
    change_exyou = {
        "i":"you",
        "we":"you guys",
        "this":"that",
        "these":"those",
        "our":"your",
        "my":"your",
        "me":"you",
    }
    dic = change_exyou if q_type in {"ADCLW","ADCLWt"} else change
    if row in dic.keys():
        return dic[row]
    return row

#Questionとして反応が必要なセンテンスかどうか判断する
def detect_question(text):
    q_list = {"are","aren't","is","isn't","do","don't","did","didn't","can","can't","could","couldn't","may","might","would","wouldn't","should","have","had","havent","how","what"}
    # clouse_label = {"S","SBAR","SBARQ","SINV","SQ"}
    text = text.lower()
    matched = tag_df(text)
    tokenized = fix_tag(matched)
    global subj
    subj = tokenized[tokenized["tag"].isin(prps+nouns)]
    global vbs
    vbs = tokenized[tokenized["tag"].isin(verbs)]
    if tokenized["word"][len(tokenized)-1] == "?":
        return tokenized
    elif tokenized["word"][0] in q_list:
        return tokenized
    elif tokenized["word"][0] == "you":
        return tokenized
    elif tokenized["word"][len(tokenized)-1] == "right":
        return tokenized
    #一旦はこれでおいとく
    elif tokenized["word"][0] == "i" and vbs["word"].iloc[0] == "know" and any(tokenized["word"][:vbs.index[0]].isin(["dont","don't"])):
        return tokenized
    elif tokenized["word"][0] == "i" and vbs["word"].iloc[0] == "have" and any(tokenized["word"][vbs.index[0]:].isin(["idea"])):
        return tokenized
    else:
        return False            

#have toは一語にまとめる処理してしまうのもあり
def question_type(tokenized):

    #ここではtokenizedの最初にdoがあるか、その後動詞が一つ以上出てくるかを見ている。
    if len(subj) < 1 and len(vbs) < 1:
        # and for what all of that?見たいなのとる
        if any(tokenized["word"].isin(["for"])) and any(tokenized["word"].isin(["what"])):
            for_idx = tokenized[tokenized.isin(["for"])].index
            what_idx = tokenized[tokenized.isin(["what"])].index
            for i in for_idx:
                if any(what_idx[(what_idx-i)]<3):
                    return "OPOPS3"
            else:
                return "F"
        else:
            return "F"
#doで始まるもの    
    elif tokenized["word"][0] in do_type and any(tokenized["tag"][1:].isin(verbs) == True):
        #ここは[1]で取りたいとこ。Do whatever you wanna do?とかが通ってしまうため。
        if tokenized["word"][1] == "you":
            #最初のDOとかがVBになったりなんなかったりするから[1:]でとるDo youの次の最初のVBがthink系の場合
            if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                
                #ここではそもそも主語(名詞)が２個以上あるのか、そして２個目の主語の後に動詞がついているかを判断している
                if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                    #２個目のprp
                    p_idx = subj.index[1]
                    # ２個目のprpよりも後に出てくる動詞の最初(つまり２個目のprpにかかっている動詞を見つけたい)
                    v_idx = vbs[vbs.index>p_idx].index[0]
                    
                    if subj["word"].iloc[1] == "you":
                        if vbs["word"][v_idx] == "would":
                            return "ADCLWt"
                        else:
                            return "F"
                    else:
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                            return "ADCLSt"
                        elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                            return "ADCLCt"
                        else:
                            return "OPCLT"
                #ここは主語が２個以上ないorそのあとに動詞がないものex) so do you feel bad about it?
                else:
                    return "OPCLT"
                    
            elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"agree"}:
                return "OPCLRs"
            
            elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"have"}:
                if any(tokenized["word"].isin(idea_type)):
                    return "ADOPS"
                else:
                    return "JJ"
            elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in sp_type2:
                return "JJ"
            else:
                return "OPCLRs"
        elif tokenized["word"][1] == "i":
            if all(tokenized["tag"].isin(verbs) == False):
                print("NO VB...need to search more")
            elif any(tokenized["word"].isin(should_type+can_type)):
                return "ADCLS"
            else:
                return "OPCLRs"
        else:
            if all(tokenized["tag"].isin(verbs) == False):
                print("NO VB...need to search more")
            elif any(tokenized["word"].isin(should_type+can_type)):
                return "ADCLS"
            else:
                return "OPCLRs"
      
#ここからcan編            
    elif tokenized["word"][0] in can_type and any(tokenized["tag"][1:].isin(verbs) == True):
        if tokenized["word"][1] == "you":
            if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"help","talk","tell","check"}:
                return "OR"
            else:
                return "JJ"
                
        elif tokenized["word"][1] == "i":
            if len(subj) > 1:
                if subj["word"].iloc[1] == "you":
                    return "OR"
                else:
                    return "OPCLRs"
            else:
                return "OR"
        
        elif tokenized["word"][1] == "we":
            return "OR"
        
        else:
            return "ADCLC"


# ここからBe動詞で始まるもの編    
    elif tokenized["word"][0] in be_type:
        if tokenized["word"][1] == "you":
            if any(tokenized["tag"][1:].isin(verbs)) == False:
                return "JJ"
            #crazyとかはvbとしてそもそも扱われないから、youの直後にあるかないかで判断する
            elif tokenized["word"][2] in {"kidding","serious","crazy","insane"}:
                return "RE"
            elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"thinking","feeling","considering"}:
                if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                    p_idx = subj.index[1]
                    v_idx = vbs[vbs.index>p_idx].index[0]
                    
                    if subj["word"].iloc[1] == "you":
                        if vbs["word"][v_idx] == "would":
                            return "ADCLWt"
                        else:
                            return "F"
                    else:
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                            return "ADCLSt"
                            
                        
                        elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                            return "ADCLCt"
                        else:
                            return "OPCLT"
                else:
                    return "OPCLT"
            else:
                return "JJ"
                
        elif tokenized["word"][1] in {"this","here"}:
            if any(tokenized["word"][1:].isin(["safe","annonymous"])):
                return "JJ"
            else:
                if len(vbs)>1:
                    return "OPCLRbe"
                else:
                    return "OPCLRs"
                
        else:
            if len(vbs)>1:
                return "OPCLRbe"
            else:
                return "OPCLRs"

#ここからwhat編
    elif tokenized["word"][0] == "what":
        # what upとかで終わってるものは削除。subj前の
        if any(tokenized["word"][1:subj.index[0]].isin(["if"])):
            return "OPOPS2"
        elif any(tokenized["word"][1:subj.index[0]].isin(["about"])):
            return "OPOPS1"
        elif all(tokenized["tag"].isin(verbs) == False):
            return "F"
        elif len(subj)==0:
            if any(tokenized["word"][:vbs.index[0]].isin(["can","could","should","would","is","was"])):
                return "OPOPS4"
        elif any(tokenized["word"][:subj.index[0]].isin(do_type)):
            #VB２個以上ないなら返す。Do you?とかの場合
            if len(vbs) < 2:
                return "F"
            #２個目のVB前のsubjを見る
            elif any(tokenized["word"][:vbs.index[1]].isin(["you"])):
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                        p_idx = subj.index[1]
                        v_idx = vbs[vbs.index>p_idx].index[0]
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                            return "ADOPWt"
                        #ここwhat do you think about him?とかを予想。what do you like to do?とかくるとちょっと見当違いかな。
                        else:
                            return "OPOPWTs"
                    else:
                        return "OPOPWTs"
                else:
                    return "OPOPWRs"
            elif any(tokenized["word"][:vbs.index[1]].isin(["i"])):
                return "ADOPW"
                
            elif any(tokenized["word"][:vbs.index[1]].isin(["that","it"])):
                if any(tokenized["word"][2:].isin(["mean"])):
                    return "RE"
                else:
                    return "OPOPWRs"
            else:
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    return "OPOPWTs"
                else:
                    return "OPOPWRs"
        elif any(tokenized["word"][:subj.index[0]].isin(can_type)):
            if len(vbs) < 1:
                return "F"
            #最初のVB前のsubjを見る
            if any(tokenized["word"][:vbs.index[0]].isin(["you"])):
                return "JJ"
            elif any(tokenized["word"][:vbs.index[0]].isin(["i"])):
                return "ADOPW"
            elif any(tokenized["word"][:vbs.index[0]].isin(["we"])):
                return "ADOPW"
            else:
                return "ADOPW"
        
        #最初のsbj前にshouldが入っているかどうか検証
        elif any(tokenized["word"][:subj.index[0]].isin(["should"])):
            #最初のshouldの後にsubjがくるかどうか。what should be better?とかはOPOPS4にしたいため
            if any(tokenized["tag"][tokenized["word"][:subj.index[0]].isin(["should"]).index[0]:].isin(prps+nouns)):
                return "ADOPW"
            else:
                return "OPOPS4"
        elif any(tokenized["word"][:subj.index[0]].isin(["would"])):
            if any(tokenized["tag"][:subj.index[0]].isin(verbs)):
                if any(tokenized["word"][:subj.index[0]].isin(["be"])):
                    if any(tokenized["word"][3:].isin(sp_type1)):
                        return "ADOPW"
                    else:
                        return "OPOPS4"
                else:
                    return "OPOPS4"
                    
            elif any(tokenized["word"][:vbs.index[0]].isin(["you"])):
                if tokenized["word"][vbs.index[0]] == "like":
                    return "JJ"
                elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                        p_idx = subj.index[1]
                        v_idx = vbs[vbs.index>p_idx].index[0]
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                            return "ADOPWt"
                        #ここwhat do you think about him?とかを予想。what do you like to do?とかくるとちょっと見当違いかな。
                        else:
                            return "OPOPWTs"
                    else:
                        return "OPOPWTs"
                else:
                    return "ADOPW"
                
            else:
                return "OPOPWRs"
                
        #what is thisとかのタイプ        
        elif any(tokenized["word"][1:subj.index[0]].isin(be_type)):
            #what is the best action とか what is good for herとか
            if any(tokenized["word"][:subj.index[0]].isin(sp_type1)):
                return "ADOPW"
        
            elif any(tokenized["word"][:vbs.index[1]].isin(["you"])):
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"thinking","feeling","considering"}:
                    if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                        p_idx = subj.index[1]
                        v_idx = vbs[vbs.index>p_idx].index[0]
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                            return "ADOPWt"
                        else:
                            return "OPOPWTbe"
                    else:
                        return "OPOPWTbe"
                else:
                    return "JJ"
            elif any(tokenized["word"][:vbs.index[1]].isin(["i"])):
                return "ADOPW"
                
            else:
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    return "OPOPWTbe"
                else:
                    return "OPOPWRbe"
        
        else:
            return "F"


    #ここからHow編
    elif tokenized["word"][0] == "how":
        # what upとかで終わってるものは削除。subj前の
        if all(tokenized["tag"].isin(verbs) == False):
            return "F"
        elif len(subj)==0:
            if any(tokenized["word"][:vbs.index[0]].isin(["can","could","should","would","is","was"])):
                return "OPOPS4"
        elif any(tokenized["word"][:subj.index[0]].isin(do_type)):
            if len(vbs) < 2:
                return "F"
            else:
                vb_idx1 = tokenized["word"][:vbs.index[1]]
                #２個目のVB前のsubjを見る
                if any(vb_idx1.isin(["you"])):
                    if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                        if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                            p_idx = subj.index[1]
                            v_idx = vbs[vbs.index>p_idx].index[0]
                            
                            if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                                return "ADOPHt"
                            #ここwhat do you think about him?とかを予想。what do you like to do?とかくるとちょっと見当違いかな。
                            else:
                                return "OPOPHTs"
                        else:
                            return "OPOPHRs"
                    else:
                        return "OPOPHRs"
                elif any(vb_idx1.isin(["i"])):
                    #iの後につくVBで一番iに近いものを見てる
                    i_idx = vb_idx1[vb_idx1.isin(["i"])].index[0]
                    if vbs[vbs.index>i_idx]["word"].iloc[0] in {"know","assure","feel"}:
                        # 上記know,assure系の後に下記ワード入っているかだけチェック
                        if any(tokenized["word"][vbs[i_idx:].index[0]:].isin({"you","safe"})):
                            return "JJ"
                        else:
                            return "ADOPH"
                    else:
                        return "ADOPH"
                    
                elif any(vb_idx1.isin(["this"])):
                    if vbs.iloc[1] in {"work"}:
                        return "JJ"
                    else:
                        return "OPOPHRs"
                else:
                    if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                        return "OPOPHTs"
                    else:
                        return "OPOPHRs"
                    
        elif any(tokenized["word"][:subj.index[0]].isin(can_type)):
            if len(vbs) < 1:
                return "F"
            #最初のVB前のsubjを見る
            if any(tokenized["word"][:vbs.index[0]].isin(["you"])):
                return "JJ"
            elif any(tokenized["word"][:vbs.index[0]].isin(["i"])):
                return "ADOPH"
            elif any(tokenized["word"][:vbs.index[0]].isin(["we"])):
                return "ADOPH"
            elif any(tokenized["tag"][:vbs.index[0]].isin(verbs)):
                return "OPOPS4"
            else:
                return "ADOPH"
        
        #最初のsbj前にshouldが入っているかどうか検証
        elif any(tokenized["word"][:subj.index[0]].isin(["should"])):
            #最初のshouldの後にsubjがくるかどうか。what should be better?とかはOPOPS4にしたいため
            if any(tokenized["tag"][tokenized["word"][:subj.index[0]].isin(["should"]).index[0]:].isin(prps+nouns)):
                return "ADOPH"
            else:
                return "OPOPS4"
        elif any(tokenized["word"][:subj.index[0]].isin(["would"])):
            if any(tokenized["tag"][:subj.index[0]].isin(verbs)):
                if any(tokenized["word"][:subj.index[0]].isin(["be"])):
                    if any(tokenized["word"][3:].isin(sp_type1)):
                        return "ADOPH"
                    else:
                        return "OPOPS4"
                else:
                    return "OPOPS4"
                    
            elif any(tokenized["word"][:vbs.index[0]].isin(["you"])):
                if tokenized["word"][vbs.index[0]] == "like":
                    return "JJ"
                elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                        p_idx = subj.index[1]
                        v_idx = vbs[vbs.index>p_idx].index[0]
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                            return "ADOPHt"
                        #ここwhat do you think about him?とかを予想。what do you like to do?とかくるとちょっと見当違いかな。
                        else:
                            return "OPOPHTs"
                    else:
                        return "OPOPHTs"
                else:
                    return "ADOPH"
                
            else:
                return "OPOPHR"
                
                
        elif any(tokenized["word"][1:subj.index[0]].isin(be_type)):
            #what is the best action とか what is good for herとか
            if any(tokenized["word"][:subj.index[0]].isin(sp_type1)):
                return "ADOPH"
        
            elif any(tokenized["word"][:vbs.index[1]].isin(["you"])):
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"thinking","feeling","considering"}:
                    if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                        p_idx = subj.index[1]
                        v_idx = vbs[vbs.index>p_idx].index[0]
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type+can_type)):
                            return "ADOPHt"
                        else:
                            return "OPOPHTbe"
                    else:
                        return "OPOPHTbe"
                else:
                    return "JJ"
            elif any(tokenized["word"][:vbs.index[1]].isin(["i"])):
                return "ADOPH"
                
            else:
                if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                    return "OPOPHTbe"
                else:
                    return "OPOPHRbe"
                    
        elif any(tokenized["word"][1:subj.index[0]].isin(["about"])):
            return "OPOPS1"
        
        else:
            return "F"
    
    #whyで始まるもの
    elif tokenized["word"][0] == "why":
        if len(subj)>0 and len(vbs)>0:
            if vbs["word"].iloc[0] in be_type:
                return "OPOPYbe"
            else:
                return "OPOPYs"
        else:
            return "F"
            
    #wouldで始まるもの
    elif tokenized["word"][0] == "would":
        if tokenized["word"][1] == "you":
            if vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
                #ここではそもそも主語が１個以上あるのか、そして２個目の主語の後に動詞がついているかを判断している
                if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                    #２個目のprp
                    p_idx = subj.index[1]
                    # ２個目のprpよりも後に出てくる動詞の最初(つまり２個目のprpにかかっている動詞を見つけたい)
                    v_idx = vbs[vbs.index>p_idx].index[0]
                    
                    if subj["word"].iloc[1] == "you":
                        #２個目のPRPとその次の動詞の間にwouldがあるかどうか
                        if vbs["word"][p_idx:v_idx].isin({"would"}):
                            return "ADCLWt"
                        else:
                            return "F"
                    else:
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                            return "ADCLSt"
                    
                        elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                            return "ADCLCt"
                        else:
                            return "OPCLT"
                else:
                    return "OPCLT"
                    
            elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in sp_type2:
                return "JJ"
            else:
                return "ADCLW"
        else:
            if any(tokenized["word"].isin(should_type)):
                return "ADCLS"
            else:
                return "OPCLRs"
    #shouldで始まるもの
    elif tokenized["word"][0] == "should":
        return "ADCLS"
        
    #youで始まるもの。ここから平叙文編
    elif tokenized["word"][0] == "you":
        if len(vbs)<1:
            return "F"
        elif any(tokenized["word"][:vbs.index[0]].isin(can_type)):
            if vbs["word"].iloc[0] in {"help","talk","tell","check"}:
                return "OR"
            else:
                return "JJ"
        elif any(tokenized["word"][:vbs.index[0]].isin({"would"})):
            if vbs["word"][0] in think_type:
                #ここではそもそも主語が１個以上あるのか、そして２個目の主語の後に動詞がついているかを判断している
                if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                    #２個目のprp
                    p_idx = subj.index[1]
                    # ２個目のprpよりも後に出てくる動詞の最初(つまり２個目のprpにかかっている動詞を見つけたい)
                    v_idx = vbs[vbs.index>p_idx].index[0]
                    if subj["word"].iloc[1] == "you":
                        if vbs["word"][v_idx] == "would":
                            return "ADCLWt"
                        else:
                            return "F"
                    else:
                        
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                            return "ADCLSt"
                        
                        elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                            return "ADCLCt"
                        else:
                            return "OPCLT"
                else:
                    return "OPCLT"
            elif vbs["word"][0] == "like":
                return "JJ"
            else:
                return "ADCLW"
            
        elif vbs["word"].iloc[0] in {"are","were"}:
            #crazyとか形容詞系はareの直後にきてるかどうかで判断
            if tokenized["word"][vbs.index[0]+1] in {"kidding","serious","crazy","insane"}:
                return "RE"
            #you are thinkingで始まる場合
            elif vbs["word"][1] in {"thinking","feeling","considering"}:
                if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                    p_idx = subj.index[1]
                    v_idx = vbs[vbs.index>p_idx].index[0]
                    
                    if subj["word"].iloc[1] == "you":
                        if vbs["word"][v_idx] == "would":
                            return "ADCLWt"
                        else:
                            return "F"
                    else:
                        if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                            return "ADCLSt"
                    
                        elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                            return "ADCLCt"
                        else:
                            return "OPCLT"
                else:
                    return "OPCLT"
            else:
                return "JJ"
        elif tokenized["word"][1] in {"kidding","serious","crazy","insane"}:
            return "RE"
            
        elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in think_type:
            #ここではそもそも主語が１個以上あるのか、そして２個目の主語の後に動詞がついているかを判断している
            if len(subj) > 1 and vbs.index[len(vbs)-1] > subj.index[1]:
                #２個目のprp
                p_idx = subj.index[1]
                # ２個目のprpよりも後に出てくる動詞の最初(つまり２個目のprpにかかっている動詞を見つけたい)
                v_idx = vbs[vbs.index>p_idx].index[0]
                
                if subj["word"].iloc[1] == "you":
                    if vbs["word"][v_idx] == "would":
                        return "ADCLWt"
                    else:
                        return "F"
                else:
                    
                    if any(tokenized["word"][p_idx:v_idx].isin(should_type)):
                        return "ADCLSt"
                    
                    elif any(tokenized["word"][p_idx:v_idx].isin(can_type)):
                        return "ADCLCt"
                    else:
                        return "OPCLT"
            else:
                return "OPCLT"
        
        elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"agree"}:
            return "OPCLRs"
        
        elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in {"have"}:
            if any(tokenized["word"].isin(idea_type)):
                return "ADOPS"
            else:
                return "JJ"
        elif vbs[vbs.index>subj.index[0]]["word"].iloc[0] in sp_type2:
            return "JJ"
        else:
            return "OPCLRs"
                
    #iで始まるもの。
    elif tokenized.loc[0,"word"] == "i":
        #最初の動詞がknowで、且つその前にdontが入っていた場合
        if vbs["word"].iloc[0] == "know" and any(tokenized.loc[:vbs.index[0],"word"].isin(["dont","don't"])):
            if tokenized["word"][vbs.index[0]+1] == "if":
                md = tokenized["word"][tokenized["word"][vbs.index[0]+1:].isin(should_type+can_type).index[0]]
                if md == "can":
                    return "ADCLCd"
                else:
                    return "ADCLSd"
                
            elif tokenized.loc[vbs.index[0]+1,"word"] == "what":
                return "ADOPWd"
            elif tokenized.loc[vbs.index[0]+1,"word"] == "how":
                return "ADOPHd"
        #i have no idea と i dont have any idea how/whatを検知        
        elif vbs["word"].iloc[0] == "have" and any(tokenized.loc[vbs.index[0]:,"word"].isin(["idea"])):
            if any(tokenized["word"][:vbs.index[0]].isin(["dont","don't"])) or any(tokenized["word"][vbs.index[0]:tokenized[tokenized["word"]=="idea"].index[0]].isin(["no"])):
                if tokenized["word"][len(tokenized)-1] == "idea":
                    return "ADOPS"
                elif tokenized.loc[tokenized[tokenized["word"]=="idea"].index[0]+1,"word"] == "how":
                    return "ADOPHd"
                elif tokenized.loc[tokenized[tokenized["word"]=="idea"].index[0]+1,"word"] == "what":
                    return "ADOPWd"
                    
        elif any(tokenized.loc[:vbs.index[0],"word"].isin(["can"])):
            if len(subj) > 1:
                if subj["word"].iloc[1] == "you":
                    return "OR"
                else:
                    return "OPCLRs"
            else:
                return "OR"
        
        elif vbs["word"].iloc[0] in {"am","was"}:
            return "OPCLRbe"
    
        elif any(tokenized["word"].isin(should_type)):
            return "ADCLS"
        else:
            return "OPCLRs"
    
    #ここまで引っかからなかったけどsubjectがVBの前にある場合(she,they,my friendとかで始まる場合)        
    elif len(vbs)>0 and len(subj)>0 and subj.index[0] < vbs.index[0]:
        if any(tokenized.loc[:vbs.index[0],"word"].isin(["can"])):
            return "ADCLC"
        elif vbs["word"].iloc[0] in be_type:
            return "OPCLRbe"
        elif any(tokenized["word"].isin(should_type)):
            return "ADCLS"
        else:
            return "OPCLRs"
    elif len(subj)>0:
        if any(tokenized["word"].isin(["any"])) and any(tokenized["word"].isin(["idea","suggestion","solution"])):
            return "ADOPS"
            
        
    else:
        return "F"


#ADSHを変換するやつ
def rep(tokenized,q_type):
    def parse_sent(q_type,tokenized):
        #通常のdo系
        def svo_s(tokenized):
            tokenized["word"] = tokenized.apply(lambda row: change_subj(row["word"]),axis=1)
            subject = tokenized["word"][subj.index[0]]
            vb = vbs["word"].ix[subj.index[0]:]
            verb = vb.iloc[0]
            if tokenized.loc[len(tokenized)-1,"word"] == "?":
                tokenized = tokenized.drop(len(tokenized)-1)
            obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][vb.index[0]+1:]]).strip()
            df = pd.DataFrame({"subject":[subject],"verb":[verb],"objective":obj})
            return df
        #think系    
        def svo_t(tokenized):
            tokenized["word"] = tokenized.apply(lambda row: change_subj(row["word"]),axis=1)
            print(tokenized)
            subject = tokenized["word"][subj.index[1]]
            vb = vbs["word"].ix[subj.index[1]:]
            verb = vb.iloc[0]
            if tokenized.loc[len(tokenized)-1,"word"] == "?":
                tokenized = tokenized.drop(len(tokenized)-1)
            obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][vb.index[0]+1:]]).strip()
            df = pd.DataFrame({"subject":[subject],"verb":[verb],"objective":obj})
            return df
        #be動詞系 are you thinking or you are thinking
        def svo_be(tokenized):
            tokenized["word"] = tokenized.apply(lambda row: change_subj(row["word"]),axis=1)
            subject = tokenized["word"][subj.index[0]]
            verb = vbs["word"].iloc[0]
            #are you の場合とyou are の場合でobjectiveとるindex変わってくる
            drop_num = vbs.index[0] if vbs.index[0]>subj.index[0] else subj.index[0]
            if tokenized.loc[len(tokenized)-1,"word"] == "?":
                tokenized = tokenized.drop(len(tokenized)-1)
            obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][drop_num+1:]]).strip()
            df = pd.DataFrame({"subject":[subject],"verb":[verb],"objective":obj})
            return df
        
        #i dont know if i should do thatとか
        def svo_d(tokenized):
            kw_idx = tokenized[tokenized["word"].isin(["how","what","if"])].index[0]
            kw = tokenized.loc[kw_idx,"word"]
            if kw  == "if":
                df = svo_s(tokenized[kw_idx+1:].reset_index())
                return df
            elif kw in {"what","how"}:
                if tokenized.loc[kw_idx+1,"word"] == "to":
                    subject = "you"
                    #toのあとの動詞から全て引っこぬく
                    vb = tokenized.loc[kw_idx+1:,"word"][tokenized["tag"][kw_idx+1:].isin(verbs)]
                    verb = vb.iloc[0]
                    obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][vb.index[0]+1:]]).strip()
                    df = pd.DataFrame({"subject":[subject],"verb":[verb],"objective":obj})
                    return df
                else:
                    df = svo_s(tokenized[kw_idx+1:].reset_index())
                    return df
            else:
                print("EXCEPTION HAPPEN AT SVO_D")
        #you would or would you or do you think you would
        def svo_w(tokenized):
            tokenized["word"] = tokenized.apply(lambda row: change_subj(row["word"],q_type=q_type),axis=1)
            subject = "you"
            #do you think you wouldの場合２個目のyouからとる
            if q_type == "ADCLWt":
                vb = vbs.ix[subj[subj["word"]=="you"].index[1]:]
            else:
                vb = vbs.ix[subj[subj["word"]=="you"].index[0]:]
            verb = vb["word"].iloc[0]
            obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][vb.index[0]+1:]]).strip()
            df = pd.DataFrame({"subject":[subject],"verb":[verb],"objective":obj})
            return df
        #for special types    
        def s1(tokenized):
            tokenized["word"] = tokenized.apply(lambda row: change_subj(row["word"]),axis=1)
            drop_num = tokenized[tokenized["word"].isin(["what","how"])].index[0]
            obj = "".join([" "+i if not i.startswith("'") and i not in string.punctuation else i for i in tokenized["word"][vb.index[0]+1:]]).strip()
            df = pd.DataFrame({"subject":["hoge"],"verb":["hoge"],"objective":obj})
            return df
        
   
        
        if q_type in {"ADOPW","ADOPH","ADCLS","ADCLC","OPCLRs","OPOPTs","OPOPWRs","OPOPHRs","OPOPWTs","OPOPHTs","OPOPYs"}:
            df = svo_s(tokenized)
            return df
 
        elif q_type in {"ADCLSt","ADCLCt","ADOPWt","ADOPHd","OPCLT"}:
            df = svo_t(tokenized)
            return df
        elif q_type in {"OPCLRbe","OPOPTbe","OPOPWRbe","OPOPHRbe","OPOPWTbe","OPOPHTbe","OPOPYbe"}:
            df = svo_be(tokenized)
            return df
        elif q_type in {"OPOPS1","OPOPS2","OPOPS4"}:
            df = s1(tokenized)
            return df
        elif q_type in {"ADCLSd","ADCLCd","ADOPWd","ADOPHd"}:
            df = svo_d(tokenized)
            return df
        elif q_type in {"ADCLW","ADCLWt"}:
            df = svo_w(tokenized)
            return df
        else:
            df = pd.DataFrame({"subject":["hoge"],"verb":["hoge" ],"objective":["hoge"]})
            return df
        
     #上記でsvo分けしたdfを受け取り、主語に合わせて動詞を複数形単数形変換。returnでは動詞の原型と、主語に合わせた形の両方を返す。
    def change_verb_form(df):
        sub = df["subject"].values[0]
        verb = df["verb"].values[0]
        v_pos = vbs["tag"][vbs["word"]==verb].iloc[0]
        v1 = Word(verb).lemmatize("v")
        #be動詞かどうか
        if verb in {"be","am","are","is","was","were"}:
            if v_pos in {"VBG","VBD"}:
                if sub in {"you","they","we"}:
                    v2 = "were"
                else:
                    v2 = "was"
            else:
                if sub in {"i"}:
                    v2 = "am"
                elif sub in {"you","they","we"}:
                    v2 = "are"
                else:
                    v2 = "is"
            
        else:
            if v_pos in {"VBG","VBD"}:
                #普通の動詞で過去形だった場合そのまま返す
                v2 = verb
            else:
                if sub in {"i","you","they","we"}:
                    #主語が上記で動詞がbe動詞でも無く過去形でもない場合はその動詞の原型がv2
                    v2 = v1
                else:
                    #主語がsheとかの場合、一旦原型に戻したものを複数形にして返す
                    v2 = Word(v1).pluralize()
        
        verbs = [v1,v2]
        return verbs
        
    if q_type in {"ADOPS"}:
        repeat_ADOPS = [
        "Okay, so you dont know what to do now",
        "seems you have no idea to do at all but dont worry.",
        ]
        answer_ADOPS = [
        "Lets think about it together...we still have time.",
        "is there anything in your mind now?",
        ]
        r_num = random.randint(0,len(repeat_ADOPS)-1)
        a_num = random.randint(0,len(answer_ADOPS)-1)
        rep = [repeat_ADOPS[r_num],answer_ADOPS[a_num]]
        return rep
    elif q_type in {"JJ","OR","RE","F"}:
        return None
    
    s_c = ""
    w_h = ""
    df = parse_sent(q_type,tokenized)
    verbs = change_verb_form(df)
    s = df["subject"].values[0]
    #動詞の原型。元がwasならbeが入る
    v_original = verbs[0]
    v = verbs[1]
    o = df["objective"].values[0]
    if q_type in {"ADOPW","ADOPWt","ADOPWd"}:
        category = "ADOPW"
    elif q_type in {"ADOPH","ADOPHt","ADOPHd"}:
        category = "ADOPH"
    elif q_type in {"ADCLW","ADCLWt"}:
        s_c = "better"
        category = "ADCL"
    elif q_type in {"ADCLS","ADCLSt","ADCLSd"}:
        s_c = "should"
        category = "ADCL"
    elif q_type in {"ADCLC","ADCLCt","ADCLCd"}:
        s_c = "can"
        category = "ADCL"
    elif q_type in {"OPCLT"}:
        category = "OPCLT"
    elif q_type in {"OPCLRs","OPCLRbe"}:
        category = "OPCLR"
    elif q_type in {"OPOPWRs","OPOPWRbe"}:
        w_h = "what"
        category = "OPOPWHR"
    elif q_type in {"OPOPHRs","OPOPHRbe"}:
        w_h = "how"
        category = "OPOPWHR"
    elif q_type in {"OPOPWTs","OPOPWTbe"}:
        w_h = "what"
        category = "OPOPWHT"
    elif q_type in {"OPOPHTs","OPOPHTbe"}:
        w_h = "how"
        category = "OPOPWHT"
    elif q_type in {"OPOPYs","OPOPYbe"}:
        category = "OPOPY"
    elif q_type in {"OPOPS1","OPOPS2","OPOPS3","OPOPS4"}:
        category = q_type
    
    svo = " "+s+" "+v+" "+o
    vo = " "+v_original+" "+o
    ssvo = " "+s+" "+s_c+" "+v_original+" "+o
    smvo = " "+s+" "+"might"+" "+v_original+" "+o
    repeat = {
        "ADOPW":[
        "i see sounds like you are seeking for what to"+vo,
        "got it. so you wanna know what"+svo,
        "okay sounds like you have no idea what to"+vo,
        ],
        "ADOPH":[
        "i see sounds like you are seeking for the way to"+vo,
        "got it. so you wanna know how"+svo,
        "okay sounds like you have no idea how to"+vo,
        "right so you are thinking of how"+svo,
        ],
        "ADCL":[
        "sounds bit hard for you to decide if"+ssvo +" "+"now",
        "sounds you are not sure if"+ssvo,
        "so you cant make up your mind if"+ssvo,
        "okay, you are thinking"+ssvo,
        ],
        "OPCLT":[
        "so you wanna know whether"+svo+" "+"or not",
        "well sounds you are feeling"+svo,
        ],
        "OPCLR":[
        "so you are trying to know whether"+svo+" "+"or not",
        "well sounds like you are feeling"+svo,
        ],
        "OPOPWHR":[
        "so you wanna know"+" "+w_h+svo,
        "i see sounds like you are thinking of"+" "+w_h+svo,
        ],
        "OPOPWHT":[
        "so you wanna know"+" "+w_h+svo,
        "ok you are asking me"+" "+w_h+svo,
        ],
        "OPOPY":[
        "so you wanna know why"+svo,
        "i see sounds like you are seeking the reason why"+svo,
        ],
        "OPOPS1":[
        "oh you are asking"+" "+o,
        ],
        "OPOPS2":[
        "any idea to do"+" "+o,
        ],
        "OPOPS3":[
        "well you wanna know the reason right",
        ],
        "OPOPS4":[
        "well..",
        ]}
    answer= {
        "ADOPW":[
        "Is there any idea what to"+vo+"?",
        "Anything in your mind to"+vo+"?",
        "What would your friends"+vo+"?",
        "What would your friend do in the situation?",
        "can you tell me anything in your mind about it now? like any idea is fine! also i can wait for it!",
        "lets think about it together… i know its hard but just let me know if you get any idea!",
        ],
        "ADOPH":[
        "Is there any idea how to"+vo+"?",
        "Anything in your mind how to"+vo+"?",
        "How would your friends"+vo+"?",
        "How would your friend do in the situation?",
        "can you tell me anything in your mind about it now? like any idea is fine! also i can wait for it!",
        "lets think about it together… i know its hard but just let me know if you get any idea!",
        ],    
        "ADCL":[
        "Is there any reason"+ssvo+"?",
        "why do you think"+ssvo+"?",
        "what makes you feel"+ssvo+"?",
        "Lets think about Good side and Bad side of it.. whats is the good side should be if"+svo+"?",
        "what would be a problem if"+svo+"?",
        "how would you feel if"+svo+"?",
        "let me ask you.. do you wanna"+vo+"?",
        "well, just let me ask you. are you willing to"+vo+"?",
        "do you have any other option than that"+svo+"?",
        "is there any other idea than that"+svo+"?",
        ],
        "OPCLT":[
        "why do you think"+smvo,
        "is there any reason you think"+smvo,
        "what if"+svo,
        "what would you feel if"+svo,
        "let me ask you whether you think"+svo,
        "can i ask you if you think"+svo,
        ],
    
        "OPCLR":[
        "why do you think"+smvo,
        "is there any reason you think"+smvo,
        "what if"+svo,
        "what would you feel if"+svo,
        "let me ask you whether you think"+svo,
        "can i ask you if you think"+svo,
        ],
    
        "OPOPWHR":[
        w_h+" "+"do you think"+svo+"?",
        "can you imagine"+" "+w_h+svo+"?"
        ],
    
        "OPOPWHT":[
        "can you guess "+w_h+svo+"?",
        w_h+" "+"would your friend"+vo+"?",
        ],
   
        "OPOPY":[
        "is there any reason you can come up?",
        "what would your friend say about the reason?",
        "why do you think"+svo+"?",
        ],
        "OPOPS1":[
        "well, what do you think about that?",
        ],
   
        "OPOPS2":[
        "would you do anything"+" "+o,
        ],
    
        "OPOPS3":[
        "Any reason you can come up?",
        "i am not sure the reason, but any idea?",
        ],
        "OPOPS4":[
        "i am not sure...is there anything"+" "+o,
        "i have no idea, anything"+" "+o,
        ]}
    
    # global category
    r_num = random.randint(0,len(repeat[category])-1)
    a_num = random.randint(0,len(answer[category])-1)
    
    return [repeat[category][r_num], answer[category][a_num]]


#これが本番用　エラー時はNone流すけどエラー文は出してslackに送る！
def question(text):
    try:
        tokenized = detect_question(text)
        print(tokenized)
    except :
        error_list = error_msg(text=text)
        slack_master.notify(text=error_list[0])
        print(error_list[0])
        return None
    else:
        if type(tokenized)!=bool:
            #リピートとアンサー両方入っている
            try:
                q_type = question_type(tokenized)
                if q_type == None:
                    q_type = "F"
                print(q_type)
            except:
                error_list = error_msg(text=text)
                slack_master.notify(text=error_list[0])
                print(error_list[0])
                return None
                # print(hoge)
            else:
                if q_type != None:
                    try:
                        rep_ans = rep(tokenized,q_type)
                    except:
                        error_list = error_msg(text=text)
                        slack_master.notify(text=error_list[0])
                        print(error_list[0])
                        return None
                        
                    #まだ反応できないやつはNoneにしている。Noneのものは通常のリピートに回す。
                    else:
                        if rep_ans != None:
                            return rep_ans
                        else:
                            print(3)
                            return None
                else:
                    print(2)
                    return None
        else:
            print(1)
            return None

# df = question("do you think i should do that to this?")
# print(df)



