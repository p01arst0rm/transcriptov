import sys
import markovify
import glob
import tweepy
import ast




# global variables
#----------------------------------------------------------------------------
api_key ="XXXXXXXXX"
api_key_secret = "XXXXXXXXX"   
access_token = "XXXXXXXXX"    
access_token_secret = "XXXXXXXXX"

notify_log_file = "./transcriptov.log"
warn_log_file = "./transcriptov.log"
err_log_file = "./transcriptov.log"

transcript_dir="transcripts/"
tweet_state_size=2




# Error handler
#----------------------------------------------------------------------------

def log_handle(log, log_file):
        print(log)
        with open(log_file, "a") as x:
            x.write(log + "\n")
   
def log_notify(notif):
        log_handle(str("[INFO]: "+notif),notify_log_file)

def log_warn(warn):
        log_handle(str("[WARNING]: "+warn),warn_log_file)

def log_err(err):
        log_handle(str("[ERROR]: "+err),err_log_file)
        sys.exit()



       
# Twitter handler
#----------------------------------------------------------------------------
def get_api():
        log_notify("Loading api..")
        auth = tweepy.OAuthHandler(api_key, api_key_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        log_notify("..api loaded.")
        return api

def send_tweet(tweet):
        api = get_api()
        try:
                log_notify("Sending tweet..")
                if tweet.strip():
                        api.update_status(status=tweet)
                log_notify("..tweet sent.")
        except tweepy.TweepError as e:
                # format dodgy returns from tweepy api
                err_dict_list = ast.literal_eval(e.response.text)
                # print errors
                for x in err_dict_list['errors']:
                        log_err(str("{} ({})").format(x['message'],x['code']))
        except AttributeError:
                log_err("invalid tweet. (lower tweet_state_size?)")


                       
# file parsing
#---------------------------------------------------------------------------- 
def load_txt_from_dir(file_dir):
        log_notify("fetching transcripts from \"{}\"..".format(transcript_dir))
        file_list = glob.glob(file_dir + '/*.txt')
        if file_list == []:
                log_err(": No text files found in transcript directory")
        else:
                file_list.sort()
                log_notify("..Done.")
                return file_list

def read_file(file_name):
        log_notify("reading file \"{}\"".format(file_name))
        try:
                with open(file_name, "r") as f:
                        f=f.read()
                        return f
        except FileNotFoundError:
                log_warn(str("cannot find file \"{}\"").format(file_name))




# model generation
#----------------------------------------------------------------------------        
def gen_model(file_list):
        index=0
        num_elements=len(file_list)
        model_list=[]
        # generate text models from input files
        while index < num_elements:
                f = read_file(file_list[index])
                text_model = markovify.Text(f, state_size=tweet_state_size)
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
        tweet = text_model.make_short_sentence(280, tries=100)
        
        # send generated tweet
        send_tweet(tweet)



if __name__ == '__main__': main(sys.argv[1:])
