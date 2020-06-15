import scraper
import get_missing

def get_all():
    scraperOut = scraper.fetch_all_pages()
    finalFile = get_missing.fetch_missing_posts(scraperOut)
    print('Okay, hopefully all the confessions are in %s?' % finalFile)

if __name__ == '__main__':
    get_all()
