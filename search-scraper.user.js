// ==UserScript==
// @name         Gunn Confessions scraper
// @namespace    https://sheeptester.github.io/
// @version      1.0
// @description  When Facebook ratelimits my Python scraper but doesn't for Ovinus
// @author       SheepTester
// @match        *://www.facebook.com/page/1792991304081448/search/*
// @grant        none
// ==/UserScript==

(async function () {
    'use strict'

    const foundKey = '[gunn-confessions-scraper] found'
    const missingKey = '[gunn-confessions-scraper] missing'

    const mainSelector = '[role="main"]'
    const linkSelector = 'a[href^="https://www.facebook.com/gunnconfessions/posts/"'
    const contentSelector = '.l9j0dhe7.stjgntxs.ni8dbmo4'

    const confessionNumberRegex = /(?:^|\n)(\d+)\. /
    function getConfessionNumber (content) {
        const match = content.match(confessionNumberRegex)
        return match ? match[1] : null
    }

    const getPostIdRegex = /\/posts\/(\d+)/
    function getPostId (link) {
        const match = link.match(getPostIdRegex)
        return match ? match[1] : null
    }

    const delay = time => new Promise(resolve => setTimeout(resolve, time))

    const missing = (localStorage.getItem(missingKey) || '').split(/\r?\n/).map(Number).filter(n => n)
    if (!missing.length) {
        localStorage.setItem(missingKey, prompt('No missing confession numbers given. Care to give them now?'))
        window.location.reload()
        return
    }

    while (true) {
        if (document.querySelector(mainSelector)) break
        await delay(50)
    }

    await delay(500)

    const links = document.querySelectorAll(linkSelector)
    const newFound = Object.fromEntries(Array.from(links, link => [
        getConfessionNumber(link.querySelector(contentSelector).childNodes[1].nodeValue),
        getPostId(link.href)
    ]))
    console.log(JSON.stringify(newFound, null, 2))

    const found = JSON.parse(localStorage.getItem(foundKey)) || {}
    Object.assign(found, newFound)
    localStorage.setItem(foundKey, JSON.stringify(found))

    const params = new URL(window.location).searchParams
    let current = +params.get('q')
    if (Number.isNaN(current)) throw new Error('search bad')
    do {
        current--
    } while (current > 0 && !missing.includes(current))
    if (current > 0) {
        window.location = `?q=${current}`
    } else {
        alert('Done!')
    }
})()
