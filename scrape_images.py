#!/usr/bin/env python

# Scrapes Google Image Search I guess for images of food.
#
# Usage:
# ./scrape_images.py --food_image_urls_file=(output file for food image urls)

# https://developers.google.com/image-search/v1/jsondevguide#json_snippets_python
# If this gets rate limited, we can always do:
# http://stackoverflow.com/questions/11242967/python-search-with-image-google-images
# 

import urllib2, json, requests, argparse, csv, time, base64, os


def get_image_urls_for_food(food):
    params = {'v': 1.0, 'imgsz': 'large', 'rsz':6, 'as_filetype':'jpg', 'q': food}
    r = requests.get('https://ajax.googleapis.com/ajax/services/search/images',
            params=params)
    urls = [result['unescapedUrl'] for result in r.json()['responseData']['results']]
    return urls

# Get a filename for a food image that is located at the following URL.
def get_filename(food, url):
    url_after_http = url[10:]
    return food.replace(' ', '_') + '_' + base64.b64encode(url_after_http)[0:8] + ".jpg"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--foods_file', default='foods.txt')
    parser.add_argument('--food_image_urls_file', default='food_image_urls.txt', help="output file so we can save the urls and credit where credit's due.")
    parser.add_argument('--images_dir', default='images', help="output directory to store the images in.")
    parser.add_argument('--start_at', help='if you want to skip some foods, then enter here a name of a food that will be the first one not skipped. (for example, if this process got interrupted before.)')
    args = parser.parse_args()

    foods = [food.strip().lower() for food in open(args.foods_file)]
    food_image_urls = csv.writer(open(args.food_image_urls_file, 'w'))
    food_image_urls.writerow(['food', 'url', 'filename'])
    for food in foods:
        if args.start_at and food < args.start_at:
            continue
        print 'Getting images for: ' + food
        urls = get_image_urls_for_food(food)
        for url in urls:
            filename = get_filename(food, url)

            try:
                image_data = requests.get(url).content
            except requests.exceptions.SSLError:
                print "SSL error on %s" % url
                continue
            except requests.exceptions.ConnectionError:
                print "Connection error on %s" % url
                continue
            except requests.exceptions.TooManyRedirects:
                print "Too many redirects on %s" % url
                continue
            except:
                print "Some other error getting an image at %s" % url
                continue

            food_image_urls.writerow([food, url, filename])
            writer = open(args.images_dir + os.sep + filename, 'w')
            writer.write(image_data)
            writer.close()
        time.sleep(10)
