import sys
import markovify
import glob
import tweepy
import ast

# global variables
#----------------------------------------------------------------------------
api_key ="XXXX"
api_key_secret = "XXXX"   
access_token = "XXXX"    
access_token_secret = "XXXX"
transcript_dir="transcripts/"
err_log_file = "./transcriptov.log"

# Error handler
#----------------------------------------------------------------------------
def log_err(err):
        print(err)
        with open(err_log_file, "a") as x:
            x.write(err + "\n")
            
# Twitter handler
#----------------------------------------------------------------------------
def get_api():
        print("[INFO] Loading api..")
        auth = tweepy.OAuthHandler(api_key, api_key_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        print("[INFO] ..api loaded.")
        return api

def send_tweet(tweet):
        api = get_api()
        try:
                print("[INFO] Sending tweet..")
                api.update_status(tweet)
                print("[INFO] ..tweet sent.")
        except tweepy.TweepError as e:
                # format dodgy returns from tweepy api
                err_dict_list = ast.literal_eval(e.response.text)
                # print errors
                for x in err_dict_list['errors']:
                        err_print = str("[ERROR] {}: {}").format(x['code'],x['message'])
                        log_err(err_print)
                       
# file parsing
#---------------------------------------------------------------------------- 
def load_txt_from_dir(file_dir):
        file_list = glob.glob(file_dir + '/*.txt')
        if file_list == []:
                log_err("[ERROR]: No text files found in transcript directory")
                sys.exit()
        else:
                file_list.sort()
                return file_list

def read_file(file_name):
        print(file_name)
        try:
                with open(file_name, "r") as f:
                        f=f.read()
                        return f
        except FileNotFoundError:
                err_print=str("[WARNING]: cannot find file \"{}\"").format(file_name)
                log_err(err_print)

# model generation
#----------------------------------------------------------------------------        
def gen_model(file_list):
        index=0
        num_elements=len(file_list)
        model_list=[]
        # generate text models from input files
        while index < num_elements:
                f = read_file(file_list[index])
                text_model = markovify.Text(f)
                model_list.append(text_model)
                index+=1

        # combine all of the input file text structures
        while len(model_list) > 1:
                model_combo = markovify.combine([ model_list[0], model_list.pop(1) ], [ 1.5, 1 ])
                return model_combo

        # Only one element, return single element
        return model_list[0]

# main
#----------------------------------------------------------------------------
def main(argv):
        # load transcripts from directory
        transcripts = load_txt_from_dir(transcript_dir)

        # generate a text model from transcripts
        text_model = gen_model(transcripts)

        # generate a tweet from the text model
        tweet = text_model.make_short_sentence(280)

        # send generated tweet
        send_tweet(tweet)



if __name__ == '__main__': main(sys.argv[1:])
