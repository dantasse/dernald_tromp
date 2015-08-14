#!/usr/bin/env python

# Follows Donald Trump's twitter, and just tweets out what he says, misspelled,
# meme-ified.

import argparse, random, ConfigParser, os, PIL, StringIO, time, datetime, string
from PIL import Image, ImageFont, ImageDraw
from collections import defaultdict
from twython import Twython
import twython.exceptions

config = ConfigParser.ConfigParser()
config.read('config.txt')
POST_URL = 'https://api.twitter.com/1.1/statuses/update.json'
OAUTH_KEYS = {'consumer_key': config.get('twitter', 'consumer_key'),
              'consumer_secret': config.get('twitter', 'consumer_secret'),
              'access_token_key': config.get('twitter', 'access_token_key'),
              'access_token_secret': config.get('twitter', 'access_token_secret')}

IMPACT = "Impact.ttf"
twitter = Twython(OAUTH_KEYS['consumer_key'], OAUTH_KEYS['consumer_secret'],
    OAUTH_KEYS['access_token_key'], OAUTH_KEYS['access_token_secret'])

# Lookup table to translate phones to letters.
phone_lookup = {
    'AA':['AH', 'AW', 'AR', 'ER', 'OH'],
    'AE':['A', 'AA', 'EH', 'AH'],
    'AH':['AH', 'EH', 'OH', 'UH', 'AR'],
    'AO':['AW', 'OH', 'UH'],
    'AW':['OW', 'OO', 'AW'],
    'AY':['I', 'IE', 'AY'],
    'B': ['B', 'P', 'D'],
    'CH':['CH', 'SH', 'K'],
    'D': ['D', 'T', 'TH'],
    'DH':['DH', 'TH'],
    'EH':['E', 'UH', 'ER', 'EH', 'I', 'O'],
    'ER':['ER', 'AR', 'OR'],
    'EY':['A', 'A', 'EY'],
    'F': ['F', 'V'],
    'G': ['G', 'G', 'GH'],
    'HH':['H', 'H', 'CH'],
    'IH':['I', 'A', 'UH'],
    'IY':['I', 'EE', 'AY'],
    'JH':['J', 'G', 'Z'],
    'K': ['K', 'C'],
    'L': ['L', 'L', 'LL'],
    'M': ['M', 'N'],
    'N': ['N', 'M'],
    'NG':['NG', 'N', 'NN'],
    'OW':['O', 'OH', 'OW', 'YO'],
    'OY':['OY', 'OI', 'UI'],
    'P': ['P', 'B'],
    'R': ['R'],
    'S': ['S', 'S', 'SH', 'Z', 'Z'],
    'SH':['SH', 'CH'],
    'T': ['T', 'D', 'TH'],
    'TH':['TH', 'T', 'D'],
    'UH':['OO', 'UH', 'OU'],
    'UW':['OO', 'U', 'UE'],
    'V': ['V', 'B', 'F'],
    'W': ['W', 'V'],
    'Y': ['Y', 'EEY'],
    'Z': ['Z', 'ZH', 'TH'],
    'ZH':['ZH', 'SH', 'CH'],
}

# Given a phone (like "IY2" or "HH") returns letters that might somehow
# represent it in a word, in a goofy sort of way.
def get_letter(phone, weirdness=1):
    phone = phone.strip('012') # Ignore stresses, at least for now.
    possible_letters = phone_lookup[phone][:] # Slice to copy.
    # Copy early letters to make them more likely.
    for i in range(15 - weirdness):
        possible_letters.extend(possible_letters[0:1])
    # for i in range(len(possible_letters)):
    #     possible_letters.extend(possible_letters[0:i])
    return random.sample(possible_letters, 1)[0]

# Returns a misspelled (but sort of pronounced the same) version of the text.
# weirdness is on a scale from 1-5.
def misspell(text, pronouncing_dictionary, weirdness=1):
    exclude = set(string.punctuation)
    misspelled = []
    for word in text.split(' '):
        word = ''.join(ch for ch in word if ch not in exclude)
        if word.upper() not in pronouncing_dictionary:
            misspelled.append(word.upper())
        else:
            letters = ''
            for phone in pronounce[word.upper()]:
                # if phone.endswith('0') and not phone.startswith('ER') and random.random() < .25:
                #     continue # skip 25% of unstressed vowels, funnier that way.
                    # but don't skip ERs, they are important. and usually funny.
                letters += get_letter(phone, weirdness)
            misspelled.append(letters)
    return ' '.join(misspelled)

