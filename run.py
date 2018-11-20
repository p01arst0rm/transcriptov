import Transcriptov

a = Transcriptov.transcriptov()
a.transcript_dir="transcripts/"
a.tweet_state_size=5

a.api_key ="XXXXXXXXX"
a.api_key_secret = "XXXXXXXXX"   
a.access_token = "XXXXXXXXX"    
a.access_token_secret = "XXXXXXXXX"

a.create_tweet()
