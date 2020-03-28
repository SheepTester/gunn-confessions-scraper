from pyquery import PyQuery
from lxml import html
import requests

print(PyQuery('https://www.facebook.com/pg/gunnconfessions/posts/').find('._3576').text())