# Given a correctly-spelled word and a made-up spelling, returns a meme image.
def make_image(text, image_filename):
    textlower = text.lower().replace(' ', '_')
    print textlower
    # possible_files = [f for f in os.listdir(args.images_dir) if '_'.join(f.split('_')[:-1]) == foodlower]
    # print possible_files
    # A lot of this cribbed from https://github.com/danieldiekmeier/memegenerator
    # img = Image.open(args.images_dir + os.sep + random.sample(possible_files, 1)[0])
    img = Image.open(image_filename)

    # find biggest font size that works
    print img.size
    fontSize = img.size[1]/5
    font = ImageFont.truetype(IMPACT, fontSize)
    textSize = font.getsize(text[0:30])
    print textSize
    while textSize[0] > img.size[0]-20 or textSize[1] > img.size[1]/2:
        fontSize = fontSize - 1
        font = ImageFont.truetype(IMPACT, fontSize)
        textSize = font.getsize(text[0:30])
        print textSize

    textPositionX = (img.size[0]/2) - (textSize[0]/2)
    
    # We want the text to be visible when you first see it in the twitter
    # stream. That means, if the image is taller than 2:1, you have to make
    # sure to position the text within the center 2:1 rectangle.
    # ... though this doesn't even work, b/c different clients display it differently. TODO fix.
    height = img.size[1]
    width = img.size[0]
    # if height > width/2:
    #     innerBoxTop = height/2 + .5 * width/2
    #     textPositionY = innerBoxTop - textSize[1]*1.1
    # else:
    #     textPositionY = img.size[1] - textSize[1]*1.2
    textPositionY = height/2
    textPosition = (textPositionX, textPositionY)

    draw = ImageDraw.Draw(img)
    
    # draw outlines - this is kind of slow, there may be a better way
    outlineRange = fontSize/15
    for x in range(-outlineRange, outlineRange+1, 2):
        for y in range(-outlineRange, outlineRange+1, 2):
            draw.text((textPosition[0]+x, textPosition[1]+y), text, (0,0,0), font=font)

    draw.text(textPosition, text, (255,255,255), font=font)

    # half ass watermark :P TODO make this better
    watermarkFontSize = fontSize / 5
    watermarkFont = ImageFont.truetype(IMPACT, watermarkFontSize)
    draw.text((5, 5), "@DernaldTromp", fill=(200, 200, 200), font=watermarkFont)

    img.save("temp.png")
    return img

def post_tweet(image, text):
    image_io = StringIO.StringIO()
    image.save(image_io, format='JPEG')
    # If you do not seek(0), the image will be at the end of the file and unable to be read
    image_io.seek(0)
    # TODO update this to use upload_media and then a separate post instead.
    twitter.update_status_with_media(media=image_io, status='')
    # twitter.update_status_with_media(media=image_io, status='#' + text.lower().replace(' ', '_'))

def import_pronunciation_dictionary(filename):
    pronounce = defaultdict(list) # word -> list of pronunciations, each a list of phones.
    for line in open(filename):
        if line.startswith(';'):
            continue
        word = line.split('  ')[0]
        pronounce[word] = line.split('  ')[1].strip().split(' ')
    return pronounce

def add_word_breaks(text):
    words = text.split(' ')
    total_chars = 0
    for i in range(len(words)):
        total_chars += len(words[i])
        if total_chars > 22:
            words[i] = '\n' + words[i]
            total_chars = 0
    return ' '.join(words)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--images_dir', default='images')
    parser.add_argument('--pronouncing_dict_file',
        default='cmu_pronouncing_dict/cmudict-0.7b.txt')
    args = parser.parse_args()

    pronounce = import_pronunciation_dictionary(args.pronouncing_dict_file)
    # Parse food list and pronunciation dictionary
    # foods = [line.strip() for line in open(args.foods_file)]
    # not_pronounced_words = [w for w in foods if w.split()[0].upper() not in pronounce]
    # if len(not_pronounced_words) > 0:
        # print 'Warning! These words are unpronounced: ' + str(not_pronounced_words)

    while True:
        status = twitter.get_user_timeline(screen_name="realDonaldTrump")[0]
        text = status['text']
        # tweet = get trump's latest
        misspelled_text = misspell(text, pronounce)
        misspelled_text = add_word_breaks(misspelled_text)
        image = make_image(misspelled_text, 'images/trump' + str(random.randint(0, 12)) + '.jpg')
        print "Posting %s as %s" % (text, misspelled_text)
        try:
            pass
            # post_tweet(image, misspelled_text)
        except twython.exceptions.TwythonError:
            print "Error once, trying again."
            try:
                pass
                # post_tweet(image, fud)
            except:
                print "Error twice, giving up for now."
 
        # post ~ 2 / day? Average sleep 11 hrs so it'll rotate through the day.
        minutes_to_sleep = random.randint(460, 860)
        print "It is now %s, sleeping for %d hours, %d minutes" % (datetime.datetime.now(), minutes_to_sleep / 60, minutes_to_sleep % 60)
        time.sleep(minutes_to_sleep * 60)
