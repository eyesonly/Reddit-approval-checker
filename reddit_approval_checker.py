#!/usr/bin/env python3
# Approved Submission Checker v1.0 by u/buckrowdy

# Import modules needed for the bot to run.
import praw
import sys
import time
import pdb
import configparser

config = configparser.ConfigParser()
config.read('checker.cfg')

login = config._sections['login']
my_config = config._sections['my_config']


# Define subreddit and bot's comment reply 
sub_name      = my_config['sub_name']
comment_reply = my_config['comment_reply']


# Define how long the bot will sleep before waking up for another pass.
sleep_seconds = 300

#  Define the reddit login.  Fill in your username, pwd, client id, and client secret.
def reddit_login():
	try:
		reddit = praw.Reddit(   
					user_agent = login['user_agent'],
					refresh_token = login['refresh_token'],
                                        username = login['username'],
                                        password = login['password'],
					client_id = login['client_id'],
					client_secret = login['client_secret']
					)
		# connect to the subreddit
		subreddit = reddit.subreddit(sub_name)
	
	except Exception as e:
		print(f'\t### ERROR - Could not login.\n\t{e}')	
	print(f'Logged in as: {reddit.user.me()}')
	return reddit

###  Fetch submissions from r/subreddit/new.
def get_latest_submissions(subreddit):
	submissions = reddit.subreddit(sub_name).new(limit=100)
	return submissions
	

# Process submissions
def check_submissions(submissions):
	try: 
		print(f"Now processing submissions...")
		for submission in submissions:  
			if submission.approved and not submission.removed:
				# Check 100 comments on each submission.  If you need to check more, increase the limit.  Max is 1000.
				submission.comments.replace_more(limit=100)
				for comment in submission.comments.list():
					# Check to see if any of the comments were made by automoderator
					if comment.author == "AutoModerator" and comment.removed == False:
						print(f'Removing automod comment on {submission.id} - {submission.title}')
						comment.mod.remove()                                                
						if comment_reply != "":
							print('Posting mod comment reply...')
							mod_comment = submission.reply(body=comment_reply)
							mod_comment.mod.distinguish(how='yes', sticky=True)  
			
	except Exception as e:
		print(f'\t### ERROR - Something went wrong checking submissions.\n\t{e}')

##############################################
### Bot starts here
if __name__ == '__main__':
	try:
		# Connect to reddit and return the object
		reddit = reddit_login()

		# Connect to the subreddit
		subreddit = reddit.subreddit(sub_name)

	except Exception as e:
		print(f'\t\n### ERROR - Could not connect to reddit.\n\t{e}')
		sys.exit(1)

	# Loop the bot
	while True:
		try:
			# Get the latest submissions after emptying variable
			submissions = None
			submissions = get_latest_submissions(subreddit)
				
		except Exception as e:
			print(f'\t### ERROR - Could not get posts from reddit\n\t{e}')

		# If there are posts, start scanning
		if not submissions is None:

			# Once you have submissions, run  the bot function.
			check_submissions(submissions)

		# Loop every X seconds (5 minutes, currently.)        
		time.sleep(sleep_seconds)
	
