import sys
import markovify
import glob
import tweepy
import ast


class transcriptov:

        # Error handler
        #----------------------------------------------------------------------------

        def log_handle(self, log, log_file):
                print(log)
                with open(log_file, "a") as x:
                    x.write(log + "\n")
           
        def log_notify(self, notif):
                self.log_handle(str("[INFO]: "+notif),self.notify_log_file)

        def log_warn(self, warn):
                self.log_handle(str("[WARNING]: "+warn),self.warn_log_file)

        def log_err(self, err):
                self.log_handle(str("[ERROR]: "+err),self.err_log_file)
                sys.exit()



               
        # Twitter handler
        #----------------------------------------------------------------------------
        def get_api(self):
                self.log_notify("Loading api..")
                auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)
                self.api = tweepy.API(auth)
                self.log_notify("..api loaded.")

        def publish_status(self):
                try:
                        self.log_notify("Sending tweet..")
                        if self.tweet.strip():
                                self.api.update_status(status=self.tweet)
                        self.log_notify("..tweet sent.")
                except tweepy.TweepError as e:
                        # format dodgy returns from tweepy api
                        err_dict_list = ast.literal_eval(e.response.text)
                        # print errors
                        for x in err_dict_list['errors']:
                                self.log_err(str("{} ({})").format(x['message'],x['code']))
                except AttributeError:
                        self.log_err("invalid tweet. (lower tweet_state_size?)")

        def gen_tweet(self):
                self.tweet = self.text_model.make_short_sentence(280, tries=100)
                               
        # file parsing
        #---------------------------------------------------------------------------- 
        def load_txt_from_dir(self):
                self.log_notify("fetching transcripts from \"{}\"..".format(self.transcript_dir))
                self.file_list = glob.glob(self.transcript_dir + '/*.txt')
                if self.file_list == []:
                        self.log_err(": No text files found in transcript directory")
                else:
                        self.file_list.sort()
                        self.log_notify("..Done.")

        def read_file(self, file_name):
                self.log_notify("reading file \"{}\"".format(file_name))
                try:
                        with open(file_name, "r", encoding="utf8") as f:
                                f=f.read()
                                return f
                except FileNotFoundError:
                        log_warn(str("cannot find file \"{}\"").format(file_name))




        # model generation
        #----------------------------------------------------------------------------        
        def gen_model(self):
                index=0
                num_elements=len(self.file_list)
                model_list=[]
                # generate text models from input files
                while index < num_elements:
                        f = self.read_file(self.file_list[index])
                        f_model = markovify.Text(f, state_size=self.tweet_state_size)
                        model_list.append(f_model)
                        index+=1

                # combine all of the input file text structures
                
                
                while len(model_list) > 1:
                        model_list[0] = markovify.combine([ model_list[0], model_list.pop(1) ], [ 1.5, 1 ])
                self.text_model = model_list[0]




        # main
        #----------------------------------------------------------------------------
        def create_tweet(self):
                # load transcripts from directory
                self.transcripts = self.load_txt_from_dir()

                # generate a text model from transcripts
                text_model = self.gen_model()
                
                # generate a tweet from the text model
                self.gen_tweet()

                # get auth
                self.get_api()
                
                # send generated tweet
                self.publish_status()

        def create_tweet_cmd(self, argv):
                ## TODO: add variable support
        
                # load transcripts from directory
                self.transcripts = self.load_txt_from_dir()

                # generate a text model from transcripts
                self.gen_model()
                
                # generate a tweet from the text model
                self.gen_tweet()

                # get auth
                self.get_api()
                
                # send generated tweet
                self.publish_status()
                
        def __init__(self):
                self.api_key ="XXXXXXXXX"
                self.api_key_secret = "XXXXXXXXX"   
                self.access_token = "XXXXXXXXX"    
                self.access_token_secret = "XXXXXXXXX"

                self.notify_log_file = "./transcriptov.log"
                self.warn_log_file = "./transcriptov.log"
                self.err_log_file = "./transcriptov.log"

                self.transcript_dir="transcripts/"
                self.tweet_state_size=2

if __name__ == '__main__':
        run =transcriptov()
        run.create_tweet_cmd(sys.argv[1:])
